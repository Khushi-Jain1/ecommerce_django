import logging
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView
from customUser.models import Orders
from Ecommerce.settings import MEDIA_URL
from django.contrib import messages
from django.shortcuts import render
from .forms import ChangePasswordForm, ProfileForm
from django.views import View
from .models import Product, User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


logger = logging.getLogger(__name__)

# Create your views here.

class Dashboard(LoginRequiredMixin, PermissionRequiredMixin,  View):
    login_url='admin:login'
    permission_required = 'user.is_superuser'
    
    
    def get(self, request):
        context = {}
        context['orders'] = Orders.objects.all().count()
        context['users'] = User.objects.filter(is_superuser = False).count()
        context['products'] = Product.objects.all().count()
        context['user'] = {'username': request.user.username,
                           'media': MEDIA_URL, 'image': request.user.image}
        return render(request, 'customAdmin/index.html', context)


class ChangePassword(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'user.is_superuser'
    # form_class = ChangePasswordForm
    template_name = 'customAdmin/change-password.html'
    success_url = reverse_lazy('admin:change')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ChangePasswordForm
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context
        
    def post(self, request):
        context = {}
        try:
            form = ChangePasswordForm(request.POST)
            context['form'] = form
            context['user'] = {'username': request.user.username,
                            'media': MEDIA_URL, 'image': request.user.image}
            if form.is_valid():
                old_password = form.cleaned_data.get('oldPassword')
                password = form.cleaned_data.get('password')
                user = request.user
                if User.objects.filter(username=user.username).exists():
                    user_obj = User.objects.get(username=user.username)
                    if user.check_password(old_password):
                        user_obj.set_password(password)
                        user_obj.save()
                        messages.success(request, "Password Changed")
                    else:
                        messages.error(request,"wrong old password")
                else:
                    messages.error(request, 'Invalid username')
            else:
                logger.error(form.errors)
        except Exception as e:
            logger.error(e)
        return render(request, 'customAdmin/change-password.html', context)


class ProfileView(LoginRequiredMixin,PermissionRequiredMixin, TemplateView):
    login_url='admin:login'
    permission_required = 'user.is_superuser'
    template_name = 'customAdmin/profile.html'
        
    def get(self, request):
        context = {}
        form = ProfileForm()
        user_obj = User.objects.get(username=request.user)
        form.fields['first_name'].initial = user_obj.first_name
        form.fields['username'].initial = user_obj.username
        form.fields['last_name'].initial = user_obj.last_name
        form.fields['email'].initial = user_obj.email
        form.fields['mobile_number'].initial = user_obj.mobile_number
        context['form'] = form
        context['user'] = {'username': request.user.username,
                           'media': MEDIA_URL, 'image': request.user.image}
        return render(request, 'customAdmin/profile.html', context)

    def post(self, request):
        context = {}
        try:
            form = ProfileForm(request.POST, request.FILES, user=request.user)
            context['form'] = form
            if form.is_valid():
                user_object = User.objects.get(username=request.user)
                user_object.username = form.clean_username()
                user_object.first_name = form.cleaned_data.get('first_name')
                user_object.last_name = form.cleaned_data.get('last_name')
                user_object.email = form.cleaned_data.get('email')
                user_object.mobile_number = form.cleaned_data.get('mobile_number')
                if form.cleaned_data.get('image'):
                    user_object.image = form.cleaned_data.get('image')
                user_object.save()
                messages.success(request, 'Profile Updated')
                context['user'] = {'username': user_object.username,
                                'media': MEDIA_URL, 'image': user_object.image}
            else:
                messages.error(request, form.errors)
                context['user'] = {'username': request.user.username,
                                'media': MEDIA_URL, 'image': request.user.image}
        except Exception as e:
            logger.error(e)
        return render(request, 'customAdmin/profile.html', context)


