import logging
from customUser.decorators import unauthenticated_user
from customUser.models import AddressBook, CouponUsage, OrderHistory, OrderProductDetails, Orders, PaymentDetails, ShoppingCart
from customAdmin.forms import ChangePasswordForm, RecoverPasswordForm, ResetPassword
from customAdmin.helpers import send_email
import datetime
from django.urls.base import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from .forms import CouponForm, PaymentForm, ProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseRedirect
from customUser.forms import LoginForm, RegisterForm
from django.views import View
from django.shortcuts import redirect, render
from customAdmin.models import Coupons, Email_Template, Images, Product, User
from Ecommerce.settings import MEDIA_URL
from django.views.generic import TemplateView
from django.contrib import messages
from django.urls import reverse
import uuid
from django.utils import timezone
from django.views.decorators.cache import cache_control
import io as StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from .products import ProductDetails

# Create your views here.

logger = logging.getLogger(__name__)

class Login(TemplateView):
    template_name = 'customUser/login.html'

    @unauthenticated_user
    def get(self, request):
        context = {}
        context['tab'] = 'login'
        context['form'] = {'login': LoginForm, 'register': RegisterForm}
        return render(request, 'customUser/login.html', context)

    def post(self, request):
        context = {}
        if request.POST.get('form_type') == 'login':
            login_form = LoginForm(request.POST)
            register_form = RegisterForm()
            context['form'] = {'login': login_form, 'register': register_form}
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                # msg = self.login_user(username, password)
                # context['invalid_pass'] = {'msg': msg}
                user = authenticate(
                    request, username=username, password=password)
                if user is not None:
                    if request.session.session_key:
                        cart = []
                        for key, value in request.session.items():
                            if key == '_auth_user_id' or key == '_auth_user_backend' or key == '_auth_user_hash':
                                pass
                            else: 
                                cart.append({'key': int(key), 'quantity': int(value)})
                        login(request, user)
                        for product in cart:
                            ProductDetails.add_product(
                                self, request, product['key'], product['quantity'])
                    else:
                        login(request, user)
                else:
                    context['invalid_pass'] = {'msg': 'Invalid credentials'}
                    return render(request, 'customUser/login.html', context)
            else:
                return render(request, 'customUser/login.html', context)
        else:
            login_form = LoginForm()
            register_form = RegisterForm(request.POST)
            context['form'] = {'login': login_form, 'register': register_form}
            if register_form.is_valid():
                username = register_form.cleaned_data.get('username')
                email = register_form.cleaned_data.get('email')
                password = register_form.cleaned_data.get('password')
                user = User.objects.create(username=username, email=email, is_superuser=False)
                user.set_password(password)
                user.save()
                messages.success(request, "User Created.")
                email_user = Email_Template.objects.get(code = 'ET04')
                send_email(
                    email = email,
                    username = username,
                    password = password,
                    subject = email_user.subject,
                    message = email_user.message,
                )
                if request.session.session_key:
                    for key, value in request.session.items():
                        ProductDetails.add_product(self, request, key, value)
            else:
                return render(request, 'customUser/login.html', context)
        return redirect('user:login')

class ProfileView(LoginRequiredMixin, UpdateView):
    login_url = 'user:login'
    model = User
    form_class = ProfileForm
    template_name = 'customUser/profile.html'

    def get_success_url(self):
        return reverse('user:profile', kwargs={'pk': self.object.pk})

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(id=self.object.pk)
        context['image'] = {'media': MEDIA_URL, 'image': user.image}
        return context


class LogoutView(LoginRequiredMixin, View):
    login_url = 'user:login'

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('user:home'))


class PasswordReset(View):
    def get(self, request):
        context = {}
        context['form'] = ResetPassword
        return render(request, 'customUser/forgetPassword.html', context)

    def post(self, request):
        context = {}
        form = ResetPassword(request.POST or None)
        context['form'] = form
        token = str(uuid.uuid4())
        if form.is_valid():
            user = form.cleaned_data.get('username')
            user_object = User.objects.get(username=user)
            nextTime = datetime.datetime.now() + datetime.timedelta(minutes=15)
            user_object.token_expiry = nextTime
            user_object.forget_password_token = token
            user_object.save()
            email_template = Email_Template.objects.get(code='ET01')
            send_email(
                email=user_object.email,
                token=token,
                subject=email_template.subject,
                message=email_template.message,
                name=user_object.first_name + " " + user_object.last_name,
                url='recover-password'
            )
            messages.success(request, 'Email sent')
        return render(request, 'customUser/forgetPassword.html', context)


