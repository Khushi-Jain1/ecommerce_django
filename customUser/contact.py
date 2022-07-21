import logging
from django.contrib import messages
from django.http import request
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from customAdmin.models import ViewMessage
from customUser.forms import ContactForm
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from Ecommerce.settings import MAILCHIMP_API_KEY, MAILCHIMP_DATA_CENTER, MAILCHIMP_EMAIL_LIST_ID

logger = logging.getLogger(__name__)

class Contact(CreateView):
    model = ViewMessage
    form_class = ContactForm
    success_url = reverse_lazy('user:contact_us')

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user_logged_in = True
        else:
            form.instance.user_logged_in = False
        messages.success(self.request, 'Message Sent')
        return super(Contact, self).form_valid(form)


class NewsletterView(LoginRequiredMixin, View):
    login_url = 'user:login'

    def get(self, request):
        # print('email', request.user.email)
        email = request.user.email
        mailchimp = Client()
        mailchimp.set_config({
            'api_key': MAILCHIMP_API_KEY,
            'server': MAILCHIMP_DATA_CENTER,
        })
        member_info = {
            "email_address": email,
            # 'first_name': request.user.first_name,
            # 'last_name': request.user.last_name,
            # 'phone_number': request.user.mobile_number,
            "status": "subscribed",
        }
        try:
            response = mailchimp.lists.add_list_member(MAILCHIMP_EMAIL_LIST_ID, member_info)
            # print("response: {}".format(response))
            messages.success(request, "Email received. thank You! ")
        except ApiClientError as error:
            logger.error("An exception occurred: {}".format(error.text))
        return redirect('user:contact_us')
