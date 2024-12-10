# from django.db import models
# from django import forms
# from django.conf import settings
# from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
# import os
# import requests
# from requests.auth import HTTPBasicAuth
# from django.contrib import admin, messages
# from django.contrib.auth.models import User
#
#
# # ----------------------- User Model and Manager ---------------------------- #
#
# # Custom User Manager
# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, username, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, email, username, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self.create_user(email, username, password, **extra_fields)
#
#
# # Custom User Model
# class CustomUser(AbstractUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=255, unique=True)
#     first_name = models.CharField(max_length=255, blank=True)
#     last_name = models.CharField(max_length=255, blank=True)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     date_joined = models.DateTimeField(auto_now_add=True)
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#
#     objects = CustomUserManager()
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']
#
#     def __str__(self):
#         return self.username
#
#
# # ----------------------- E-Commerce Models ---------------------------- #
#
# # ----------------------- E-Commerce Models ---------------------------- #
#
# class Category(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#
#     def __str__(self):
#         return self.name
#
#
# # class Product(models.Model):
# #     name = models.CharField(max_length=255)
# #     description = models.TextField()
# #     price = models.DecimalField(max_digits=10, decimal_places=2)
# #     image = models.ImageField(upload_to='product_images/', blank=True, null=True)
# #     category = models.ForeignKey(Category, on_delete=models.CASCADE)
# #     seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
# #
# #     def __str__(self):
# #         return self.name
#
# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     image = models.ImageField(upload_to='product_images/', null=True, blank=True)
#     # other fields...
#
#
# class ProductRating(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_ratings')
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_ratings')
#     rating = models.PositiveIntegerField(
#         choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ['product', 'user']
#
#
# class CartItem(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)  # No need for a string reference here
#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.quantity} x {self.product.name}"
#
#     def total_price(self):
#         return self.product.price * self.quantity
#
#
# class Cart(models.Model):  # Cart model added back here
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#
#     class Meta:
#         unique_together = ('user', 'product')
#
#     def __str__(self):
#         return f"{self.user.username} - {self.product.name} ({self.quantity})"
#
#
# class Order(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
#     products = models.ManyToManyField(Product, through='OrderItem')
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     status = models.CharField(
#         max_length=20,
#         choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Shipped', 'Shipped'), ('Completed', 'Completed')],
#         default='Pending'
#     )
#
#     def __str__(self):
#         return f"Order #{self.id} - {self.user.username}"
#
#
# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.product.name} - {self.quantity}"
#
#
# # ----------------------- Other Models ---------------------------- #
#
# class Testimony(models.Model):
#     author = models.CharField(max_length=100)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.author
#
#
# class Rating(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     rating = models.IntegerField()  # Example field for rating (e.g., 1 to 5)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user.username} rated {self.product.name} - {self.rating}"
#
#
# class Blog(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.title
#
#
# # ----------------------- Mpesa Models and Utils ---------------------------- #
#
# class MpesaAccessToken(models.Model):
#     validated_mpesa_access_token = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.validated_mpesa_access_token
#
#
# class LipanaMpesaPassword(models.Model):
#     business_short_code = models.CharField(max_length=50)
#     decode_password = models.CharField(max_length=255)
#     lipa_time = models.CharField(max_length=50)
#
#     def __str__(self):
#         return f"{self.business_short_code} - {self.decode_password}"
#
#
# class MpesaC2bCredential:
#     consumer_key = os.getenv('MPESA_CONSUMER_KEY', 'your_consumer_key_here')
#     consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', 'your_consumer_secret_here')
#     api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
#
#
# def get_mpesa_token():
#     credentials = MpesaC2bCredential()
#     response = requests.get(
#         credentials.api_url,
#         auth=HTTPBasicAuth(credentials.consumer_key, credentials.consumer_secret)
#     )
#     if response.status_code == 200:
#         return response.json().get('access_token', '')
#     return None
#
#
# # ----------------------- Forms ---------------------------- #
#
# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'price', 'category', 'seller', 'description']
#
#
# class ContactMessage(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     message = models.TextField()
#     date_sent = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Message from {self.name} ({self.email})"

from django.db import models
from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
import os
import requests
from requests.auth import HTTPBasicAuth
from django.contrib import admin, messages
from django.contrib.auth.models import User


# ----------------------- User Model and Manager ---------------------------- #

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


# ----------------------- E-Commerce Models ---------------------------- #

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_ratings')
    rating = models.PositiveIntegerField(
        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'user']


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Shipped', 'Shipped'), ('Completed', 'Completed')],
        default='Pending'
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


# ----------------------- Other Models ---------------------------- #

class Testimony(models.Model):
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author


class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Example field for rating (e.g., 1 to 5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rated {self.product.name} - {self.rating}"


class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# ----------------------- Mpesa Models and Utils ---------------------------- #

class MpesaAccessToken(models.Model):
    validated_mpesa_access_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.validated_mpesa_access_token


class LipanaMpesaPassword(models.Model):
    business_short_code = models.CharField(max_length=50)
    decode_password = models.CharField(max_length=255)
    lipa_time = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.business_short_code} - {self.decode_password}"


class MpesaC2bCredential:
    consumer_key = os.getenv('MPESA_CONSUMER_KEY', 'your_consumer_key_here')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', 'your_consumer_secret_here')
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'


def get_mpesa_token():
    credentials = MpesaC2bCredential()
    response = requests.get(
        credentials.api_url,
        auth=HTTPBasicAuth(credentials.consumer_key, credentials.consumer_secret)
    )
    if response.status_code == 200:
        return response.json().get('access_token', '')
    return None


# ----------------------- Forms ---------------------------- #

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'seller', 'description']


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
