from django.core.validators import MaxValueValidator
from customAdmin.models import Coupons, Product, User
from django.db import models

# Create your models here.


class AddressBook(models.Model):
    name = models.CharField(max_length=50, default='user')
    mobile_number = models.CharField(max_length=10)
    pincode = models.CharField(max_length=10)
    address_line1 = models.CharField(max_length=20)
    address_line2 = models.CharField(max_length=20)
    city = models.CharField(max_length=10)
    state = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=10)
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(
            self.name + '\n' +
            self.address_line1 + " ,\n" + 
            self.address_line2 + " ,\n" + 
            self.city + " ,\n" + 
            self.state + " ,\n" +
            self.country
        )


class ShoppingCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MaxValueValidator(10)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Orders(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    shipping_address = models.ForeignKey(AddressBook, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_shipping_address")
    billing_address = models.ForeignKey(AddressBook, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_billing_address")
    status = models.CharField(max_length=20, default='Pending')
    subtotal = models.IntegerField()
    cart_total = models.IntegerField()
    shipping_amount = models.IntegerField()
    discount = models.IntegerField()


class OrderProductDetails(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=100, default='product_name')
    image = models.ImageField(upload_to = './ordered-products/')
    quantity = models.IntegerField()
    price = models.IntegerField()

class OrderHistory(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    status = models.CharField(default='Pending', max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)

class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupons, on_delete=models.CASCADE)
    used_by = models.ForeignKey(User, on_delete=models.PROTECT)
    used_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)

class PaymentDetails(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_mode = models.CharField(default='netbanking', max_length=50)
    transaction_id = models.CharField(max_length=100, null=True)
    payment_status = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=50, null=True)

class WishList(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class ProductReview(models.Model):
    name = models.ForeignKey(User, on_delete=models.PROTECT)
    review = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
