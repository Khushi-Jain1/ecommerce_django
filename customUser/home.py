from django.db.models.aggregates import Count, Max, Min
from django.utils.text import slugify
from django.views.generic import TemplateView
from Ecommerce.settings import MEDIA_URL

from customAdmin.models import Banners, Category, Images, Product


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        products = []
        context = super().get_context_data(**kwargs)
        brands = Product.objects.values(
            'brand').annotate(count=Count('brand')).order_by()
        for brand in brands:
            brand.update({'slug': slugify(brand['brand'])})
        context['brands'] = brands
        category = []
        for cat in Category.objects.all():
            category.append({'id': cat.id, 'name': cat.name, 'parent_category_id': cat.parent_category_id, 'slug': slugify(cat.name),
                            'childs': Category.objects.filter(parent_category_id=cat.id).exists()})
        for product in Product.objects.all():
            if Images.objects.filter(product_id=product.id).exists():
                image = Images.objects.filter(product_id=product.id).first()
            products.append({
                'id': product.id, 'name': product.name, 'price': product.price,
                'image': image.image if Images.objects.filter(product_id=product.id).exists() else None,
                'media': MEDIA_URL,
                'image_alt': image.description if Images.objects.filter(product_id=product.id).exists() else None
            })
        context['products'] = products
        context['category'] = category
        context['media'] = MEDIA_URL
        context['slides'] = Banners.objects.all()
        context['price'] = {
            'max': Product.objects.all().aggregate(Max('price'))['price__max'],
            'min': Product.objects.all().aggregate(Min('price'))['price__min'],}
        return context


