from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **kwargs):
        """Create and return a `User` with an email, phone number, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')
        if email is None:
            raise TypeError('Users must have an email.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')
        if email is None:
            raise TypeError('Superusers must have an email.')
        if username is None:
            raise TypeError('Superusers must have an username.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractUser):
    mobile_number = models.CharField(null=True, blank=True, max_length=10)
    forget_password_token = models.CharField(max_length=100, null=True)
    token_expiry = models.DateTimeField(null=True)
    image = models.ImageField(upload_to='./profile-images/', null=True)

    USERNAME_FIELD = 'username'

    # objects = UserManager()

    def __str__(self):
        return self.username


class Common(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="%(app_label)s_%(class)s_created_by")
    modified_on = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                    null=True, related_name="%(app_label)s_%(class)s_modified_by")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = kwargs.get("user")
        if self.pk:
            self.modified_by = user
        else:
            self.created_by = user
            self.modified_by = user
        super(Common, self).save()


class Category(Common):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(null=True)
    parent_category = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=False)
    slug = models.SlugField(max_length=250, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    # TODO no defaults on fk fields
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.CharField(max_length=20)
    price = models.IntegerField()
    quantity = models.IntegerField()
    out_of_stock_status = models.BooleanField()
    status = models.BooleanField()
    shipping_required = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, )
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    # modified_by = models.ForeignKey(User,on_delete=models.CASCADE)
    modified_on = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.name


class Images(models.Model):
    description = models.TextField(null=True)
    image = models.ImageField(upload_to='./product-images/', null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.image)


class Attribute(models.Model):
    name = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AttributeValues(models.Model):
    name = models.CharField(max_length=50)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class Product_attribute_association(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.ForeignKey(AttributeValues, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Coupons(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    type = models.IntegerField(default=2)
    discount = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    # customer_login = models.BooleanField(default=True)
    free_shipping = models.BooleanField(default=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    uses_per_coupons = models.IntegerField(blank=True)
    uses_per_customer = models.IntegerField(blank=True)
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ViewMessage(models.Model):
    name = models.CharField(max_length=20)
    mail = models.EmailField(blank=True)
    mailed_on = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=50)
    message = models.TextField()
    reply = models.TextField(null=True)
    replied_on = models.DateTimeField( null=True)
    user_logged_in = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Email_Template(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, blank=True)
    subject = models.CharField(max_length=50, blank=True)
    # html_content = models.BooleanField(default=False)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Banners(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, null=True)
    paragraph = models.CharField(max_length=150)
    link = models.CharField(max_length=100)
    image = models.ImageField(upload_to='./banners/', null=True)

    def __str__(self):
        return self.title