import logging
from customAdmin.models import Email_Template, Product, User
from django_cron import CronJobBase, Schedule
from .models import WishList
from customAdmin.helpers import send_email
from customUser.views import render_to_pdf

class MailWishlist(CronJobBase):
    RUN_EVERY_MINS=1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code='customAdmin.MailWishlist'

    def do(self):
        # mail code willbe here
        try:
            wishlist = []
            for product in WishList.objects.order_by().values('product_id').distinct():
                wishlist.append({'product': Product.objects.get(id = product['product_id'])})          
    # for product in order_list:
    #     products.append({
    #         'product_name': product.product_name,
    #         'quantity': product.quantity,
    #         'price': product.price,
    #         'total': product.price * product.quantity
    #     })
            attachment = render_to_pdf(
                'customUser/mailWishlist.html',
                {
                    'pagesize': 'A4',
                    'products': wishlist
                }
            )
            email_template = Email_Template.objects.get(code='ET06')
            # print(attachment)
            send_email(
                emails=[value.email for value in User.objects.filter(is_superuser = True)],
                attachment=attachment,
                subject=email_template.subject,
                message=email_template.message,
            )
        except Exception as e:
            logging.error(e)