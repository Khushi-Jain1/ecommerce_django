from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from .forms import EmailTemplateForm, ViewMessageForm
from Ecommerce.settings import MEDIA_URL
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Email_Template, ViewMessage
from django.core.mail import EmailMultiAlternatives
import datetime
import logging

logger = logging.getLogger(__name__)


class MailView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = 'admin:login'
    template_name = 'customAdmin/table.html'
    model = ViewMessage
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['table'] = {
            'columns': ['Name', 'Subject', 'Date', 'Actions'],}
        context['object_list']= ViewMessage.objects.all()
        context['tab'] = {'title': 'Mails'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def post(self, request):
        some_var = request.POST.getlist('checks[]')
        for id in some_var:
            mail = ViewMessage.objects.get(id=int(id))
            mail.delete()
        return redirect('admin:mails')


class ViewMail(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'admin:login'
    permission_required = 'user.is_superuser'

    def get(self, request, pk):
        context = {}
        form = ViewMessageForm()
        context['form'] = form
        mail = ViewMessage.objects.get(pk=pk)
        form.fields['name'].initial = mail.name
        form.fields['mail'].initial = mail.mail
        form.fields['subject'].initial = mail.subject
        form.fields['message'].initial = mail.message
        form.fields['reply'].initial = mail.reply
        form.fields['user_logged_in'].initial = mail.user_logged_in
        if mail.reply:
            form.fields['reply'].disabled = True
        form.fields['mailed_on'].initial = mail.mailed_on
        form.fields['user_logged_in'].initial = mail.user_logged_in
        context['tab'] = {'parent_title': 'Mails', 'title': 'View Mail'}
        context['user'] = {'username': request.user.username,
                           'media': MEDIA_URL, 'image': request.user.image}
        return render(request, 'customAdmin/mail_form.html', context)

    def post(self, request, pk):
        form = ViewMessageForm(request.POST or None)
        context = {}
        context['user'] = {'username': request.user.username,
                           'media': MEDIA_URL, 'image': request.user.image}
        context['form'] = form
        context['tab'] = {'parent_title': 'Mails', 'title': 'View Mail'}
        if form.is_valid():
            reply = form.cleaned_data.get('reply')
            if reply:
                mail = ViewMessage.objects.get(pk=pk)
                name = mail.name
                subject = mail.subject
                try:
                    message = EmailMultiAlternatives(subject, reply, to=[mail.mail], from_email=settings.EMAIL_HOST_USER, reply_to=[mail.name])
                    message.send()
                except Exception as e:
                    logger.error(e)
                mail.reply = reply
                mail.replied_on = datetime.datetime.now()
                mail.save()
                messages.success(request, "Email Sent")
            else:
                messages.success(request, "Email already sent")
        return redirect('admin:view_mails', pk=pk)


######################## Email Templates ##########################


class EmailTemplate(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    login_url = 'admin:login'
    template_name = 'customAdmin/table.html'
    model = Email_Template
    permission_required = 'user.is_superuser'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['table'] = {
            'columns': ['Name', 'Code', 'Actions'],}
        context['tab'] = {'title': 'Templates'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def post(self, request):
        try:
            some_var = request.POST.getlist('checks[]')
            for id in some_var:
                attribute_group = Email_Template.objects.get(id=int(id))
                attribute_group.delete()
        except Exception as e:
            messages.error(request, e)
        return redirect('admin:email_templates')


class AddEmailTemplate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = 'admin:login'
    form_class = EmailTemplateForm
    model = Email_Template
    permission_required = 'user.is_superuser'
    success_url = reverse_lazy('admin:email_templates')
    template_name = 'customAdmin/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Templates',
                          'title': 'Add Template'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(AddEmailTemplate, self).form_valid(form)

class EditEmailTemplate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = 'admin:login'
    form_class = EmailTemplateForm
    model = Email_Template
    permission_required = 'user.is_superuser'
    success_url = reverse_lazy('admin:email_templates')
    template_name = 'customAdmin/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = {'parent_title': 'Templates',
                          'title': 'Add Template'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context