from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from Ecommerce.settings import MEDIA_URL
from customAdmin.forms import OrderHistoryForm
from customUser.models import AddressBook, CouponUsage, OrderHistory, OrderProductDetails, Orders, PaymentDetails
from .models import Coupons, Email_Template, User
from .helpers import send_email

class OrderView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    login_url='admin:login'
    template_name = 'customAdmin/table.html'
    permission_required = 'user.is_superuser'


    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        data = []
        for order in Orders.objects.all():
            data.append({
                'id' : order.id,
                'customer' : User.objects.get(id = order.user_id),
                'status': order.status,
                'total': order.subtotal
            })
        context['table'] = {
            'columns': ['Order ID', 'Customer', 'Active', 'Total', 'Actions'],}
        context['object_list'] = data
        context['tab'] = {'title': 'Orders'}
        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        return context

    def post(self, request):
        some_var = request.POST.getlist('checks[]')
        for id in some_var:
            attribute_group = Orders.objects.get(id=int(id))
            attribute_group.delete()
        return redirect('admin:orders')



class OrderDetailView(LoginRequiredMixin,PermissionRequiredMixin, TemplateView):
    login_url = 'admin:login'
    template_name = 'customAdmin/order_form.html'
    permission_required = 'user.is_superuser'


    def get_context_data(self, id, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        order = Orders.objects.get(id = id)
        couponDetail = {}
        if CouponUsage.objects.filter(order_id = id).exists():
            coupon = CouponUsage.objects.get(order_id = id)
            couponDetail = Coupons.objects.get(id = coupon.coupon_id)

        context['user'] = {'username': self.request.user.username,
                           'media': MEDIA_URL, 'image': self.request.user.image}
        context['tab'] = {'parent_title': 'Orders', 'title': 'View Order Detail'}
        products = []
        for product in OrderProductDetails.objects.filter(order_id = id):
            products.append({
                'name': product.product_name,
                'quantity': product.quantity,
                'price': product.price,
                'total': product.quantity * product.price,
                'media': MEDIA_URL,
                'image': product.image
            })
        context['orderDetails'] = {
            'order_id': id,
            'status': order.status,
            'cart_total': order.cart_total,
            'total': order.subtotal,
            'discount': order.discount,
            'shipping': order.shipping_amount,
            'shipping_address': AddressBook.objects.get(id = order.shipping_address_id),
            'billing_address': AddressBook.objects.get(id = order.billing_address_id),
            'user': User.objects.get(id = order.user_id),
            'coupon': couponDetail,
            'paymentDetails': PaymentDetails.objects.get(order_id = id)
        }

        context['orderHistory'] = OrderHistory.objects.filter(order_id = id)

        context['form'] = OrderHistoryForm

        context['products'] = products
        return context

    def post(self, request, id):
        form = OrderHistoryForm(request.POST or None)
        if form.is_valid():
            status = form.cleaned_data.get('status')
            OrderHistory.objects.create(
                order_id= id,
                status= status
            )
            email = Email_Template.objects.get(code = 'ET03')
            order = Orders.objects.get(id = id)
            order.status = status
            order.save()
            user = User.objects.get(id = order.user_id)
            send_email(
                email = user.email,
                subject = email.subject,
                message = email.message,
                status = order.status,
                order_id = order.id,
                order_by = user.first_name + user.last_name
            )
        return redirect('admin:order_details', id=id)

        