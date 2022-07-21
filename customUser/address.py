from django.shortcuts import redirect
from customUser.models import AddressBook
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls.base import reverse_lazy
from django.views import View
from .forms import AddressForm


class AddressView(LoginRequiredMixin, TemplateView):
    login_url = 'user:login'
    template_name = 'customUser/addressbook.html'

    def get_context_data(self, **kwargs):
        context = super(AddressView, self).get_context_data(**kwargs)
        context['addresses'] = AddressBook.objects.filter(
            user_id=self.request.user.id, status=True)
        return context


class AddAddress(LoginRequiredMixin, CreateView):
    login_url = 'user:login'
    model = AddressBook
    form_class = AddressForm
    success_url = reverse_lazy('user:address')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddAddress, self).form_valid(form)


class EditAddress(LoginRequiredMixin, UpdateView):
    login_url = 'user:login'
    model = AddressBook
    form_class = AddressForm
    template_name = 'customUser/addressbook_form.html'
    success_url = reverse_lazy('user:address')


class DeleteAddress(LoginRequiredMixin, View):
    def get(self, request, id):
        address = AddressBook.objects.get(id=id)
        address.status = False
        address.save()
        context = {}
        context['addresses'] = AddressBook.objects.filter(
            user_id=self.request.user.id, status=True)
        return redirect('user:address')