class RecoverPassword(View):
    def get(self, request, token):
        context = {}
        context['form'] = RecoverPasswordForm()
        if User.objects.filter(forget_password_token=token).exists():
            profile_obj = User.objects.get(forget_password_token=token)
            if profile_obj.token_expiry > timezone.now():
                return render(request, 'customUser/forgetPassword.html', context)
            else:
                return HttpResponse("Token Expired")
        else:
            return HttpResponse("Incorrect token")

    def post(self, request, token):
        context = {}
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
        return render(request, 'customUser/forgetPassword.html', context)


class ChangePassword(LoginRequiredMixin, View):
    login_url = 'user:login'

    def get(self, request):
        context = {}
        form = ChangePasswordForm()
        context['form'] = form
        # context['user'] = {'username': request.user.username,
        #                    'media': MEDIA_URL, 'image': request.user.image}
        return render(request, 'customUser/forgetPassword.html', context)

    def post(self, request):
        context = {}
        form = ChangePasswordForm(request.POST)
        context['form'] = form
        # context['user'] = {'username': request.user.username,
        #                    'media': MEDIA_URL, 'image': request.user.image}
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
                messages.error(request, form.errors)
        return render(request, 'customUser/forgetPassword.html', context)


class CartView(TemplateView):
    template_name = 'customUser/cart.html'

    def get_context_data(self):
        context = {}
        products = []
        cart = []
        cart_total = 0

        if self.request.user.is_authenticated:
            for item in ShoppingCart.objects.filter(user_id=self.request.user.id):
                cart.append({'product_id': item.product_id, 'id': item.id,
                            'quantity': item.quantity})
        else:
            if self.request.session.session_key:
                for key, value in self.request.session.items():
                    cart.append(
                        {'product_id': key, 'quantity': value, 'id': key})

        for product in cart:
            item = Product.objects.get(id=product['product_id'])
            products.append({
                'name': item.name,
                'product_id': item.id,
                'cart_id': product['id'],
                'image': Images.objects.filter(product_id=item.id).first(),
                'media': MEDIA_URL,
                'price': item.price,
                'quantity': product['quantity'],
                'total': (item.price * int(product['quantity']))
            })
            cart_total = cart_total + (item.price * int(product['quantity']))
            if cart_total >= 500 or cart_total == 0:
                shipping = 0
            else:
                shipping = 50

        context['products'] = products
        if products:
            context['subtotal'] = {
                'cart_total': cart_total, 'shipping': shipping, 'total': cart_total + shipping}
        return context


