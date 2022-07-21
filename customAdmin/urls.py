# from django.conf.urls import include, url
from django.urls import path

from customAdmin import banners, cms, customers, orders, views, login, password, category, products, attributes, contact, coupons, reports

app_name = 'admin'
urlpatterns = [
    path('unauthorized-user/', login.Unauth.as_view(), name='unauthorized'),
    path('', login.LoginView.as_view(), name='login'),
    # Dashboard
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    #  Password change without login
    path('reset/', password.PasswordReset.as_view(), name='reset'),
    path('recover/<token>/', password.RecoverPassword.as_view(), name='recover' ),
    path('change/', views.ChangePassword.as_view(), name='change'),
    path('logout/', login.LogoutView.as_view(), name='logout'),
    # Profile 
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # Category
    path('category/', category.CategoryView.as_view(), name='category'),
    path('category/add/', category.AddCategoryView.as_view(), name='add_category'),
    path('category/<int:pk>/update/', category.EditCategoryView.as_view(), name='edit_category'),
    # Products
    path('products/', products.ProductView.as_view(), name='products'),
    path('products/add/', products.AddProduct.as_view(), name='add_product'),
    path('products/<pk>/update/', products.EditProduct.as_view(), name='edit_product'),
    path('products/<pk>/update/delete-image/<id>', products.DeleteImage.as_view(), name='delete_image'),
    path(r'^attribute-value/$', products.AttributeValueChange.as_view(), name='attribute_value'),
    path(r'^delete-attribute/$', products.DeleteAtrribute.as_view(), name='delete_attribute'),
    # url(r'^products/add/attribute-value/$', products.AttributeValueChange.as_view(), name='attribute_value'),
    # Attributs
    path('attribute-groups/', attributes.AttributeGroup.as_view(), name="attribute_group"),
    path('attribute-groups/add/', attributes.AddAttributeGroup.as_view(), name='add_attribute_group'),
    path('attribute-groups/<pk>/update/', attributes.EditAttributeGroup.as_view(), name='edit_attribute_group'),
    path('attribute/', attributes.AttributeValue.as_view(), name="attribute"),
    path('attribute/add/', attributes.AddAttribute.as_view(), name='add_attribute'),
    path('attribute/<pk>/update/', attributes.EditAttribute.as_view(), name='edit_attribute'),
    # Customers
    path('customer/', attributes.AttributeValue.as_view(), name="customer"),
    path('customer-groups/', attributes.AddAttribute.as_view(), name='customer_group'),
    # Coupons
    path('coupons/', coupons.CouponsView.as_view(), name='coupons'),
    path('coupons/add/', coupons.AddCouponsView.as_view(), name='add_coupon'),
    path('coupons/<pk>/update/', coupons.EditCoupons.as_view(), name='edit_coupon'),
    # Contact us
    path('mails/', contact.MailView.as_view(), name='mails'),
    path('mails/view/<pk>', contact.ViewMail.as_view(), name='view_mails'),
    #  Orders
    path('orders/', orders.OrderView.as_view(), name='orders'),
    path('orders/view/<id>/', orders.OrderDetailView.as_view(), name='order_details'),
    # Email-templates
    path('templates/', contact.EmailTemplate.as_view() ,name='email_templates'),
    path('templates/add/', contact.AddEmailTemplate.as_view(), name='add_template'),
    path('templates/<pk>/update/', contact.EditEmailTemplate.as_view(), name='edit_template'),
    #reports
    path('reports/', reports.Report.as_view(), name='reports'),
    path('reports/sales/', reports.SalesReport.as_view(), name='sales_report'),
    path('reports/cutomers/', reports.CustomerReport.as_view(), name='customers_report'),
    path('reports/coupons/', reports.CouponReport.as_view(), name='coupons_report'),
    # cms
    path('cms/', cms.CMSView.as_view() , name='cms'),  
    path('cms/<pk>/update/', cms.EditCMS.as_view() , name='edit_cms'),  
    path('cms/add/', cms.AddCMS.as_view() , name='add_cms'),  
    # customers
    path('customers/', customers.CustomerView.as_view(), name='customers'),
    path('customers/view/<pk>', customers.CustomerDetails.as_view(), name='view_customer'),
    # Banners
    path('banners/', banners.BannerView.as_view(), name='banners'),
    path('banners/add/', banners.AddBanners.as_view(), name='add_banners'),
    path('banners/<pk>/update/', banners.EditBanners.as_view(), name='edit_banners'),
 ]