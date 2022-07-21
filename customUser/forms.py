from django.core.exceptions import ValidationError
from builtins import super
from django.forms import fields, widgets
from customAdmin import models
from customUser.models import AddressBook, ProductReview, ShoppingCart
from customAdmin.models import Product, User, ViewMessage
# from django.contrib.admin
from django import forms
# from django.contrib.auth.models import User
from string import Template
from django.utils.safestring import mark_safe


# class PictureWidget(forms.widgets.Widget):
#     def render(self, name, value, attrs=None, **kwargs):
#         html =  Template("""<img src="$link"/>""")
#         return mark_safe(html.substitute(link=value))


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=10, required=False, widget=forms.TextInput(
        attrs={'placeholder': 'First Name'}))
    username = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    last_name = forms.CharField(required=False, max_length=10, widget=forms.TextInput(
        attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}))
    mobile_number = forms.IntegerField(
        required=False, widget=forms.TextInput(attrs={'placeholder': 'Mobile number'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'mobile_number', 'image']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username = username).exists():
            raise ValidationError('Username already exists.')
        return username


class AddressForm(forms.ModelForm):
    name = forms.CharField(max_length=50)
    mobile_number = forms.CharField(widget=forms.NumberInput)
    # address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
    pincode = forms.CharField(widget=forms.NumberInput)
    address_line1 = forms.CharField(max_length=20)
    address_line2 = forms.CharField(max_length=20)
    city = forms.CharField(max_length=10)
    state = forms.CharField(max_length=10)
    country = forms.CharField(max_length=10)

    class Meta:
        model = AddressBook
        exclude = ['user', 'status']


class CouponForm(forms.Form):
    coupon = forms.CharField(max_length=10)


class PaymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.userid = kwargs.pop('user_id', None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        address = [{None, '--------'}]
        for row in AddressBook.objects.filter(user_id=self.userid, status=True):
            address.append({row.id, row})
        self.fields['shipping_address'].choices = address
        self.fields['billing_address'].choices = address

    shipping_address = forms.ChoiceField()
    billing_address = forms.ChoiceField()

    def clean(self):
        # import pdb; pdb.set_trace()
        for item in ShoppingCart.objects.filter(user_id = self.userid):
            product = Product.objects.get(id = item.product_id)
            if item.quantity > product.quantity:
                raise ValidationError("Products not available")
    # payment_method =  forms.ChoiceField(choices=[('cod','COD (Cash on Delivery)'),('paypal','Paypal')], widget=forms.RadioSelect)


class TrackOrderForm(forms.Form):
    order_id = forms.CharField(max_length=5)


class ContactForm(forms.ModelForm):
    class Meta:
        model = ViewMessage
        exclude = ['reply', 'replied_on']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'mail': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message Here', 'rows': 8})
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model=ProductReview
        fields = ['review']
        widgets = {
            'review': forms.Textarea(attrs={'rows':5})
        }


