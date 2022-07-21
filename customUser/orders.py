import logging
from django.contrib import messages
from django.http import request
from django.shortcuts import render
from customUser.forms import TrackOrderForm
from django import template
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.forms import Form
from django.views.generic.edit import CreateView, FormView
from Ecommerce.settings import MEDIA_URL
from customAdmin.models import Coupons
from customUser.models import AddressBook, CouponUsage, OrderHistory, OrderProductDetails, Orders, PaymentDetails
from django.views.generic import TemplateView
from django.views import View


class MyOrders(TemplateView):
    template_name = 'customUser/my_orders.html'

    def get_context_data(self):
        context = {}
        orders = []
        for order in Orders.objects.filter(user_id=self.request.user.id).order_by('id'):
            products = []
            # print(self.request.user.id)
            print(order.id)
            payment = PaymentDetails.objects.get(order_id=order.id)
            product_list = OrderProductDetails.objects.filter(order_id=order.id)
            for product in product_list:
                products.append({
                    'name': product.product_name,
                    'image': product.image,
                    'quantity': product.quantity,
                    'price': product.price,
                    'subtotal': product.price * product.quantity,
                })
            orders.append({
                'media': MEDIA_URL,
                'order_id': order.id,
                'order_on': order.order_date,
                'status': order.status,
                'subtotal': order.subtotal,
                'cart_total': order.cart_total,
                'shipping': order.shipping_amount,
                'discount': order.discount,
                'payment_mode': payment.payment_mode,
                'transaction_id': payment.transaction_id,
                'payment_status': payment.payment_status,
                'account_holder': payment.name,
                'products': products,
            })
            if order.shipping_address == order.billing_address:
                orders[-1].update({
                    'address': AddressBook.objects.get(id=order.shipping_address_id),
                })
            else:
                orders[-1].update({
                    'shipping_address': AddressBook.objects.get(id=order.shipping_address_id),
                    'billing_address':  AddressBook.objects.get(id=order.billing_address_id),
                })
            if CouponUsage.objects.filter(order_id=order.id).exists():
                coupon_obj = CouponUsage.objects.get(order_id=order.id)
                coupon = Coupons.objects.get(id=coupon_obj.coupon_id)
                orders[-1].update({
                    'coupon': coupon.name,
                    'code': coupon.code,
                })
        context['orders'] = orders
        return context


class TrackOrder(LoginRequiredMixin, FormView):
    template_name = 'customUser/trackOrder.html'
    login_url = 'user:login'
    form_class = TrackOrderForm

    def post(self, request):
        try:
            context = {}
            form = TrackOrderForm(request.POST or None)
            context['form'] = form
            orderHistory = []
            if form.is_valid():
                order = form.cleaned_data.get('order_id')
                if Orders.objects.filter(id=order, user_id=request.user.id).exists():
                    for row in OrderHistory.objects.filter(order_id=order):
                        orderHistory.append(
                            {'status': row.status, 'date': row.created_on})
                    context['orderHistory'] = orderHistory
                else:
                    messages.error(request, 'Invalid Order id')
            return render(request, 'customUser/trackOrder.html', context)
        except Exception as e:
            logging.error(e)
