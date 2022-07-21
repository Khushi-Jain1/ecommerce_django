from django.contrib import messages
from django.db.models.aggregates import Max, Min
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import context
from django.views import View
from django.views.generic.base import TemplateView
from customAdmin.models import Product, Category, Images, Product_attribute_association, Attribute, AttributeValues, User
from customUser.forms import ReviewForm
from .models import ProductReview, ShoppingCart
from django.db.models import Count
from Ecommerce.settings import MEDIA_URL
from django.utils.text import slugify
from django.template.loader import render_to_string
# from django.http.response import HttpResponse
import json


class ProductsView(TemplateView):
    template_name = "customUser/products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = []
        products = []
        brands = Product.objects.values(
            'brand').annotate(count=Count('brand')).order_by()
        for brand in brands:
            brand.update({'slug': slugify(brand['brand'])})
        context['brands'] = brands
        for cat in Category.objects.all():
            category.append({'id': cat.id, 'name': cat.name, 'parent_category_id': cat.parent_category_id, 'slug': slugify(cat.name),
                            'childs': Category.objects.filter(parent_category_id=cat.id).exists()})
        context['category'] = category
        for product in Product.objects.all():
            if Images.objects.filter(product_id=product.id).exists():
                image = Images.objects.filter(product_id=product.id).first()
            products.append({
                'id': product.id, 'name': product.name, 'price': product.price,
                'image': image.image if Images.objects.filter(product_id=product.id).exists() else None,
                'media': MEDIA_URL,
                'image_alt': image.description if Images.objects.filter(product_id=product.id).exists() else None
            })
        context['products'] = products
        context['price'] = {
            'max': Product.objects.all().aggregate(Max('price'))['price__max'],
            'min': Product.objects.all().aggregate(Min('price'))['price__min'],
            # 'range_min': min,
            # 'range_max': max
        }
        return context

class SearchView(TemplateView):
    template_name = "customUser/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET['query']
        category = []
        products = []
        context['price'] = {
            'max': Product.objects.all().aggregate(Max('price'))['price__max'],
            'min': Product.objects.all().aggregate(Min('price'))['price__min'],
            # 'range_min': min,
            # 'range_max': max
        }
        brands = Product.objects.values(
            'brand').annotate(count=Count('brand')).order_by()
        for brand in brands:
            brand.update({'slug': slugify(brand['brand'])})
        context['brands'] = brands
        for cat in Category.objects.all():
            category.append({'id': cat.id, 'name': cat.name, 'parent_category_id': cat.parent_category_id, 'slug': slugify(cat.name),
                            'childs': Category.objects.filter(parent_category_id=cat.id).exists()})
        context['category'] = category
        for product in Product.objects.filter(name__icontains = query):
            if Images.objects.filter(product_id=product.id).exists():
                image = Images.objects.filter(product_id=product.id).first()
            products.append({
                'id': product.id, 'name': product.name, 'price': product.price,
                'image': image.image if Images.objects.filter(product_id=product.id).exists() else None,
                'media': MEDIA_URL,
                'image_alt': image.description if Images.objects.filter(product_id=product.id).exists() else None
            })
        for product in Product.objects.filter(brand__icontains = query):
            if Images.objects.filter(product_id=product.id).exists():
                image = Images.objects.filter(product_id=product.id).first()
            for p in products:
                if p['id'] != product.id:
                    products.append({
                        'id': product.id, 'name': product.name, 'price': product.price,
                        'image': image.image if Images.objects.filter(product_id=product.id).exists() else None,
                        'media': MEDIA_URL,
                        'image_alt': image.description if Images.objects.filter(product_id=product.id).exists() else None
                    })
        context['products'] = products
        return context

class FilterProductsView(TemplateView):
    def get(self, request, parent, slug):
        context = {}
        category = []
        products = []
        context['price'] = {
            'max': Product.objects.all().aggregate(Max('price'))['price__max'],
            'min': Product.objects.all().aggregate(Min('price'))['price__min'],
            # 'range_min': min,
            # 'range_max': max
        }
        brands = Product.objects.values(
            'brand').annotate(count=Count('brand')).order_by()
        for brand in brands:
            brand.update({'slug': slugify(brand['brand'])})
        context['brands'] = brands
        for cat in Category.objects.all():
            category.append({'id': cat.id, 'name': cat.name, 'parent_category_id': cat.parent_category_id, 'slug': slugify(cat.name),
                            'childs': Category.objects.filter(parent_category_id=cat.id).exists()})
        context['category'] = category
        if (parent == 'category'):
            filtered = list(filter(lambda d: d['slug'] == slug, category))
            if filtered:
                for element in filtered:
                    for product in Product.objects.filter(category_id = element['id']):
                        if Images.objects.filter(product_id=product.id).exists():
                            image = Images.objects.filter(product_id=product.id).first()
                        products.append({
                            'id': product.id, 'name': product.name, 'price': product.price,
                            'image': image.image if Images.objects.filter(product_id=product.id).exists() else None,
                            'media': MEDIA_URL,
                            'image_alt': image.description if Images.objects.filter(product_id=product.id).exists() else None
                        })
        elif(parent == 'brand'):
            filtered = list(filter(lambda d: d['slug'] == slug, brands))
            if filtered:
                for element in filtered:
                    for product in Product.objects.filter(brand = element['brand']):
                        if Images.objects.filter(product_id=product.id).exists():
                            image = Images.objects.filter(product_id=product.id).first()
                        products.append({
                            'id': product.id, 'name': product.name, 'price': product.price,
                            'image': image.image if Images.objects.filter(product_id=product.id).exists() else None,
                            'media': MEDIA_URL,
                            'image_alt': image.description if Images.objects.filter(product_id=product.id).exists() else None
                        })
        context['products'] = products
        return render(request, "customUser/products.html", context)


