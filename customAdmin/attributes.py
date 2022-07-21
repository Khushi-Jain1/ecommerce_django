from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from customAdmin.models import AttributeValues, Attribute
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import AttributeForm, AttributeGroupForm
from Ecommerce.settings import MEDIA_URL
from django.shortcuts import redirect


class AttributeGroup(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url='admin:login'
    template_name = 'customAdmin/table.html'
    permission_required = 'user.is_superuser'



    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context = {}
        columns = ['Attribute Group Name', 'Action']
        context['tab'] = {'title': 'Attribute Groups'}
        context['table'] = {'columns': columns,}
        context['object_list']= Attribute.objects.all()
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context
    
    def post(self, request):
        some_var = request.POST.getlist('checks[]')
        for id in some_var:
            attribute_group = Attribute.objects.get(id=int(id))
            attribute_group.delete()
        return redirect('admin:attribute_group')


class AddAttributeGroup(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url='admin:login'
    permission_required = 'user.is_superuser'
    model = Attribute
    form_class = AttributeGroupForm
    template_name = 'customAdmin/form.html'
    success_url = reverse_lazy('admin:attribute_group')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Attribute Group',
            'title': 'Add attribute group'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

class EditAttributeGroup(LoginRequiredMixin,PermissionRequiredMixin, UpdateView):
    login_url='admin:login'
    permission_required = 'user.is_superuser'
    model = Attribute
    form_class = AttributeGroupForm
    template_name='customAdmin/form.html'
    success_url = reverse_lazy('admin:attribute_group')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Attribute Group',
            'title': 'Add attribute group'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context   

# ###################   Attribute name ##################


class AttributeValue(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url='admin:login'
    template_name = 'customAdmin/table.html'
    permission_required = 'user.is_superuser'


    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        columns = ['Attribute Name', 'Attribute Group Name', 'Action']
        context['tab'] = {'title': 'Attribute'}
        context['table'] = {'columns': columns,}
        context['object_list'] = AttributeValues.objects.all()
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def post(self, request):
        some_var = request.POST.getlist('checks[]')
        for id in some_var:
            attribute = AttributeValues.objects.get(id=int(id))
            attribute.delete()
        return redirect('admin:attribute')


class AddAttribute(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url='admin:login'
    permission_required = 'user.is_superuser'
    model = AttributeValues
    form_class = AttributeForm
    template_name = 'customAdmin/form.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Attribute',
            'title': 'Add attribute'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context


class EditAttribute(LoginRequiredMixin, UpdateView):
    login_url='admin:login'
    permission_required = 'user.is_superuser'
    model = AttributeValues
    form_class = AttributeForm
    template_name='customAdmin/form.html'
    success_url = reverse_lazy('admin:attribute')


    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['tab'] = {'parent_title': 'Attribute',
            'title': 'Edit attribute'}
        return context
