import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, Template
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)

def send_email(**kwargs):
    try:
        context = Context({
            "name": kwargs.get('name'), 
            "link": f'http://127.0.0.1:8000/{kwargs.get("url")}/{kwargs.get("token")}/',
            "status": kwargs.get('status'),
            "order_id": kwargs.get('order_id'),
            "order_by": kwargs.get('order_by'),
            "email": kwargs.get('email'), 
            "email": kwargs.get('user_email'),
            "username": kwargs.get('username'),
            "password": kwargs.get('password'),
            "otp": kwargs.get('otp'),
        })
        sub = Template(kwargs.get('subject'))
        subject = sub.render(context)
        msg = Template(kwargs.get('message'))
        message = msg.render(context)
        email_from = settings.EMAIL_HOST_USER
        if kwargs.get('emails'):
            recipient_list = kwargs.get('emails')
        else:
            recipient_list = [kwargs.get('email'), ]
        if kwargs.get('attachment'):
            email = EmailMessage(subject, message, email_from, recipient_list)
            email.attach('attachment', kwargs.get('attachment'), 'application/pdf')
            email.send()
        else:
            send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        logger.error(e)
    return True
