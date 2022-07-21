import logging
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from customAdmin.models import Coupons
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from Ecommerce.settings import MEDIA_URL
from .forms import CouponsForm
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class CouponsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url='admin:login'
    permission_required = 'user.is_superuser'
    model = Coupons
    template_name = 'customAdmin/table.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = {'columns': ['Coupon Name', 'Code', 'Discount', 'Date Start', 'Date End', 'Active', 'Actions'],}
        # context['object_list'] =  Coupons.objects.all()
        context['tab'] = {'title': 'Coupons'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def post(self, request):
        try:
            some_var = request.POST.getlist('checks[]')
            for id in some_var:
                category = Coupons.objects.get(id=id)
                category.delete()
        except Exception as e:
            messages.error(request,e)
            logger.error(e)
        return redirect('admin:coupons')


class AddCouponsView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url='admin:login'
    model = Coupons
    form_class = CouponsForm
    template_name = 'customAdmin/form.html'
    permission_required = 'user.is_superuser'
    success_url = reverse_lazy('admin:coupons')

    def get_success_url(self):
        messages.success(self.request, 'New Coupon Added')
        return super().get_success_url()


    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(AddCouponsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Coupons', 'title': 'Add coupons'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

class EditCoupons(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url='admin:login'
    model = Coupons
    form_class = CouponsForm
    template_name = 'customAdmin/form.html'
    permission_required = 'user.is_superuser'
    success_url = reverse_lazy('admin:coupons')

    def get_success_url(self):
        messages.success(self.request, 'Changes done')
        return super().get_success_url()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Coupons', 'title': 'Add coupons'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context