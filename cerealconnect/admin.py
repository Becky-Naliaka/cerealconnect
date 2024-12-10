from django.contrib import admin
from .models import Product, CartItem, Category
from .models import ContactMessage


# Custom ProductAdmin class to use ProductForm
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'seller')  # Specify fields to display


class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')  # Specify fields for CartItem admin view


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Specify fields for Category admin view


# Register models with the admin site
admin.site.register(Product, ProductAdmin)  # Register Product with the custom ProductAdmin
admin.site.register(CartItem, CartItemAdmin)  # Register CartItem with custom admin
admin.site.register(Category, CategoryAdmin)  # Register Category with custom admin


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'date_sent')  # Display name, email, and message in the list view
    search_fields = ('name', 'email', 'message')  # Allow searching by name, email, or message


admin.site.register(ContactMessage, ContactMessageAdmin)
