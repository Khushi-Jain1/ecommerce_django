from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from Ecommerce.settings import MEDIA_URL
from customAdmin.forms import CustomerForm

from customAdmin.models import User

class CustomerView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url='admin:login'
    template_name = "customAdmin/table.html"
    permission_required = 'user.is_superuser'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = {'columns': ['Username', 'Email', 'Status', 'Date Added', 'Actions'],}
        context['object_list'] = User.objects.filter(is_superuser = False)
        context['tab'] = {'title': 'Customers'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

class CustomerDetails(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'admin:login'
    model = User
    form_class = CustomerForm
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Customers', 'title': 'View Customer'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['image'] = {'media': MEDIA_URL, 'image': User.objects.get(id = self.kwargs['pk']).image} 
        return context