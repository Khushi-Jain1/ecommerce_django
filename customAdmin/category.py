import logging
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView
from .forms import CategoryForm
from Ecommerce.settings import MEDIA_URL
from django.shortcuts import redirect
from .models import Category
from django.utils.text import slugify
from django.contrib import messages

logger = logging.getLogger(__name__)

class CategoryView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url='admin:login'
    template_name = 'customAdmin/table.html'
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        columns = ['Name', 'Action']
        categories = []
        for category in Category.objects.all():
            categories.append(
                {'id': category.id, 'name': self.parentCategory(category)})
        context['tab'] = {'title': 'Category'}
        context['table'] = {'columns': columns}
        context['object_list'] = categories
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def parentCategory(self, obj):
        category = ''
        if obj.parent_category_id:
            cat = Category.objects.get(id=obj.parent_category_id)
            category = self.parentCategory(cat) + ' > ' + obj.name
        else:
            category = obj.name
        return category

    def post(self, request):
        some_var = request.POST.getlist('checks[]')
        try:
            for id in some_var:
                if Category.objects.filter(id=int(id)).exists():
                    category = Category.objects.get(id=int(id))
                    category.delete()                    
        except Exception as e:
            messages.error(request, e)
            logger.error(e)
        return redirect("admin:category")
       

class AddCategoryView(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url='admin:login'
    model = Category
    template_name = 'customAdmin/form.html'
    form_class = CategoryForm
    permission_required = 'user.is_superuser'
    success_url = reverse_lazy('admin:category')

    def get_context_data(self,  **kwargs):
        context = super().get_context_data( **kwargs)
        context['tab'] = {'parent_title': 'Category', 'title': 'Add category'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def get_form_kwargs(self):
        kwargs =  super(AddCategoryView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        return super(AddCategoryView, self).form_valid(form)


    
class EditCategoryView(LoginRequiredMixin,PermissionRequiredMixin, UpdateView):
    login_url='admin:login'
    model = Category
    form_class = CategoryForm
    template_name = 'customAdmin/form.html'
    permission_required = 'user.is_superuser'
    success_url = reverse_lazy('admin:category')

    def get_context_data(self,  **kwargs):
        context = super().get_context_data( **kwargs)
        context['tab'] = {'parent_title': 'Category', 'title': 'Edit category'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def get_form_kwargs(self):
        kwargs =  super(EditCategoryView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        return super(EditCategoryView, self).form_valid(form)