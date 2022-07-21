import logging
from django.forms.models import modelformset_factory
from django.http import response
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.urls.base import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from Ecommerce.settings import MEDIA_URL
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import ProductAttributes, ProductForm
from django.views import View
from .models import Attribute, AttributeValues, Images, Product, Product_attribute_association
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.views.generic import ListView
import json

logger = logging.getLogger(__name__)


class ProductView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = 'admin:login'
    model = Product
    template_name = 'customAdmin/table.html'
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = {
            'columns': ['Products', 'Actions'], }
        context['tab'] = {'title': 'Products'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def post(self, request):
        try:
            some_var = request.POST.getlist('checks[]')
            for id in some_var:
                product = Product.objects.get(id=int(id))
                product.delete()
        except Exception as e:
            messages.error(request, e)
        return redirect("admin:products")


class AddProduct(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'
    form_class = ProductForm
    template_name = 'customAdmin/product_form.html'
    success_url = reverse_lazy('admin:products')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attribute_form = modelformset_factory(
            Product_attribute_association, form=ProductAttributes, extra=1)
        formset = attribute_form(
            queryset=Product_attribute_association.objects.filter(product_id=0))
        context['attribute_form'] = formset
        context['tab'] = {'parent_title': 'Products',
                          'parent-url': 'admin:products',  'title': 'Add Product'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def create_product(self, form):
        name = form.cleaned_data.get('name')
        description = form.cleaned_data.get('description')
        status = form.cleaned_data.get('status')
        category = form.cleaned_data.get('category')
        quantity = form.cleaned_data.get('quantity')
        out_of_stock_status = form.cleaned_data.get('out_of_stock_status')
        shipping_required = form.cleaned_data.get('shipping_required')
        price = form.cleaned_data.get('price')
        brand = form.cleaned_data.get('brand')
        new_entry = Product(
            name=name,
            description=description,
            status=status,
            created_on=datetime.datetime.now(),
            created_by_id=self.request.user.id,
            category=category,
            quantity=quantity,
            out_of_stock_status=out_of_stock_status,
            shipping_required=shipping_required,
            price=price,
            brand=brand
        )
        new_entry.save()
        return new_entry.id

    def post(self, request):
        context = {}
        form = ProductForm(request.POST, request.FILES, id=0)
        formset = modelformset_factory(
            Product_attribute_association, form=ProductAttributes, exclude=('product',))
        formset_attr = formset(request.POST)
        context['tab'] = {'parent_title': 'Products', 'title': 'Add Product'}
        context['user'] = {'username': request.user.username,
                           'media': MEDIA_URL, 'image': request.user.image}
        if form.is_valid():
            id = self.create_product(form)
            product = Product.objects.get(id=id)
            for img in request.FILES.getlist('images'):
                new_image = Images(description=product.name, image=img,
                                   product=Product.objects.get(id=id))
                new_image.save()
            img = Images.objects.filter(
                product=Product.objects.get(id=id))
            context['images'] = img
            for attr_form in formset_attr:
                if attr_form.is_valid():
                    attribute = attr_form.cleaned_data.get('attribute')
                    attribute_text = attr_form.cleaned_data.get('value')
                    if attribute and attribute_text:
                        if not Product_attribute_association.objects.filter(product_id=id, attribute=attribute, value=attribute_text).exists():
                            if attr_form.cleaned_data.get('id'):
                                print('edit')
                                # edit
                                attribute_obj = attr_form.cleaned_data.get(
                                    'id')
                                attr_obj = Product_attribute_association.objects.get(
                                    id=attribute_obj.id)
                                attr_obj.attribute = attribute
                                attr_obj.value = attribute_text
                                attr_obj.save()
                            else:
                                print('add', attribute)
                                Product_attribute_association.objects.create(
                                    attribute=attribute,
                                    value=attribute_text,
                                    product_id=id
                                )
            context['form'] = form
            attr_formset = formset(
                queryset=Product_attribute_association.objects.filter(product_id=id))
            context['attribute_form'] = attr_formset
            messages.success(request, "Product added")
            return redirect('admin:edit_product', pk=id)
        else:
            context['attribute_form'] = formset
            context['form'] = form
        return render(request, 'customAdmin/product_form.html', context)


class EditProduct(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('admin:products')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        img = Images.objects.filter(product_id=self.kwargs['pk'])
        context['images'] = img
        attribute_form = modelformset_factory(
            Product_attribute_association, form=ProductAttributes,extra=1)
        formset = attribute_form(queryset=Product_attribute_association.objects.filter(product_id=self.kwargs['pk']), )
        context['attribute_form']  = formset
        context['tab'] = {'parent_title': 'Products', 'title': 'Edit Product'}
        return context

    def post(self, request, pk):
        context = {}
        form = ProductForm(request.POST, request.FILES, id=pk)
        formset = modelformset_factory(
            Product_attribute_association, exclude=('product',))
        formset_attr = formset(request.POST)
        context['form'] = form
        #     'product_form': form,
        #     'attribute_form': formset_attr}
        context['tab'] = {'parent_title': 'Products', 'title': 'Add Product'}
        context['user'] = {'username': request.user.username,
                           'media': MEDIA_URL, 'image': request.user.image}
        if form.is_valid():
            product = Product.objects.get(pk=pk)
            product.name = form.cleaned_data.get('name')
            product.description = form.cleaned_data.get('description')
            product.status = form.cleaned_data.get('status')
            product.category = form.cleaned_data.get('category')
            product.quantity = form.cleaned_data.get('quantity')
            product.out_of_stock_status = form.cleaned_data.get(
                'out_of_stock_status')
            product.brand = form.cleaned_data.get('brand')
            product.shipping_required = form.cleaned_data.get(
                'shipping_required')
            product.modified_on = datetime.datetime.now()
            product.price = form.cleaned_data.get('price')
            product.save()
            for img in request.FILES.getlist('images'):
                new_image = Images(description=form.cleaned_data.get(
                    'name'), image=img, product=Product.objects.get(pk=pk))
                new_image.save()
            img = Images.objects.filter(product=pk)
            context['images'] = img
            # import pdb;pdb.set_trace();
            # if formset_attr.is_valid():
                # Valid
            for attr_form in formset_attr:
                if attr_form.is_valid():
                    attribute = attr_form.cleaned_data.get('attribute')
                    attribute_text = attr_form.cleaned_data.get('value')
                    # import pdb; pdb.set_trace()
                    # attribute_text = attr_form.clean_value()
                    if attribute and attribute_text:
                        # if attr_form.cleaned_data.get('DELETE'):
                        #     print('delete')
                        #     # delete
                        #     get_attr = Product_attribute_association.objects.filter(product_id=pk).filter(attribute=Attribute.objects.get(
                        #         name=attribute)).get(value=AttributeValues.objects.get(name=attribute_text))
                        #     get_attr.delete()
                        # elif attr_form.cleaned_data.get('DELETE') == False:
                        if not Product_attribute_association.objects.filter(product_id=pk,attribute=attribute,value=attribute_text).exists():
                            if attr_form.cleaned_data.get('id'):
                                # print('edit')
                                # edit
                                attribute_obj = attr_form.cleaned_data.get('id')
                                attr_obj = Product_attribute_association.objects.get(
                                    id=attribute_obj.id)
                                attr_obj.attribute = attribute
                                attr_obj.value = attribute_text
                                attr_obj.save()
                            else:
                                # print('add', attribute)
                                Product_attribute_association.objects.create(
                                    attribute = attribute,
                                    value = attribute_text,
                                    product_id = pk
                                )
                                # attr = Product_attribute_association(
                                #     attribute=Attribute.objects.get(
                                #         name=attribute),
                                #     value=AttributeValues.objects.get(
                                #         name=attribute_text),
                                #     product=Product.objects.get(pk=pk))
                                # attr.save()
                # else:
                #     print(attr_form.errors)
            # else:
            #     logger.error('errors', formset.errors)
            #     for form in formset_attr:
            #         logger.error(form.errors)
            #         messages.error(request, form.errors)
            # attribute_formset = modelformset_factory(Product_attribute_association, extra=1, exclude=('product',))
            # attribute_formset = modelformset_factory(
            #     Product_attribute_association, form=ProductAttributes, can_delete=True)
            attribute_formset = modelformset_factory(
                Product_attribute_association, form=ProductAttributes)
            # context['form'] =  form,
            context['attribute_form'] = attribute_formset(
                    queryset=Product_attribute_association.objects.filter(product_id=product.id))
            messages.success(request, "Product editted")
            return render(request, 'customAdmin/product_form.html', context)
        else:
            context['attribute_form'] = formset_attr
            return render(request, 'customAdmin/product_form.html', context)


class DeleteImage(LoginRequiredMixin, PermissionRequiredMixin,  View):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'

    def get(self, request, pk, id):
        # product = Images.objects.get(pk=id)
        try:
            image = Images.objects.get(id=id)
            image.delete()
        except Exception as e:
            logger.error(e)
        return redirect('admin:edit_product', pk=pk)


class AttributeValueChange(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'

    def get(self, request):
        data = request.GET['post_id']
        result_set = [{'key': None, 'value': "---------"}]
        choices = AttributeValues.objects.filter(attribute_id=data)
        for attribute in choices:
            result_set.append({'key': attribute.id, 'value': attribute.name})
        result = json.dumps(result_set)
        return HttpResponse(result)


class DeleteAtrribute(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'

    def get(self, request):
        pk = request.GET['value']
        attribute = Product_attribute_association.objects.get(pk=pk)
        product = attribute.product_id
        attribute.delete()
        attribute_formset = modelformset_factory(
            Product_attribute_association, form=ProductAttributes)
        # attribute_formset = modelformset_factory(
        #         Product_attribute_association, form=ProductAttributes, can_delete=True)
        # context['form'] =  form,
        products = attribute_formset(
            queryset=Product_attribute_association.objects.filter(product_id=product))
        data = render_to_string(
            'attribute_value.html', {'attribute_form': products})
        return JsonResponse({'data': data})
