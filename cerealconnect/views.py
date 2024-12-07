
import base64
import json
from datetime import timedelta
from decimal import Decimal
import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from collections import defaultdict

from . import models
from .models import (
    Product, Category, Rating, MpesaAccessToken,
    LipanaMpesaPpassword, Testimony
)
from .forms import ProductForm, ContactForm, RatingForm


# ========== Home and Static Pages ==========

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def blog(request):
    return render(request, 'blog.html')


def testimonies(request):
    """Displays user testimonies."""
    testimonies_list = Testimony.objects.all().order_by('-created_at')  # Order by creation date
    return render(request, 'testimonies.html', {'testimonies': testimonies_list})


# ========== Shop and Products ==========

def shop(request):
    # Group products by category
    products_by_category = {}
    products = Product.objects.all()

    # Group products by category
    for product in products:
        category = product.category.name  # Assuming 'category' is a ForeignKey, 'name' is its attribute
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)

    return render(request, 'shop.html', {'products_by_category': products_by_category})


def add_product(request):
    """Allows sellers to add new products."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # Assign the current user as the seller
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('shop')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


def product_detail(request, product_id):
    """Displays product details and allows users to rate it."""
    product = get_object_or_404(Product, id=product_id)
    ratings = Rating.objects.filter(product=product)

    if request.method == 'POST':
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.product = product
            rating.user = request.user
            rating.save()
            messages.success(request, "Rating submitted successfully!")
            return redirect('product-detail', product_id=product.id)
    else:
        rating_form = RatingForm()

    return render(request, 'product_detail.html', {
        'product': product,
        'ratings': ratings,
        'rating_form': rating_form,
    })


# ========== User Authentication ==========

def register(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
            return redirect('user-login')
    else:
        form = UserCreationForm()
    return render(request, 'registration.html', {'form': form})


def user_login(request):
    """Handles user login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid login credentials.")
    return render(request, 'login.html')


def user_logout(request):
    """Logs out the user."""
    logout(request)
    return redirect('home')


# ========== Cart and Checkout ==========

def add_to_cart(request, product_id):
    """Adds a product to the user's cart."""
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})
    if str(product.id) in cart:
        cart[str(product.id)]['quantity'] += 1
    else:
        cart[str(product.id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
        }

    request.session['cart'] = cart
    return redirect('cerealconnect:view-cart')  # Correct namespace



def view_cart(request):
    """Displays the user's cart and total price."""
    cart = request.session.get('cart', {})
    total_price = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

    return render(request, 'view-cart.html', {'cart': cart, 'total_price': total_price})


@login_required
def update_cart(request):
    """Updates the quantities of items in the cart."""
    if request.method == "POST":
        quantities = request.POST.get("quantities", {})
        cart = request.session.get("cart", {})

        for item_id, quantity in quantities.items():
            if item_id in cart:
                cart[item_id]["quantity"] = int(quantity)

        request.session["cart"] = cart
        return redirect("view-cart")
    return redirect("shop")


@login_required
def delete_from_cart(request, item_id):
    """Deletes an item from the user's cart."""
    cart = request.session.get("cart", {})
    if item_id in cart:
        del cart[item_id]
        request.session["cart"] = cart
    return redirect("view-cart")


# ========== Payment and M-Pesa Integration ==========

def generate_access_token():
    """Generates and saves M-Pesa access token."""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        MpesaAccessToken.objects.create(
            validated_mpesa_access_token=access_token,
            created_at=now()
        )
    else:
        raise Exception(f"Failed to generate access token: {response.json()}")


def get_valid_access_token():
    """Retrieves a valid M-Pesa access token."""
    token = MpesaAccessToken.objects.first()
    if token and token.created_at + timedelta(seconds=3600) > now():
        return token.validated_mpesa_access_token
    else:
        generate_access_token()
        return MpesaAccessToken.objects.first().validated_mpesa_access_token


# Other M-Pesa functions like `pay` and `mpesa_callback` should use `get_valid_access_token()` as required.


def my_products(request):
    """Displays products added by the current logged-in seller."""
    products = Product.objects.filter(seller=request.user)
    return render(request, 'my_products.html', {'products': products})


def update_product(request, id):
    """Allows a seller to update their product."""
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('my_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'update-product.html', {'form': form})


def delete_product(request, id):
    """Allows a seller to delete their product."""
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('my_products')


def browse_products(request):
    """Displays all products available for browsing."""
    products = Product.objects.all()
    return render(request, 'browse-products.html', {'products': products})


def browse_by_category(request, category_name):
    """Displays products filtered by category."""
    category = get_object_or_404(Category, name=category_name)
    products = Product.objects.filter(category=category)
    return render(request, 'browse_category.html', {'category': category, 'products': products})


def search(request):
    """Searches for products based on a query."""
    if 'q' in request.GET:
        query = request.GET['q']
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()


from django.shortcuts import render
from django.http import HttpResponse


# Checkout
def checkout(request):
    # Logic for displaying the checkout page
    return render(request, 'checkout.html')


# Payment Status and Mpesa Integration

# Pay
def pay(request):
    # Logic for initiating the payment process
    return render(request, 'pay.html')


# Payment Success
def payment_success(request):
    # Logic for displaying the success page after payment
    return render(request, 'payment_success.html')


# Payment Failure
def payment_failure(request):
    # Logic for displaying the failure page after payment
    return render(request, 'payment_failure.html')


# Confirmation
def confirmation(request):
    # Logic for confirming the order
    return render(request, 'confirmation.html')


# Mpesa Callback
def mpesa_callback(request):
    # Logic for handling the Mpesa callback
    return HttpResponse('MPESA Callback received')


# Mpesa Token
def token(request):
    # Logic for generating the Mpesa token
    return HttpResponse('Mpesa Token')


# Daraja STK Push
def stk(request):
    # Logic for initiating the STK push to Daraja API
    return HttpResponse('STK Push')


# User Ratings
def ratings(request):
    # Logic for handling user ratings
    return render(request, 'ratings.html')


# Contact Page
def contact(request):
    # Logic for displaying the contact form
    return render(request, 'contact.html')