class DeleteCartProduct(DeleteView):
    model = ShoppingCart
    success_url = reverse_lazy('user:cart')

    def delete(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().delete(request, *args, **kwargs)
        else:
            del request.session[kwargs['pk']]
            return redirect('user:cart')


class ChangeProductQuantity(View):
    def get(self, request):
        id = request.GET['product_id']
        task = request.GET['task']
        if request.user.is_authenticated:
            product = ShoppingCart.objects.filter(
                user_id=request.user.id).get(product_id=id)
            if task == 'increment':
                if product.quantity < 10:
                    product.quantity = product.quantity + 1
                    product.save()
            else:
                if product.quantity > 1:
                    product.quantity = product.quantity - 1
                    product.save()
                else:
                    product.delete()
        else:
            quantity = request.session.get(str(id))
            if task == 'increment':
                request.session[str(id)] = str(int(quantity) + 1)
            else:
                if int(quantity) > 1:
                    request.session[str(id)] = str(int(quantity) - 1)
                else:
                    del request.session[str(id)]
            # for key, value in request.session.items():
            #     print('{} => {}'.format(key, value))
        return HttpResponse('done')


class CheckoutView(LoginRequiredMixin, TemplateView):
    login_url = 'user:login'
    template_name = 'customUser/checkout.html'

    def get_products(self):
        cart_total = 0
        products = []
        for product in ShoppingCart.objects.filter(user_id=self.request.user.id):
            item = Product.objects.get(id=product.product_id)
            products.append({
                'name': item.name,
                'product_id': item.id,
                'cart_id': product.id,
                'image': Images.objects.filter(product_id=item.id).first(),
                'media': MEDIA_URL,
                'price': item.price,
                'quantity': product.quantity,
                'total': (item.price * int(product.quantity)),
                'error': 'only '+ str(item.quantity) + ' in stock' if product.quantity > item.quantity else None
            })
            cart_total = cart_total + (item.price * int(product.quantity))
        if cart_total >= 500 or cart_total == 0:
            shipping = 0
        else:
            shipping = 50
        self.request.session['cart_total'] = cart_total
        self.request.session['shipping'] = shipping
        return {
            'products': products,
            'cart_total': cart_total,
            'shipping': shipping,
        }
 
    def check_coupon(self, cart_total):
        freeShipping = False
        if self.request.session.has_key('coupon_id'):
            coupon_id = self.request.session.get('coupon_id')
            coupon = Coupons.objects.get(id=coupon_id)
            if coupon.total_amount <= cart_total:
                if coupon.free_shipping:
                    freeShipping = True
                if coupon.type == 1:
                    discount = int((coupon.discount/100) * cart_total)
                else:
                    discount = coupon.discount
                coupon_name =  coupon.name
                return {
                    'freeShipping': freeShipping, 'discount': discount, 'coupon_name': coupon_name
                }
            else:
                return -1
                # messages.error(
                #     self.request, 'Coupon is not applicable now')


    def get_context_data(self):
        context = {}
        discount = 0
        if self.request.user.is_authenticated:
            list = self.get_products()
            context['products'] = list['products']
            shipping = list['shipping']
            coupon = self.check_coupon(list['cart_total'])
            if coupon:
                if coupon != -1:
                    context['coupon'] = {'coupon_name': coupon['coupon_name']}
                    discount = coupon['discount']
                    if coupon['freeShipping']:
                        shipping = 0
                else: 
                    messages.error(self.request, 'Coupon is not applicable on this order')
        if context['products']:
            context['subtotal'] = {
                'cart_total': list['cart_total'], 
                'shipping': shipping, 'discount': discount,  
                'total': list['cart_total'] + shipping - discount
                }
            self.request.session['discount'] = discount
            self.request.session['shipping'] = shipping
            self.request.session['total'] = list['cart_total'] + shipping - discount
        user = User.objects.get(username = self.request.user)
        context['checkout_form'] = PaymentForm(user_id=user.id)
        context['coupon_form'] = CouponForm
        return context

    def post(self, request):
        form_type = request.POST['form_type']
        if form_type == 'coupon':
            coupon_form = CouponForm(request.POST or None)
            if coupon_form.is_valid():
                coupon_code = coupon_form.cleaned_data.get('coupon')
                if Coupons.objects.filter(code=coupon_code).exists():
                    now = timezone.now()
                    coupon_obj = Coupons.objects.get(code=coupon_code)
                    uses_per_coupon = CouponUsage.objects.filter(
                        coupon_id=coupon_obj.id).count()
                    uses_per_customer = CouponUsage.objects.filter(
                        coupon_id=coupon_obj.id, used_by_id=request.user.id).count()
                    try:
                        coupon = Coupons.objects.get(
                            code__iexact=coupon_code,
                            start_date__lte=now,
                            end_date__gte=now,
                            active=True,
                            uses_per_customer__gt=uses_per_customer,
                            uses_per_coupons__gt=uses_per_coupon,
                        )
                        request.session['coupon_id'] = coupon.id
                    except Coupons.DoesNotExist:
                        messages.error(request, 'Coupon is not applicable now')
                else:
                    messages.error(request, 'Coupon not available')
            return redirect('user:checkout')
        else:
            form = PaymentForm(request.POST or None,
                               user_id=self.request.user.id)
            if form.is_valid():
                shipping_address = form.cleaned_data.get('shipping_address')
                billing_address = form.cleaned_data.get('billing_address')
                subtotal = request.session.get('total')
                cart_total = request.session.get('cart_total')
                shipping = request.session.get('shipping')
                discount = request.session.get('discount')
                # import pdb;pdb.set_trace()
                if cart_total:
                    if request.session.has_key('coupon_id'):
                        now = timezone.now()
                        coupon_obj = Coupons.objects.get(
                            id=int(request.session['coupon_id']))
                        uses_per_coupon = CouponUsage.objects.filter(
                            coupon_id=coupon_obj.id).count()
                        uses_per_customer = CouponUsage.objects.filter(
                            coupon_id=coupon_obj.id, used_by_id=request.user.id).count()
                        if Coupons.objects.filter(id=int(request.session['coupon_id']), start_date__lte=now, end_date__gte=now, active=True, uses_per_customer__gt=uses_per_customer, uses_per_coupons__gt=uses_per_coupon,).exists():
                            
                            order = Orders(
                                user_id=request.user.id,
                                shipping_address_id=shipping_address,
                                billing_address_id=billing_address,
                                subtotal=subtotal,
                                cart_total=cart_total,
                                shipping_amount=shipping,
                                discount=discount
                            )
                            order.save()
                            coupon_usage = CouponUsage(
                                coupon_id=request.session['coupon_id'],
                                used_by_id=request.user.id,
                                order_id=order.id)
                            coupon_usage.save()
                            OrderHistory.objects.create(
                                order_id=order.id,
                            )
                            for product in ShoppingCart.objects.filter(user_id=self.request.user.id):
                                item = Product.objects.get(
                                    id=product.product_id)
                                image = Images.objects.filter(
                                    product_id=item.id).first()
                                # print('product', product)
                                OrderProductDetails.objects.create(order_id=order.id,
                                                                   product_name=item.name,
                                                                   image=image.image,
                                                                   quantity=product.quantity,
                                                                   price=item.price
                                                                   )
                            for product in ShoppingCart.objects.filter(user_id=self.request.user.id):
                                product.delete()
                            return redirect('user:payment', order_id=order.id)
                        else:
                            messages.error(
                                request, 'Coupon is not applicable now')
                            return redirect('user:checkout')
                    else:
                        order = Orders(
                            user_id=request.user.id,
                            shipping_address_id=shipping_address,
                            billing_address_id=billing_address,
                            subtotal=subtotal,
                            cart_total=cart_total,
                            shipping_amount=shipping,
                            discount=discount
                        )
                        order.save()
                        OrderHistory.objects.create(
                            order_id=order.id,
                        )
                        for product in ShoppingCart.objects.filter(user_id=self.request.user.id):
                            item = Product.objects.get(id=product.product_id)
                            image = Images.objects.filter(
                                product_id=item.id).first()
                            OrderProductDetails.objects.create(order_id=order.id,
                                                               product_name=item.name,
                                                               image=image.image,
                                                               quantity=product.quantity,
                                                               price=item.price
                                                               )
                            for product in ShoppingCart.objects.filter(user_id=self.request.user.id):
                                product.delete()                            
                            return redirect('user:payment', order_id=order.id)
                else:
                    messages.info(request, 'Add Items First')
                    return redirect('user:checkout')
            else:
                # print(form.errors)
                discount = 0
                context = {}
                context['checkout_form'] = form
                if self.request.user.is_authenticated:
                    list = self.get_products()
                    context['products'] = list['products']
                    shipping = list['shipping']
                    coupon = self.check_coupon(list['cart_total'])
                    if coupon:
                        context['coupon'] = {'coupon_name': coupon['coupon_name']}
                        discount = coupon['discount']
                        if coupon['freeShipping']:
                            shipping = 0
                if context['products']:
                    context['subtotal'] = {
                        'cart_total': list['cart_total'], 
                        'shipping': shipping, 'discount': discount,  
                        'total': list['cart_total'] + shipping - discount
                        }
                    self.request.session['discount'] = discount
                    self.request.session['total'] = list['cart_total'] + shipping - discount
                context['coupon_form'] = CouponForm
                self.get_context_data()
                return render(request, 'customUser/checkout.html', context)


class RemoveCoupon(View):
    def get(self, request):
        del request.session['coupon_id']
        return redirect('user:checkout')


class Payment(TemplateView):
    template_name = 'customUser/payment.html'

    def get_context_data(self, order_id):
        context = {}
        order = Orders.objects.get(id=order_id)
        context['order_id'] = order_id
        context['details'] = {'cart_total': order.cart_total, 'subtotal': order.subtotal,
                              'shipping': order.shipping_amount, 'discount': order.discount}
        return context


class PaymentCheck(View):
    def get(self, request):
        # import pdb; pdb.set_trace()
        order = request.GET['order']
        orderid = request.GET['id']
        status = request.GET['status']
        email = request.GET['email']
        name = request.GET['name']
        order_obj = Orders.objects.get(id=order)
        order_obj.status = 'Order Placed'
        order_obj.save()
        OrderHistory.objects.create(
            order_id=order,
            status='Order Placed'
        )
        paymentDetails = PaymentDetails.objects.get(order_id = order)
            # order_id=order,
            # user_id=request.user.id,
        # import pdb; pdb.set_trace()
        paymentDetails.payment_mode='netbanking'
        paymentDetails.transaction_id=orderid
        paymentDetails.payment_status=status
        paymentDetails.email=email
        paymentDetails.name=name
        paymentDetails.save()

        for product in OrderProductDetails.objects.filter(order_id = order):
            item = Product.objects.get(name = product.product_name)
            item.quantity = item.quantity - product.quantity
            if item.quantity - product.quantity == 0:
                item.out_of_stock_status = True
            item.save()
        if request.session.has_key('total'):
            del request.session['total']
        if request.session.has_key('cart_total'):
            del request.session['cart_total']
        if request.session.has_key('shipping'):
            del request.session['shipping']
        if request.session.has_key('discount'):
            del request.session['discount']
        if request.session.has_key('coupon_id'):
            del request.session['coupon_id']
        return HttpResponse('done')
        # return render(request, 'customUser/payment-success.html')


def render_to_pdf(template_src, context_dict):

    template = get_template(template_src)
    # context = Context(context_dict)
    html = template.render(context_dict)
    result = StringIO.BytesIO()

    pdf = pisa.pisaDocument(StringIO.BytesIO(
        html.encode("ISO-8859-1")), result)
    if not pdf.err:
        # return HttpResponse(result.getvalue(), content_type='application/pdf')
        return result.getvalue()
    return None
    # return HttpResponse('We had some errors<pre>%s</pre>'
    # # % escape(html)
    # )


class PaymentCOD(View):
    def get(self, request, order_id):
        order_obj = Orders.objects.get(id=order_id)
        order_obj.status = 'Order Placed'
        order_obj.save()
        OrderHistory.objects.create(
            order_id=order_id,
            status='Order Placed'
        )
        paymentDetails = PaymentDetails.objects.get(order_id = order_id)
        paymentDetails.payment_mode='cod'
        paymentDetails.payment_status='Pending'
        paymentDetails.save()
        for product in OrderProductDetails.objects.filter(order_id = order_id):
            item = Product.objects.get(name = product.product_name)
            item.quantity = item.quantity - product.quantity
            if item.quantity - product.quantity == 0:
                item.out_of_stock_status = True
            item.save()
        if request.session.has_key('total'):
            del request.session['total']
        if request.session.has_key('cart_total'):
            del request.session['cart_total']
        if request.session.has_key('shipping'):
            del request.session['shipping']
        if request.session.has_key('discount'):
            del request.session['discount']
        if request.session.has_key('coupon_id'):
            del request.session['coupon_id']
        return redirect('user:payment_success', order_id=order_id)


@cache_control(no_cache=True, must_revalidate=True)
def PaymentSuccess(request, order_id):
    order = Orders.objects.get(id=order_id)
    order_list = OrderProductDetails.objects.filter(order_id=order_id)
    products = []
    for product in order_list:
        products.append({
            'product_name': product.product_name,
            'quantity': product.quantity,
            'price': product.price,
            'total': product.price * product.quantity
        })
    attachment = render_to_pdf(
        'customUser/invoice.html',
        {
            'pagesize': 'A4',
            'shipping_address': AddressBook.objects.get(id=order.shipping_address_id),
            'billing_address': AddressBook.objects.get(id=order.billing_address_id),
            'date': order.order_date,
            'subtotal': order.subtotal,
            'cart_total': order.cart_total,
            'shipping_amount': order.shipping_amount,
            'discount': order.discount,
            'products': products,
            'payment': PaymentDetails.objects.get(order_id=order_id),
            'id': order_id
        }
    )
    user_object = User.objects.get(id=request.user.id)
    email_template = Email_Template.objects.get(code='ET02')
    send_email(
        email=user_object.email,
        attachment=attachment,
        subject=email_template.subject,
        message=email_template.message,
        name=user_object.first_name + " " + user_object.last_name,
    )
    return render(request, 'customUser/payment-success.html')


@cache_control(no_cache=True, must_revalidate=True)
def PaymentFailure(request):
    return render(request, 'customUser/payment-failure.html')

