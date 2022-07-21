from datetime import datetime
from django.db.models import fields
from django.db.models.signals import pre_save

from django.forms import widgets

from .models import Attribute, AttributeValues, Banners, Category, Coupons, Email_Template, Product, User
from django.contrib.flatpages.models import FlatPage
from django import forms
from . import models
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


def validate_user_email(user, email):
    if models.User.objects.filter(username=user).exists():
        user = models.User.objects.get(username=user)
        return user.email == email
    else:
        return False

class LoginForm(forms.Form):
    required_css_class = 'required'
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))

    def clean_username(self):
        data = self.cleaned_data.get('username')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean_password(self):
        data = self.cleaned_data.get('password')
        if not data:
            raise ValidationError("This field is empty")
        return data

    # def clean(self):
    #     cleaned_data = super().clean()
    #     user = cleaned_data.get('username')
    #     pwd = cleaned_data.get('password')
    #     if user and pwd:
    #         if not validate_incorrect_password(user, pwd):
    #             raise ValidationError("Incorrect password")


class ResetPassword(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = User
        fields = ['username', 'email']
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))

    def clean_username(self):
        data = self.cleaned_data.get('username')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean(self):
        email = self.cleaned_data.get('email')
        user = self.cleaned_data.get('username')
        if user and email:
            if not validate_user_email(user, email):
                raise ValidationError('Invalid User')


class RecoverPasswordForm(forms.Form):
    required_css_class = 'required'
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    confirmPassword = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    def clean_password(self):
        data = self.cleaned_data.get('password')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean_confirmPassword(self):
        data = self.cleaned_data.get('confirmPassword')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirmPassword')
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("Password doesn't match")


class ChangePasswordForm(forms.Form):
    # required_css_class = 'required'
    oldPassword = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Old Password', 'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password', 'class': 'form-control'}))
    confirmPassword = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    def clean_oldPassword(self):
        data = self.cleaned_data.get('oldPassword')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean_password(self):
        data = self.cleaned_data.get('password')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean_confirmPassword(self):
        data = self.cleaned_data.get('confirmPassword')
        if not data:
            raise ValidationError("This field is empty")
        return data

    def clean(self):
        old_password = self.cleaned_data.get('oldPassword')
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirmPassword')
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError("Password doesn't match")
        if old_password and password:
            if old_password ==  password:
                raise ValidationError("Same old and new password")


class ProfileForm(forms.Form):
    required_css_class = 'required'
    username = forms.CharField(
        required=False,
        # disabled=True,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': '-', 'class': 'form-control'}))
    first_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'placeholder': '-', 'class': 'form-control'}))
    last_name = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'placeholder': '-', 'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '-'}))
    image = forms.ImageField(required=False)
    mobile_number = forms.CharField(
        max_length=10, required=False,
        widget=forms.TextInput(attrs={'placeholder': '-', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    def clean_mobile_number(self):
        data = self.cleaned_data.get('mobile_number')
        if data:
            if not (data.isdigit() and len(data) == 10):
                raise ValidationError("Not a valid mobile number")
        return data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if models.User.objects.filter(username=username).exists():
            if models.User.objects.get(username=username) != models.User.objects.get(username=self.user):
                raise ValidationError("Username already exists")
        return username

class CategoryForm(forms.ModelForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CategoryForm, self).__init__(*args, **kwargs)
        categories = [(None, '------')]
        for category in models.Category.objects.all():
            categories.append((category.id, self.parentCategory(category)))
        self.fields['parent_category'].choices = categories
        self.fields['active'].initial = True

    class Meta:
        model = models.Category
        exclude = ['slug', 'created_by', 'created_on', 'modified_on', 'modified_by']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-label'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-label'}),
            'parent_category': forms.Select(    attrs={'class': 'form-control form-label'}),
            'active': forms.CheckboxInput(attrs={'class': ' form-check form-label'}),
        }

    def parentCategory(self, obj):
        category = ''
        if obj.parent_category_id:
            cat = models.Category.objects.get(id=obj.parent_category_id)
            category = self.parentCategory(cat) + ' > ' + obj.name
        else:
            category = obj.name
        return category

    def save(self, commit=True):
        a = super(CategoryForm, self).save(commit=False)
        a.save(user=self.user)
        return a


class ProductForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Product
        exclude = ['created_by', 'created_on', 'modified_on']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product Name', 'class': 'form-control form-label'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description', 'class': 'form-control form-label'}),
            'category': forms.Select(attrs={'placeholder': 'Select Category', 'class': 'form-control form-label'}),
            'brand': forms.TextInput(attrs={'placeholder': 'Brand', 'class': 'form-control form-label'}),
            'quantity' : forms.NumberInput(attrs={'placeholder': 'Quantity', 'class': 'form-control form-label'}),
            'out_of_stock_status' : forms.CheckboxInput(attrs={'class': 'form-check form-label'}),
            'status' : forms.CheckboxInput(attrs={'class': ' form-check form-label'}),
            'shipping_required' : forms.CheckboxInput(attrs={'class': ' form-check form-label'}),
            # 'images' : forms.FileInput(attrs={'multiple': True, 'class': ''})
 }
    images = forms.ImageField(required=False, widget=forms.FileInput(attrs={'multiple': True, 'class': ''}))
    def __init__(self, *args, **kwargs):
        self.id = kwargs.pop('id', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        categories = [(None, '------')]
        for category in models.Category.objects.filter(parent_category_id = None):
            sub_cat = list(Category.objects.filter(parent_category_id=category.id).values_list("id", "name"))
            categories.append((category.name, sub_cat))
            # categories.append((category.id, self.parentCategory(category)))
        self.fields['category'].choices = categories
        self.fields['price'].widget.attrs['min'] = 2
        self.fields['price'].initial = 2
        # self.fields['quantity'].widget.attrs['min'] = 1
        self.fields['quantity'].initial = 1
        self.fields['out_of_stock_status'].initial = False
        self.fields['out_of_stock_status'].required = False
        self.fields['status'].required = False
        self.fields['shipping_required'].required = False

    price = forms.IntegerField(label_suffix=' (Dollars) :', widget=forms.NumberInput(attrs={'class': 'form-control form-label'}))
   
    def parentCategory(self, obj):
        category = ''
        if obj.parent_category_id:
            cat = models.Category.objects.get(id=obj.parent_category_id)
            category = self.parentCategory(cat) + ' > ' + obj.name
        else:
            category = obj.name
        return category

    def clean_name(self):
        data = self.cleaned_data.get('name')
        if not data:
            raise ValidationError("This field is empty")
        if (self.id == 0 and models.Product.objects.filter(name=data).exists()):
            raise ValidationError("Product already exists")

        if models.Product.objects.filter(name=data).exists():
            if self.id != 0 and (models.Product.objects.get(name=data) != models.Product.objects.get(id=self.id)):
                raise ValidationError('Product already exists')
        return data

    def clean(self):
        out_of_stock_status = self.cleaned_data.get('out_of_stock_status')
        quantity = self.cleaned_data.get('quantity')
        if out_of_stock_status and quantity > 0:
            raise ValidationError('Cannot enter quantity when out of stock status is True')
        return super().clean()


class AttributeGroupForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Attribute
        fields = ['name']
        widgets = {
            'name' : forms.TextInput(attrs={'class': 'form-control form-label'})
        }

    def clean(self):
        data = self.cleaned_data.get('name')
        if not data:
            raise ValidationError("This field is empty")
        if Attribute.objects.filter(name__iexact = data).exists():
            raise ValidationError('Attribute already exists.')         
        return super().clean()


class AttributeForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = AttributeValues
        fields = ['name', 'attribute']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-label'}),
            'attribute': forms.Select(attrs={'placeholder': 'Select Attribute Group', 'class': 'form-control form-label'})
        }
        
    def clean(self):
        name = self.cleaned_data.get('name')
        attribute = self.cleaned_data.get('attribute')
        if not name:
            raise ValidationError("This field is empty")
        if not attribute:
            raise ValidationError("This field is empty")
        if AttributeValues.objects.filter(
            name__iexact = name, 
            attribute = attribute).exists():
            raise ValidationError('This attribute value already exists.')
        return super().clean()


class ProductAttributes(forms.ModelForm):

    class Meta:

        model = models.Product_attribute_association
        exclude = ['product']
        # fields = ['attribute', 'value']
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-control form-label col-4 ml-2 mr-4'}),
            'value': forms.Select(attrs={'class': 'form-control form-label col-4 ml-2 mr-4'}),
            'DELETE': forms.CheckboxInput(attrs={'class': 'form-check ml-2 mr-4'})
        }


class CouponsForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Coupons
        exclude = ['created_by']

    choices = (
        (None, '---------'),
        (1, 'Percentage'),
        (2, 'Fixed Amount'),
    )
    name = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'placeholder': 'Coupon Name', 'class': 'form-control'}))
    code = forms.CharField(max_length=10, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Code name'}))
    type = forms.ChoiceField(choices=choices, widget=forms.Select(attrs={'class': 'form-control'}))
    discount = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'placeholder': 'Discount'}))
    total_amount = forms.IntegerField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter minimun amount that must be reached to use coupon'}))
    start_date = forms.DateTimeField(initial=datetime.now(
    ),  widget=forms.SelectDateWidget(attrs={'class': 'form-input col-3'}))
    end_date = forms.DateTimeField(initial=datetime.now(
    ), widget=forms.SelectDateWidget(attrs={'class': 'form-input col-3'}))
    uses_per_coupons = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    uses_per_customer = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # customer_login = forms.BooleanField(required=False,
    #     widget=forms.CheckboxInput(attrs={'class': 'form-check'}))
    free_shipping = forms.BooleanField(required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check'}))
    active = forms.BooleanField(required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check'}))

    def clean(self):
        type = self.cleaned_data.get('type')
        discount = self.cleaned_data.get('discount')
        if int(type) == 1:
            if discount > 99:
                raise ValidationError('Exceed discount percentage')
        elif int(type) == 2:
            total_amount = self.cleaned_data.get('total_amount')
            if discount > total_amount:
                raise ValidationError('Exceed total amount')
        return super().clean()


class ViewMessageForm(forms.Form):
    required_css_class = 'required'
    name = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'class':'form-control form-label'}), disabled=True, required=False)
    mail = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control form-label'}), disabled=True, required=False)
    # replied_on = forms.DateTimeField(, required=False)
    subject = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class':'form-control form-label'}), disabled=True, required=False)
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control form-label'}), disabled=True, required=False)
    reply = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control form-label'}), required=False)
    mailed_on = forms.DateTimeField(initial=datetime.now(), disabled=True, widget=forms.DateTimeInput(attrs={'class': 'form-control form-label'}), required=False)
    user_logged_in = forms.BooleanField(required=False, disabled=True,  widget=forms.CheckboxInput(attrs={'class': 'form-check form-label'}))


class EmailTemplateForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Email_Template
        exclude = ['created_by']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'code': forms.TextInput(attrs={'class':'form-control'}),
            'subject': forms.TextInput(attrs={'class':'form-control'}),
            'message' : forms.Textarea(attrs={'class':'form-control'})
        }
        
class OrderHistoryForm(forms.Form):
    required_css_class = 'required'
    choice = (
        (None, '--------'),
        ('Pending','Pending'),
        ('Order Placed','Order Placed'),
        ('Cancelled','Cancelled'),
        ('Complete','Complete'),
        ('Expired','Expired'),     
        ('Failed','Failed'),
        ('Processed','Processed'),
        ('Processing','Processing'),
        ('Refunded','Refunded'),
        ('Reversed','Reversed'),
        ('Shipped','Shipped'),
        )
    status = forms.ChoiceField(choices=choice, widget=forms.Select(attrs={'class':'form-control'}))


class ReportForm(forms.Form):
    required_css_class = 'required'
    choice = (
        (1,'Sales Report'),
        (2,'Customer Registered'),
        (3,'Coupon User'),
        )
    report_type = forms.ChoiceField(choices=choice,  widget=forms.Select(attrs={'class': 'form-control'}))


class SalesReportForm(forms.Form):
    required_css_class = 'required'
    groupby_choice = (
        (364, '365 Days'),
        (29, '30 Days'),
        (6, '7 Days'),
        (1, '1 day')
    )
    groupby = forms.ChoiceField(choices=groupby_choice, widget=forms.Select(attrs={'class': 'form-control'}))

class CMSForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = FlatPage
        fields =  ['url','title', 'content']
        widgets = {
            'url': forms.TextInput(attrs={'class':'form-control'}),
            'title': forms.TextInput(attrs={'class':'form-control'}),      
            'content': forms.Textarea(attrs={'class':'form-control'},),      
        }



class CustomerForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined', 'mobile_number']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control', 'disabled':True},),
            'first_name': forms.TextInput(attrs={'class':'form-control','disabled':True}),
            'last_name': forms.TextInput(attrs={'class':'form-control','disabled':True}),
            'email': forms.TextInput(attrs={'class':'form-control','disabled':True}),
            'is_active': forms.CheckboxInput(attrs={'class':'form-check','disabled':True}),
            'date_joined': forms.TextInput(attrs={'class':'form-control','disabled':True}),
            'mobile_number': forms.TextInput(attrs={'class':'form-control','disabled':True}),
        }
        
class BannerForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Banners
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'paragraph': forms.Textarea(attrs={'class': 'form-control'}),
            'link': forms.TextInput(attrs={'class':'form-control'})
        }