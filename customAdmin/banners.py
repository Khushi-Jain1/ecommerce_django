from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import request
from django.shortcuts import redirect
from django.urls.base import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from Ecommerce.settings import MEDIA_URL
from customAdmin.forms import BannerForm
from customAdmin.models import Banners

class BannerView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'
    model = Banners
    template_name = 'customAdmin/table.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['table'] = { 'columns': [ 'Title', 'Link', 'Actions' ] }
        context['tab'] = {'title': 'Banners'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def post(self, request):
        try:
            some_var = request.POST.getlist('checks[]')
            for id in some_var:
                banner = Banners.objects.get(id=int(id))
                banner.delete()
        except Exception as e:
            messages.error(request, e)
        return redirect('admin:banners')


class AddBanners(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'
    model = Banners
    form_class = BannerForm
    template_name = 'customAdmin/form.html'
    success_url = reverse_lazy('admin:banners')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Banners',
            'title': 'Add Banner'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def get_success_url(self):
        messages.success(self.request, 'New Banner Added')
        return super().get_success_url()

class EditBanners(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'
    model = Banners
    form_class = BannerForm
    template_name = 'customAdmin/form.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Banners',
            'title': 'Edit banner'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['image'] = {'media': MEDIA_URL, 'image': Banners.objects.get(id = self.kwargs['pk']).image} 
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Changes Done')
        return reverse('admin:edit_banners', kwargs={'pk': self.kwargs['pk']})
