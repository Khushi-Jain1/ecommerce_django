
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls.base import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView
from Ecommerce.settings import MEDIA_URL
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from customAdmin.forms import CMSForm

# from customAdmin.forms import CMSForm


class CMSView(LoginRequiredMixin, PermissionRequiredMixin,  TemplateView):
    login_url = 'user:login'
    template_name = 'customAdmin/table.html'
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context = super(CMSView, self).get_context_data(**kwargs)
        context['table'] = {'columns': ['URL', 'Title', 'Actions'],}
        context['object_list']= FlatPage.objects.all()
        context['tab'] = {'title': 'CMS'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context
    
    def post(self, request):
        some_var = request.POST.getlist('checks[]')
        for id in some_var:
            if FlatPage.objects.filter(id=int(id)).exists():
                cms = FlatPage.objects.get(id=int(id))
                cms.delete()
        return redirect('admin:cms')


class AddCMS(LoginRequiredMixin,PermissionRequiredMixin, CreateView):
    login_url = 'user:login'
    model = FlatPage
    form_class = CMSForm
    template_name = 'customAdmin/form.html'
    success_url = reverse_lazy('admin:cms')
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'CMS',
                          'title': 'Add CMS'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def form_valid(self, form):
        form.save()
        form.instance.template_name = 'cms.html'
        form.instance.sites.add(Site.objects.get(pk=1))
        return super(AddCMS, self).form_valid(form)


class EditCMS(LoginRequiredMixin,PermissionRequiredMixin , UpdateView):
    login_url = 'admin:login'
    model = FlatPage
    form_class = CMSForm
    template_name = 'customAdmin/form.html'
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'CMS',
                          'title': 'Edit CMS'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def get_success_url(self):
        return reverse('admin:edit_cms', kwargs={'pk': self.kwargs['pk']})

