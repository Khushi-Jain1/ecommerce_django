from logging import disable
import random
import string
from django.db.models.aggregates import Count, Max, Min
from django.db.models.query import QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.utils import serializer_helpers
from core import user
from customAdmin.models import Category, ViewMessage
from customUser.models import Orders
from customUser.views import render_to_pdf
from . models import *
from rest_framework.response import Response
from .serializers import *
from django.contrib.flatpages.models import FlatPage
# Create your views here.


class CategoryView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
    queryset = [{
        "id": detail.id,
        "name": detail.name,
        "parent_category_id": detail.parent_category_id,
        "active": detail.active,
        "childs": Category.objects.filter(parent_category_id=detail.id).count()
    } for detail in Category.objects.all().order_by('name')]


class BannersView(viewsets.ModelViewSet):
    serializer_class = BannerSerializer
    permission_classes = (AllowAny,)
    queryset = Banners.objects.all()


class ProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)
    queryset = Product.objects.filter(status=True).order_by("category")


class BrandView(viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = (AllowAny,)
    queryset = Product.objects.values('brand').annotate(
        count=Count('brand')).order_by('brand')


class WishlistView(viewsets.ModelViewSet):
    serializer_action_class = {
        'create': AddWishlistSerializer,
        'list': ListWishlistSerializer,
    }
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if not WishList.objects.filter(user_id=request.data['user'], product_id=request.data['product']).exists():
            return super().create(request, *args, **kwargs)
        return Response('Already exist in wishlist', status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = WishList.objects.filter(user_id=self.request.user.id)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        return self.serializer_action_class[self.action]


class CartView(viewsets.ModelViewSet):
    serializer_action_class = {
        'create': AddCartSerializer,
        'list': ListCartSerializer,
        'update': AddCartSerializer,
    }
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if not ShoppingCart.objects.filter(user_id=request.data['user'], product_id=request.data['product']).exists():
            return super().create(request, *args, **kwargs)
        else:
            serializer = ShoppingCart.objects.get(
                user_id=request.data['user'], product_id=request.data['product'])
            serializer.quantity = serializer.quantity + \
                request.data['quantity']
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer)
            return Response({'id': serializer.id, 'product': serializer.product_id, 'quantity': serializer.quantity, 'user': serializer.user_id}, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        queryset = ShoppingCart.objects.filter(
            user_id=self.request.user.id).order_by("-id")
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def get_serializer_class(self, *args, **kwargs):
        return self.serializer_action_class[self.action]


class AddressView(viewsets.ModelViewSet):
    serializer_class = AddresSerializer
    permission_classes = (IsAuthenticated,)
    queryset = AddressBook.objects.filter(status=True)

    def get_queryset(self):
        queryset = AddressBook.objects.filter(
            user_id=self.request.user.id, status=True)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        if not AddressBook.objects.filter(
            name=request.data['name'],
            mobile_number=request.data['mobile_number'],
            pincode=request.data['pincode'],
            address_line1=request.data['address_line1'],
            address_line2=request.data['address_line2'],
            city=request.data['city'],
            state=request.data['state'],
            user=request.data['user'],
            country=request.data['country']
        ).exists():
            return super().create(request, *args, **kwargs)
        else:
            address = AddressBook.objects.get(
                name=request.data['name'],
                mobile_number=request.data['mobile_number'],
                pincode=request.data['pincode'],
                address_line1=request.data['address_line1'],
                address_line2=request.data['address_line2'],
                city=request.data['city'],
                state=request.data['state'],
                user=request.data['user'],
                country=request.data['country']
            )
            address.status = True
            address.save()
            return Response('User Created', status=status.HTTP_201_CREATED)


class ContactView(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = (AllowAny,)
    queryset = ViewMessage.objects.all()

    def create(self, request, *args, **kwargs):
        if not ViewMessage.objects.filter(name=request.data['name'],
                                          mail=request.data['mail'],
                                          subject=request.data['subject'],
                                          message=request.data['message']).exists():
            return super().create(request, *args, **kwargs)
        else:
            return Response("Message already sent", status=status.HTTP_200_OK)


class FlatPageView(viewsets.ModelViewSet):
    serializer_class = FlatPageSerializer
    permission_classes = (AllowAny,)
    queryset = FlatPage.objects.all()


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    # queryset = User.objects.all()

    def get_queryset(self):
        queryset = User.objects.filter(
            id=self.request.user.id, is_active=True)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.user.id)
        user.image = request.data['file']
        user.save()
        return Response("Image Updated", status=status.HTTP_200_OK)


class ChangePasswordView(viewsets.ModelViewSet):

    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = User.objects.filter(
            id=self.request.user.id, is_active=True)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


class PriceRangeView(viewsets.ModelViewSet):
    serializer_class = PriceRangeSerializer
    permission_classes = (AllowAny,)
    queryset = [{
        "min": Product.objects.all().aggregate(Min('price'))['price__min'],
        "max": Product.objects.all().aggregate(Max('price'))['price__max']
    }]


class ForgotPasswordView(viewsets.ModelViewSet):
    serializer_class = ForgetPasswordSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = User.objects.filter(
            id=self.request.user.id, is_active=True)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        token = ''.join([random.choice(string.ascii_uppercase +
                                       string.ascii_lowercase +
                                       string.digits)
                         for n in range(10)])
        user_object = User.objects.get(username=request.data['user'])
        nextTime = datetime.datetime.now() + datetime.timedelta(minutes=15)
        user_object.token_expiry = nextTime
        user_object.forget_password_token = token
        user_object.save()
        email_template = Email_Template.objects.get(code='ET07')
        send_email(
            email=user_object.email,
            otp=token,
            subject=email_template.subject,
            message=email_template.message,
            name=user_object.first_name + " " + user_object.last_name,
        )
        return Response({"message": "OTP sent to your registered mail id"}, status=status.HTTP_200_OK, headers=headers)


class RecoverPasswordView(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = RecoverPasswordSerializer
    queryset = User.objects.all()


class TrackOrderView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TrackOrderSerializer
    queryset = OrderHistory.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('order_id'):
            if Orders.objects.filter(id=int(self.request.query_params.get('order_id')), user_id=request.user.id).exists():
                result = queryset.filter(
                    order=int(self.request.query_params.get('order_id')))
                serializer = self.get_serializer(result, many=True)
                return Response(serializer.data)
            else:
                return Response({"error": "Invalid Order Id"})
        else:
            return Response({"error": "Enter Order Id first"})


class MyOrderView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = MyOrderSerializer
    # serializer_action_class = {
    #     'list' : MyOrderSerializer,
    #     # 'create': CreateOrderSerializer,
    # }

    def get_queryset(self):
        queryset = Orders.objects.filter(
            user_id=self.request.user.id)
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        shipping_address = self.request.data['shipping_address']
        # shipping_address = self.request.query_params.get('shipping_address')
        billing_address = self.request.data['billing_address']
        coupon_name = self.request.data['coupon']
        discount = self.request.data['discount']
        cart_total = 0
        for row in ShoppingCart.objects.filter(user_id=self.request.user.id):
            cart_total += row.quantity * \
                Product.objects.get(id=row.product_id).price
        if cart_total >= 500:
            shipping_amount = 0
        elif coupon_name and Coupons.objects.get(name=coupon_name).free_shipping:
            shipping_amount = 0
        else:
            shipping_amount = 50
        subtotal = cart_total + shipping_amount - discount
        order = Orders(user=request.user, shipping_address_id=shipping_address, billing_address_id=billing_address,
                       subtotal=subtotal, cart_total=cart_total, shipping_amount=shipping_amount, discount=discount)
        order.save()
        OrderHistory.objects.create(order_id=order.id)
        if coupon_name:
            coupon = Coupons.objects.get(name=coupon_name)
            CouponUsage.objects.create(
                coupon=coupon, used_by=request.user, order=order)
        for row in ShoppingCart.objects.filter(user_id=self.request.user.id):
            product = Product.objects.get(id=row.product_id)
            if product.quantity - row.quantity == 0:
                product.out_of_stock_status = True
            product.quantity = product.quantity - row.quantity
            product.save()
            image = Images.objects.filter(product_id=row.product_id).first()
            OrderProductDetails.objects.create(order_id=order.id, product_name=product.name, quantity=row.quantity, price=product.price,
                                               image=image.image)
        for product in ShoppingCart.objects.filter(user_id=self.request.user.id):
            product.delete()

        return Response({'order_id': order.id}, status=status.HTTP_201_CREATED)

    # def get_serializer_class(self, *args, **kwargs):
    #     return self.serializer_action_class[self.action]


class CouponView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CouponSerializer
    queryset = Coupons.objects.all()

    def list(self, request, *args, **kwargs):
        coupon_code = self.request.query_params.get('coupon_code')
        if Coupons.objects.filter(code=coupon_code).exists():
            now = timezone.now()
            coupon_obj = Coupons.objects.get(code=coupon_code)
            uses_per_coupon = CouponUsage.objects.filter(
                coupon_id=coupon_obj.id).count()
            uses_per_customer = CouponUsage.objects.filter(
                coupon_id=coupon_obj.id, used_by_id=request.user.id).count()
            total_amount = float(self.request.query_params.get('total_amount'))
            total_amount = "{:.2f}".format(total_amount)
            try:
                coupon = Coupons.objects.get(
                    code__iexact=coupon_code,
                    start_date__lte=now,
                    end_date__gte=now,
                    active=True,
                    uses_per_customer__gt=uses_per_customer,
                    uses_per_coupons__gt=uses_per_coupon,
                    total_amount__lte=float(total_amount),
                )
                if coupon:
                    if coupon.type == 1:
                        discount = coupon.discount/100 * float(total_amount)
                    else:
                        discount = coupon.discount
                return Response({
                    'discount': discount,
                    'coupon': coupon.name,
                    'free_shipping': coupon.free_shipping
                })
            except Coupons.DoesNotExist:
                return Response({'error': 'Coupon is not applicable now'})
        else:
            return Response({'error': 'Coupon not available'})


class PaymentCheck(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    queryset = Orders.objects.all()

    def list(self, request, *args, **kwargs):
        payment_method = self.request.query_params.get('payment_method')
        order_id = self.request.query_params.get('order_id')
        queryset = self.filter_queryset(self.get_queryset())
        if payment_method == 'cod':
            payment = PaymentDetails.objects.get(order_id=order_id)
            payment.payment_mode = 'cod'
            payment.save()
            OrderHistory.objects.create(
                status='Order Placed', order_id=order_id)
            order = Orders.objects.get(id=order_id)
            order.status = 'Order Placed'
            order.save()
        else:
            payment = PaymentDetails.objects.get(order_id=order_id)
            payment.transaction_id = self.request.query_params.get(
                'transaction_id')
            payment.email = self.request.query_params.get('email')
            payment.name = self.request.query_params.get('name')
            payment.payment_status = self.request.query_params.get('status')
            payment.save()
            OrderHistory.objects.create(
                status='Order Placed', order_id=order_id)
            order = Orders.objects.get(id=order_id)
            order.status = 'Order Placed'
            order.save()
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
        user_object = User.objects.get(id=self.request.user.id)
        email_template = Email_Template.objects.get(code='ET02')
        send_email(
            email=user_object.email,
            attachment=attachment,
            subject=email_template.subject,
            message=email_template.message,
            name=user_object.first_name + " " + user_object.last_name,
        )
        result = queryset.filter(
            id=int(self.request.query_params.get('order_id')))

        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)


class ProductReviewView(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = ProductReviewsSerializer
    queryset = ProductReview.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        result = queryset.filter(product_id=int(
            self.request.query_params.get('product')))
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().create(request, *args, **kwargs)
        else:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_200_OK)
