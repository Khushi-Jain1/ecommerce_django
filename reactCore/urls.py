# from django.conf.urls import url
from django.db.models import base
from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import *


# app_name = 'api'
# urlpatterns = [
#     path('category/', CategoryView, name='category'),
#  ]

routes = SimpleRouter()

routes.register(r'category', CategoryView, basename='category')
routes.register(r'banners', BannersView, basename='banners')
routes.register(r'brand', BrandView, basename='brand')
routes.register(r'product', ProductView, basename='product')
routes.register(r'wishlist', WishlistView, basename='wishlist')
routes.register(r'cart', CartView, basename='cart')
routes.register(r'address', AddressView, basename='address')
routes.register(r'contact', ContactView, basename='contact')
routes.register(r'extra', FlatPageView, basename='contact')
routes.register(r'profile', ProfileView, basename='profile')
routes.register(r'changePassword', ChangePasswordView, basename='changePassword')
routes.register(r'price-range', PriceRangeView, basename='price-range')
routes.register(r'forgot-password', ForgotPasswordView, basename='forgot-password')
routes.register(r'track-order', TrackOrderView, basename = 'track-order')
routes.register(r'recover-password', RecoverPasswordView, basename = 'recover-password')
routes.register(r'order', MyOrderView, basename = 'order')
routes.register(r'coupon', CouponView, basename='coupon')
routes.register(r'payment', PaymentCheck, basename='payment')
routes.register(r'product-review', ProductReviewView, basename='product-review')




urlpatterns = [
    *routes.urls
]