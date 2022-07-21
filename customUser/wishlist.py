from logging import log
import logging
from django.views.generic.edit import DeleteView
from customUser.products import ProductDetails
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from customAdmin.models import Product, Images
from customUser.models import ShoppingCart, WishList
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.urls.base import reverse_lazy
from django.views import View
from Ecommerce.settings import MEDIA_URL

class WishlistView(LoginRequiredMixin, TemplateView):
    login_url = 'user:login'
    template_name = 'customUser/wishlist.html'

    def get_context_data(self):
        context = {}
        data = []
        if WishList.objects.filter(user_id = self.request.user.id).exists():
            wishlist = WishList.objects.filter(user_id = self.request.user.id)
            for row in wishlist:
                product = Product.objects.get(id = row.product_id)
                image = Images.objects.filter(product_id = row.product_id).first()
                data.append({
                    'image': image.image,
                    'name': product.name,
                    'price': product.price,
                    'media': MEDIA_URL,
                    'wishlist_id': row.id,
                    'product_id': product.id,
                })
        context['wishlist'] = data
        return context

class AddWishlist(LoginRequiredMixin, View):
    login_url = 'user:login'
    def get(self, request, product_id):
        try:
            if not WishList.objects.filter(user_id = request.user.id, product_id = product_id).exists():
                WishList.objects.create(
                user_id = request.user.id,
                product_id = product_id
            )
            return redirect('user:product-details', product_id)
        except Exception as e:
            logging.error(e)

class DeleteWishlistProduct(LoginRequiredMixin, DeleteView):
    login_url = 'user:login'
    model = WishList
    success_url = reverse_lazy('user:wishlist')

class AddToCart(LoginRequiredMixin, View):
    login_url = 'user:login'
    def get(self, request, id):
        try:
            ProductDetails.add_product(self, request, id, 1)
            return redirect('user:wishlist')
        except Exception as e:
            logging.error(e)
