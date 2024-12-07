from . import views
from django.urls import path
from cerealconnect import views
from django.contrib.auth import views as auth_views
app_name = "cerealconnect"
urlpatterns = [
    # Home and basic pages
    path('', views.home, name='home'),  # Home page
    path('about/', views.about, name='about'),  # About page
    path('blog/', views.blog, name='blog'),  # Blog page
    path('testimonies/', views.testimonies, name='testimonies'),  # Testimonies page

    # Product pages
    path('shop/', views.shop, name='shop'),  # Shop page (list of products)
    path('add-product/', views.add_product, name='add-product'),  # Add a new product
    path('product/<int:product_id>/', views.product_detail, name='product-detail'),  # Product details page

    # User authentication
    path('register/', views.register, name='user-registration'),  # User registration page
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='user-login'),  # Login page
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='user-logout'),  # Logout page

    # Seller's product management
    path('my_products/', views.my_products, name='my_products'),  # View seller's products
    path('update-product/<int:id>/', views.update_product, name='update-product'),  # Update product details
    path('delete-product/<int:id>/', views.delete_product, name='delete-product'),  # Delete a product

    # Product browsing and search
    path('products/', views.product_detail, name='products-view'),  # Public view of all products
    path('browse-products/', views.browse_products, name='browse-products'),  # Browse products
    path('browse-category/<str:category_name>/', views.browse_by_category, name='browse-by-category'),  # Browse by category
    path('search/', views.search, name='search'),

    # Cart and checkout pages
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add-to-cart'),  # Add product to cart
    path('update-cart/', views.update_cart, name='update_cart'),
    path('delete-from-cart/<str:item_id>/', views.delete_from_cart, name='delete_from_cart'),

    path('view-cart/', views.view_cart, name='view-cart'),  # View the shopping cart
    # path('admin/cart/', views.admin_cart, name='admin-cart'),  # Admin cart view (optional)
    path('checkout/', views.checkout, name='checkout'),  # Checkout process

    # Payment status and Mpesa integration
    path('pay/', views.pay, name='pay'),
    path('payment-success/', views.payment_success, name='payment-success'),  # Payment success page
    path('payment-failure/', views.payment_failure, name='payment-failure'),  # Payment failure page
    path('confirmation/', views.confirmation, name='confirmation'),
    # path('lipa-na-mpesa/', views.lipa_na_mpesa, name='lipa_na_mpesa'),  # Initiate Mpesa payment
    path('mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),  # Mpesa callback URL
    path('token/', views.token, name='token'),  # Mpesa token URL (if needed)
    path('daraja/stk', views.stk, name="stk"),

    # User ratings
    path('ratings/', views.ratings, name='ratings'),  # User ratings page

    # Contact page
    path('contact/', views.contact, name='contact'),  # Contact form page
]


