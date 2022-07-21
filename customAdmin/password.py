import logging
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from .forms import RecoverPasswordForm, ResetPassword
from django.views import View
import uuid
from .models import Email_Template, User
from .helpers import send_email
import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

class PasswordReset(FormView):
    template_name = 'customAdmin/forgot-password.html'
    form_class = ResetPassword
    success_url = reverse_lazy('admin:reset')

    def get_success_url(self):
        messages.success(self.request, 'Email sent')
        return super().get_success_url()

    def form_valid(self, form):
        token = str(uuid.uuid4())
        user_object = User.objects.get(username=form.instance.username)
        nextTime = datetime.datetime.now() + datetime.timedelta(minutes=15)
        user_object.token_expiry = nextTime
        user_object.forget_password_token = token
        user_object.save()
        email_template = Email_Template.objects.get(code = 'ET01')
        send_email(
            email = user_object.email, 
            token = token, 
            subject = email_template.subject, 
            message = email_template.message,
            name = user_object.first_name + " " + user_object.last_name,
            url = 'admin/recover'
        )
        return super().form_valid(form)
    
class RecoverPassword(View):

    def get(self, request, token):
        context = {}
        context['form'] = RecoverPasswordForm()
        if User.objects.filter(forget_password_token=token).exists():
            profile_obj = User.objects.get(forget_password_token=token)
            if profile_obj.token_expiry > timezone.now():
                return render(request, 'customAdmin/recover-password.html', context)
            else:
                return HttpResponse("Token Expired")
        else:
            return HttpResponse("Incorrect token")

    def post(self, request, token):
        context = {}
        try:
            form = RecoverPasswordForm(request.POST or None)
            context['form'] = form
            if form.is_valid():
                password = form.cleaned_data.get('password')
                if User.objects.filter(forget_password_token=token).exists():
                    user_obj = User.objects.get(forget_password_token=token)
                    user_obj.set_password(password)
                    user_obj.forget_password_token = None
                    user_obj.save()
                    messages.success(request, "Password Changed")
                else:
                    messages.error(request, 'Invalid token')
            else:
                messages.error(request, form.errors)
        except Exception as e:
            logger.error(e)
        return render(request, 'customAdmin/recover-password.html', context)
