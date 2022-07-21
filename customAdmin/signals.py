import logging
from customUser.models import Orders, PaymentDetails
from django.db.models.signals import post_save
from django.dispatch import receiver

from customAdmin.helpers import send_email
from .models import Email_Template, Product, User

logger = logging.getLogger(__name__)


# @receiver(post_save, sender=User)
def handle_email(sender, instance, created, **kwargs):
    try:
        email = Email_Template.objects.get(code='ET05')
        if created:
            send_email(
                emails=[value.email for value in User.objects.filter(
                    is_superuser=True)],
                subject=email.subject,
                message=email.message,
                username=instance.username,
                user_email=instance.email
            )
    except Exception as e:
        logger.error(e)

# @receiver(post_save, sender=User)
# def handle_cart(sender, instance, created, **kwargs):
#     try:
#         if created:
#             if request.session.session_key:
#                         cart = []
#                         for key, value in request.session.items():
#                             if key == '_auth_user_id' or key == '_auth_user_backend' or key == '_auth_user_hash':
#                                 pass
#                             else:
#                                 cart.append({'key': int(key), 'quantity': int(value)})
#                         login(request, user)
#                         for product in cart:
#                             ProductDetails.add_product(
#                                 self, request, product['key'], product['quantity'])
#     except Exception as e:
#         logger.error(e)


# @receiver(post_save, sender=Orders)
def handle_payment(sender, instance, created, **kwargs):
    try:
        if created:
            PaymentDetails.objects.create(
                payment_status='Pending',
                order_id=instance.id,
                user_id=instance.user_id,
            )
    except Exception as e:
        logger.error(e)

# @receiver(post_save, sender=Product)


def handle_out_of_stock_status(sender, instance, created, **kwargs):
    try:
        if created:
            if instance.quantity <= 0:
                instance.out_of_stock_status = True
    except Exception as e:
        logger.error(e)


post_save.connect(handle_payment, sender=Orders)

post_save.connect(handle_email, sender=User)

post_save.connect(handle_out_of_stock_status, sender=Product)