class ProductDetails(View):
    def get(self, request, id):
        context = {}
        context['product'] = {'productDetail': Product.objects.get(
            id=id), 'images': Images.objects.filter(product_id=id), 'media': MEDIA_URL}
        brands = Product.objects.values(
            'brand').annotate(count=Count('brand')).order_by()
        for brand in brands:
            brand.update({'slug': slugify(brand['brand'])})
        context['brands'] = brands
        category = []
        for cat in Category.objects.all():
            category.append({'id': cat.id, 'name': cat.name, 'parent_category_id': cat.parent_category_id, 'slug': slugify(cat.name),
                            'childs': Category.objects.filter(parent_category_id=cat.id).exists()})
        context['category'] = category
        attributes = []
        context['price'] = {
            'max': Product.objects.all().aggregate(Max('price'))['price__max'],
            'min': Product.objects.all().aggregate(Min('price'))['price__min'],
            # 'range_min': min,
            # 'range_max': max
        }
        for attribute in Product_attribute_association.objects.filter(product_id=id):
            attribute_text = Attribute.objects.get(id=attribute.attribute_id)
            value = attribute_text.name
            list_of_all_values = [value for elem in attributes
                                  for value in elem.values()]
            if value not in list_of_all_values:
                values = []
                for attr in Product_attribute_association.objects.filter(product_id=id).filter(attribute_id=attribute.attribute_id):
                    value = AttributeValues.objects.get(id=attr.value_id)
                    values.append(value.name)
                attributes.append(
                    {'attribute': attribute_text.name, 'value': values})
        context['attributes'] = attributes
        context['user'] = request.user
        reviews = []
        for review in ProductReview.objects.filter(product_id=id):
            reviews.append({
                'name': User.objects.get(id=review.name_id),
                'message': review.review,
                'time': review.created_on
            })

        context['reviews'] = reviews
        context['review_form'] = ReviewForm

        return render(request, 'customUser/product-details.html', context)

    def post(self, request, id):
        form = ReviewForm(request.POST or None)
        if 'add_review' in request.POST:
            if form.is_valid():
                review = form.cleaned_data.get('review')
                if not ProductReview.objects.filter(name_id=request.user.id, product_id=id).exists():
                    ProductReview.objects.create(
                        name_id=request.user.id,
                        review=review,
                        product_id=id
                    )
                else:
                    messages.info(request,"You have already added review for this product")
            else:
                messages.error(request,form.errors)
        else:
            quantity = request.POST['quantity']
            if not request.user.is_authenticated:
                if request.session.has_key(str(id)):
                    product = request.session.get(str(id))
                    total = int(quantity) + int(product)
                    request.session[str(id)] = str(total)
                else:
                    request.session[id] = quantity
                # for key, value in request.session.items():
                #     print('{} => {}'.format(key, value))
            else:
                # print('user is authenticated')
                self.add_product(request, id, quantity)
        return redirect('user:product-details', id=id)

    def add_product(self, request, id, quantity):
        if id == '_auth_user_id' or id == '_auth_user_backend' or id == '_auth_user_hash':
            pass
        else:
            if ShoppingCart.objects.filter(product_id=int(id), user_id=request.user.id).exists():
                product = ShoppingCart.objects.filter(
                    user_id=request.user.id).get(product_id=int(id))
                product.quantity = int(quantity) + product.quantity
                product.save()
            else:
                product = ShoppingCart(
                    product_id=int(id), quantity=int(quantity), user_id=request.user.id)
                product.save()

class RangeFilter(View):
    
    def get(self, request):
        products = []
        min = request.GET['min']
        max = request.GET['max']
        for product in Product.objects.filter(price__lte = max, price__gte = min):
            if Images.objects.filter(product_id=product.id).exists():
                image = Images.objects.filter(product_id=product.id).first()
            products.append({
                'id': product.id, 'name': product.name, 'price': product.price,
                'image': str(image.image) if Images.objects.filter(product_id=product.id).exists() else None,
                'media': MEDIA_URL,
                'image_alt': image.description if Images.objects.filter(product_id=product.id).exists() else None
            })
        data = render_to_string('customUser/price-range.html', {'products': products})
        return JsonResponse({'data': data})