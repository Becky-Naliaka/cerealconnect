from django.contrib import admin
from .models import Product, CartItem, Category
from .forms import ProductForm


# Custom ProductAdmin class to use ProductForm
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm


# Register models with the admin site
admin.site.register(Product, ProductAdmin)  # Register Product with the custom ProductAdmin
admin.site.register(CartItem)  # Register CartItem without a custom admin
admin.site.register(Category)  # Register Category without a custom admin
