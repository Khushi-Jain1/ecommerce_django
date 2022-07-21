from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import HttpResponseRedirect
from django.views.generic.base import TemplateView

from customAdmin.decorators import unauthenticated_admin
from .forms import LoginForm
from django.urls import reverse
from django.views import View
from django.shortcuts import redirect, render
import logging

class Unauth(TemplateView):
    template_name = 'customAdmin/403.html'

logger = logging.getLogger(__name__)

class LoginView(View):
    @unauthenticated_admin
    def get(self, request):
        context = {}
        context['form'] = LoginForm()
        return render(request, 'customAdmin/login.html', context)

    def post(self, request):
        context = {}
        form = LoginForm(request.POST)
        context['form'] = form
        try:
            if form.is_valid():
                username = form.clean_username()
                password = form.clean_password()
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_superuser:
                        login(request, user)
                        return HttpResponseRedirect(reverse('admin:dashboard'))
                    else:
                        login(request, user)
                        return redirect('admin:unauthorized')
                else:
                    context['invalid_pass'] = {'msg': 'Invalid credentials'}
                    return render(request, 'customAdmin/login.html', context)
            else:
                return render(request, 'customAdmin/login.html', context)
        except Exception as e:
            messages.error(request, e)
            logger.error(e)
            return render(request, 'customAdmin/login.html', context)




class LogoutView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url='admin:login'
    permission_required = 'user.is_superuser'

    def get(self, request):
        try:
            logout(request)
        except Exception as e:
            logger.error(e)
        return HttpResponseRedirect(reverse('admin:login'))
