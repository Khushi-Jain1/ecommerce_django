import datetime
from django.core.exceptions import ValidationError
from django.db.models import fields
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers
from customAdmin.helpers import send_email

from customUser.models import AddressBook, CouponUsage, OrderHistory, OrderProductDetails, Orders, PaymentDetails, ProductReview, ShoppingCart, WishList
from . models import *
from customAdmin.models import Attribute, AttributeValues, Banners, Category, Coupons, Email_Template, Images, Product, Product_attribute_association, User, ViewMessage
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.flatpages.models import FlatPage


class CategorySerializer(serializers.ModelSerializer):
    childs = serializers.SerializerMethodField('count_childs')

    def count_childs(self, category):
        return category['childs']

    class Meta:
        model = Category
        fields = ['name', 'parent_category_id', 'active', 'id', 'childs']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banners
        fields = ['id', 'title', 'subtitle', 'paragraph', 'link', 'image']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('__all__')


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField('get_images')
    attributes = serializers.SerializerMethodField('get_attributes')

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'brand', 'price', 'quantity', 'out_of_stock_status',
                  'status', 'shipping_required', 'category', 'images', 'attributes')

    def get_images(self, product):
        return [image.image.url for image in Images.objects.filter(product_id=product.id)]

    def get_attributes(self, product):
        attributes = []
        for attribute in Product_attribute_association.objects.filter(product_id=product.id):
            attribute_text = Attribute.objects.get(
                id=attribute.attribute_id).name
            if not any(d['attribute'] == attribute_text for d in attributes):
                values = []
                for attr in Product_attribute_association.objects.filter(product_id=product.id).filter(attribute_id=attribute.attribute_id):
                    value = AttributeValues.objects.get(id=attr.value_id)
                    values.append(value.name)
                attributes.append(
                    {'attribute': attribute_text, 'values': values})
        return attributes


class BrandSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField('get_slug')
    count = serializers.SerializerMethodField('count_products')

    def get_slug(self, product):
        return slugify(product['brand'])

    def count_products(self, product):
        return product['count']

    class Meta:
        model = Product
        fields = ['brand', 'slug', 'count']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        return token


class AddWishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'


class ListWishlistSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField("get_product_name")
    price = serializers.SerializerMethodField("get_product_price")
    image = serializers.SerializerMethodField("get_product_image")

    class Meta:
        model = WishList
        fields = '__all__'

    def get_product_name(self, wishlist):
        return Product.objects.get(id=wishlist.product_id).name

    def get_product_price(self, wishlist):
        return Product.objects.get(id=wishlist.product_id).price

    def get_product_image(self, wishlist):
        images = Images.objects.filter(product_id=wishlist.product_id).first()
        return images.image.url


class AddCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

    # def validate(self, attrs):
    #     if attrs['product'].quantity < attrs['quantity']:
    #         raise serializers.ValidationError({"quantity": "Not in stock"})
    #     return attrs

class ListCartSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField("get_product_name")
    price = serializers.SerializerMethodField("get_product_price")
    image = serializers.SerializerMethodField("get_product_image")
    out_of_stock = serializers.SerializerMethodField("get_out_of_stock_status")

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def get_product_name(self, shopping_cart):
        return Product.objects.get(id=shopping_cart.product_id).name

    def get_product_price(self, shopping_cart):
        return Product.objects.get(id=shopping_cart.product_id).price

    def get_product_image(self, shopping_cart):
        images = Images.objects.filter(product_id=shopping_cart.product_id).first()
        return images.image.url

    def get_out_of_stock_status(self, shopping_cart):
        product = Product.objects.get(id=shopping_cart.product_id)
        return shopping_cart.quantity > product.quantity

class AddresSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressBook
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewMessage
        fields = '__all__'


class FlatPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatPage
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'mobile_number', 'image']


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        elif attrs['old_password'] == attrs['new_password1']:
            raise serializers.ValidationError(
                {'password': "New password shouldn't be same as old password"})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"})
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        user.set_password(validated_data['new_password1'])
        user.save()
        return user


class PriceRangeSerializer(serializers.ModelSerializer):
    min = serializers.SerializerMethodField("get_min_price_range")
    max = serializers.SerializerMethodField("get_max_price_range")

    class Meta:
        model = Product
        fields = ['min', 'max']

    def get_min_price_range(self, product):
        return product['min']

    def get_max_price_range(self, product):
        return product['max']


class ForgetPasswordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['user', 'email']

    def validate(self, attrs):
        if not User.objects.filter(username=attrs['user'], email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"message": "User doesn't exist"})
        return attrs


class RecoverPasswordSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(write_only=True, required=True)
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['otp', 'new_password1', 'new_password2']

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        elif not User.objects.filter(forget_password_token=attrs['otp']).exists():
            raise ValidationError("Invalid OTP")
        else:
            profile_obj = User.objects.get(forget_password_token=attrs['otp'])
            if profile_obj.token_expiry < timezone.now():
                raise ValidationError("OTP Expired")
            elif profile_obj.check_password(attrs['new_password1']):
                raise ValidationError(
                    "New password should not be same as old one")
        return attrs

    def create(self, validated_data):
        profile_obj = User.objects.get(
            forget_password_token=validated_data['otp'])
        profile_obj.set_password(validated_data['new_password1'])
        profile_obj.forget_password_token = None
        profile_obj.save()
        return profile_obj


class TrackOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = '__all__'


class MyOrderSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField("get_product")
    shipping_address = serializers.SerializerMethodField(
        "get_shipping_address")
    billing_address = serializers.SerializerMethodField("get_billing_address")
    coupon = serializers.SerializerMethodField("get_coupon")
    payment = serializers.SerializerMethodField("get_payment_info")

    class Meta:
        model = Orders
        fields = '__all__'

    def get_shipping_address(self, orders):
        return orders.shipping_address.name + ", " + orders.shipping_address.address_line1 +  \
            ", " + orders.shipping_address.address_line2 + " ," + orders.shipping_address.city + \
            ", " + orders.shipping_address.state + ", " + orders.shipping_address.country

    def get_billing_address(self, orders):
        return orders.billing_address.name + ", " + orders.billing_address.address_line1 +  \
            ", " + orders.billing_address.address_line2 + " ," + orders.billing_address.city + \
            ", " + orders.billing_address.state + ", " + orders.billing_address.country

    def get_product(self, orders):
        return [{'product_name': product.product_name,
                 'image': product.image.url,
                 'quantity': product.quantity,
                 'price': product.price} for product in OrderProductDetails.objects.filter(order_id=orders.id)]

    def get_coupon(self, orders):
        if CouponUsage.objects.filter(order_id=orders.id).exists():
            coupon_usage = CouponUsage.objects.get(order_id=orders.id)
            coupon = Coupons.objects.get(id=coupon_usage.coupon_id)
            return coupon.name
        else:
            return ""

    def get_payment_info(self, orders):
        row = PaymentDetails.objects.get(order_id=orders.id)
        return {
            'payment_mode': row.payment_mode,
            'transaction_id': row.transaction_id,
            'payment_status': row.payment_status,
            'email': row.email,
            'name': row.email,
        }


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupons
        fields = ('__all__')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ('__all__')

class ProductReviewsSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField("get_name")
    avatar = serializers.SerializerMethodField("get_avatar")

    class Meta:
        model = ProductReview
        fields = ('__all__')

    def get_name(self, productReview):
        user = User.objects.get(id = productReview.name.id)
        return user.first_name + " " + user.last_name

    def get_avatar(self, productReview):
        user = User.objects.get(id = productReview.name.id)
        if user.image:
            return user.image.url
        return None