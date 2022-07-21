from customUser import contact, orders
# from django.conf.urls import url
from django.urls import path

from . import views
from . import home
from . import products
from . import address
from . import wishlist

app_name = 'user'
urlpatterns = [
    path('', home.HomeView.as_view(), name='home'),

    path('products/', products.ProductsView.as_view(), name='products'),
    path('products/<str:parent>/<slug:slug>/', products.FilterProductsView.as_view(), name='filter_products'),
    path('products/<id>', products.ProductDetails.as_view(), name='product-details'),
    path(r'^range/$', products.RangeFilter.as_view(), name='range'),

    path('search/', products.SearchView.as_view(), name='search'),

    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('profile/<int:pk>/update/', views.ProfileView.as_view(), name='profile'),
    path('forget-password/', views.PasswordReset.as_view(), name='forget_password'),
    path('recover-password/<token>/', views.RecoverPassword.as_view(), name='recover' ),
    path('change-password/', views.ChangePassword.as_view(), name='change'),

    path('address/', address.AddressView.as_view(), name='address'),
    path('address/add-address/', address.AddAddress.as_view(), name='add-address'),
    path('address/<int:pk>/update/', address.EditAddress.as_view(), name='edit-address'),
    path('address/<id>/delete/', address.DeleteAddress.as_view(), name='delete-address'),

    path('shopping-cart/', views.CartView.as_view(), name='cart'),
    path(r'^shopping-cart/product_quantity/$', views.ChangeProductQuantity.as_view(), name='product_quantity'),
    path(r'^checkout/product_quantity/$', views.ChangeProductQuantity.as_view(), name='checkout'),
    path('shopping-cart/<pk>/delete/', views.DeleteCartProduct.as_view(), name='delete_cartProduct'),

    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    path('checkout/remove-coupon/', views.RemoveCoupon.as_view(), name='remove_coupon'),
    path('checkout/payment/<order_id>/', views.Payment.as_view(), name='payment'),
    path(r'^checkout/netbanking/$', views.PaymentCheck.as_view(), name='payment-done'),
    path('checkout/paymentsuccess/<order_id>/', views.PaymentSuccess, name='payment_success'),
    path('checkout/paymentfail/', views.PaymentFailure, name='payment_failure'),
    path('checkout/cod/<order_id>/', views.PaymentCOD.as_view(), name='paymeny_cod'),

    path('wishlist/', wishlist.WishlistView.as_view(), name='wishlist'),
    path('wishlist/<product_id>/', wishlist.AddWishlist.as_view(), name='add-wishlist'),
    path('wishlist/<pk>/delete/', wishlist.DeleteWishlistProduct.as_view(), name='delete_wishlistProduct'),
    path('wishlist/addToCart/<id>/', wishlist.AddToCart.as_view(), name='add_to_cart'),

    path('myorders/', orders.MyOrders.as_view(), name='my_orders'),
    path('track-order/', orders.TrackOrder.as_view(), name='track-order'),
    
    path('contact-us/', contact.Contact.as_view(), name='contact_us'),
    path('subscribe/', contact.NewsletterView.as_view(), name='subscribe'),
 ]