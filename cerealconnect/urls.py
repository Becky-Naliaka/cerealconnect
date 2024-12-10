from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = "cerealconnect"

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('blog/', views.blog, name='blog'),
    path('testimonies/', views.testimonies, name='testimonies'),
    path('shop/', views.shop, name='shop'),
    path('add-product/', views.add_product, name='add-product'),
    path('product/<int:product_id>/', views.product_detail, name='product-detail'),
    path('register/', views.register, name='user-registration'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='user-login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='user-logout'),
    path('my_products/', views.my_products, name='my_products'),
    path('update-product/<int:id>/', views.update_product, name='update-product'),
    path('products/', views.product_detail, name='products-view'),
    path('browse-products/', views.browse_products, name='browse-products'),
    path('browse-category/<str:category_name>/', views.browse_by_category, name='browse-by-category'),
    path('search/', views.search, name='search'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('view-cart/', views.view_cart, name='view-cart'),
    path('delete-from-cart/<str:item_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('pay/', views.pay, name='pay'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('payment-failure/', views.payment_failure, name='payment-failure'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('token/', views.token, name='token'),
    path('stk', views.stk, name='stk'),
    path('rate-product/<int:product_id>/', views.rate_product, name='rate-product'),
    path('contact/', views.contact, name='contact'),
]



