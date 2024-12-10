import json
import datetime
from datetime import timedelta
from decimal import Decimal
import requests
from requests.auth import HTTPBasicAuth
from django.http import HttpResponseNotAllowed
# from .mpesa_integration import get_mpesa_token
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from datetime import datetime
import base64
from .models import ContactMessage
from .models import Product, ProductRating
from django.db.models import Avg
from .forms import RatingForm

from collections import defaultdict

from . import models
from .models import (
    Product, Category, Rating, MpesaAccessToken,
    LipanaMpesaPassword, Testimony, get_mpesa_token, Cart, CartItem
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
#
# def shop(request):
#     # Group products by category
#     products_by_category = {}
#     products = Product.objects.all()
#
#     # Group products by category
#     for product in products:
#         category = product.category.name  # Assuming 'category' is a ForeignKey, 'name' is its attribute
#         if category not in products_by_category:
#             products_by_category[category] = []
#         products_by_category[category].append(product)
#
#     return render(request, 'shop.html', {'products_by_category': products_by_category})
def shop(request):
    query = request.GET.get('query', '')

    if query:
        # Perform case-insensitive search by name, description, etc.
        products = Product.objects.filter(name__icontains=query)
    else:
        # If no query, show all products
        products = Product.objects.all()

    # Group products by category
    products_by_category = {}
    for product in products:
        category = product.category.name  # assuming the product has a category
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)

    return render(request, 'shop.html', {
        'products_by_category': products_by_category,
        'query': query
    })


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


# def product_detail(request, product_id):
#     """Displays product details and allows users to rate it."""
#     product = get_object_or_404(Product, id=product_id)
#     ratings = Rating.objects.filter(product=product)
#
#     if request.method == 'POST':
#         rating_form = RatingForm(request.POST)
#         if rating_form.is_valid():
#             rating = rating_form.save(commit=False)
#             rating.product = product
#             rating.user = request.user
#             rating.save()
#             messages.success(request, "Rating submitted successfully!")
#             return redirect('product-detail', product_id=product.id)
#     else:
#         rating_form = RatingForm()
#
#     return render(request, 'product_detail.html', {
#         'product': product,
#         'ratings': ratings,
#         'rating_form': rating_form,
#     })


def add_rating(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        rating_value = int(request.POST['rating'])
        Rating.objects.create(product=product, user=request.user, rating=rating_value)
        return redirect('product_detail', product_id=product_id)


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
    product = Product.objects.get(id=product_id)
    quantity = int(request.POST.get('quantity', 1))  # Default to 1 if no quantity is provided
    cart = request.session.get('cart', {})

    # Convert Decimal price to float before adding to the session
    price = float(product.price)  # Ensure the price is a float

    if product_id in cart:
        cart[product_id]['quantity'] += quantity  # Increase the quantity if already in the cart
    else:
        cart[product_id] = {
            'name': product.name,
            'price': price,  # Store the price as a float
            'quantity': quantity,
        }

    # Update the session with the cart
    request.session['cart'] = cart
    messages.success(request, f"Added {quantity} {product.name} to your cart")
    return redirect('cerealconnect:shop')


def view_cart(request):
    """Displays the user's cart and total price."""
    cart = request.session.get('cart', {})
    total_price = calculate_total(cart)

    return render(request, 'view-cart.html', {
        'cart': cart,
        'total_price': total_price,
    })


def calculate_total(cart):
    """Calculates the total price of the items in the cart."""
    total_price = Decimal('0.00')
    for item in cart.values():
        total_price += Decimal(item['price']) * item['quantity']
    return total_price


@login_required
def update_cart(request):
    """Updates the quantities of items in the cart."""
    if request.method == "POST":
        cart = request.session.get('cart', {})
        for item_id, quantity in request.POST.items():
            if item_id in cart:
                try:
                    new_quantity = int(quantity)
                    if new_quantity > 0:
                        cart[item_id]['quantity'] = new_quantity
                    else:
                        messages.error(request, "Quantity must be at least 1.")
                except ValueError:
                    messages.error(request, "Invalid quantity entered.")
        request.session['cart'] = cart  # Save updated cart
        messages.success(request, "Cart updated successfully!")
        return redirect('cerealconnect:view_cart')
    return redirect('cerealconnect:shop')


@login_required
def delete_from_cart(request, item_id):
    """Deletes an item from the user's cart."""
    cart = request.session.get('cart', {})
    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart  # Save updated cart
        messages.success(request, "Item removed from cart.")
    else:
        messages.error(request, "Item not found in cart.")
    return redirect('cerealconnect:view-cart')


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


# Other M-Pesa functions like pay and mpesa_callback should use get_valid_access_token() as required.


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


# Checkout
def checkout(request):
    # Logic for displaying the checkout page
    return render(request, 'checkout.html')


# Payment Success
def payment_success(request):
    # Logic for displaying the success page after payment
    return render(request, 'payment_success.html')


# Payment Failure
def payment_failure(request):
    # Logic for displaying the failure page after payment
    return render(request, 'payment_failure.html')


def confirmation(request):
    # Logic for confirming the order
    return render(request, 'confirmation.html')


@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            # Parse the JSON response
            result_code = data['Body']['stkCallback']['ResultCode']
            result_description = data['Body']['stkCallback']['ResultDesc']

            # You can log this data or update your database accordingly
            if result_code == 0:
                # Payment successful
                return JsonResponse({"message": "Payment processed successfully!"})
            else:
                # Payment failed
                return JsonResponse({"error": result_description}, status=400)

        except KeyError as e:
            return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
    return HttpResponseNotAllowed(["POST"])


#
# def rate_product(request, product_id):
#     product = Product.objects.get(id=product_id)
#
#     # Ensure user is authenticated
#     if not request.user.is_authenticated:
#         messages.error(request, 'You need to be logged in to rate a product.')
#         return redirect('login')  # Redirect to login page if not authenticated
#
#     # Check if the user has already rated the product
#     if ProductRating.objects.filter(product=product, user=request.user).exists():
#         messages.error(request, 'You have already rated this product.')
#         return redirect('product-detail', product_id=product.id)
#
#     if request.method == 'POST':
#         rating = int(request.POST['rating'])
#
#         # Save the rating
#         ProductRating.objects.create(
#             product=product,
#             user=request.user,
#             rating=rating
#         )
#
#         # Calculate the average rating
#         average_rating = product.ratings.all().aggregate(models.Avg('rating'))['rating__avg']
#         product.average_rating = average_rating
#         product.save()
#
#         messages.success(request, 'Thank you for your rating!')
#         return redirect('product-detail', product_id=product.id)
#
#     return render(request, 'product_detail.html', {'product': product})
def rate_product(request, product_id):
    product = Product.objects.get(id=product_id)

    # Calculate the average rating for the product
    average_rating = ProductRating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']

    context = {
        'product': product,
        'average_rating': average_rating
    }

    return render(request, 'product_detail.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get all ratings for this product
    ratings = ProductRating.objects.filter(product=product)

    # Calculate the average rating for the product
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] if ratings.exists() else None

    # Handle form submission (rating)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.product = product
            rating.user = request.user
            rating.save()
            return redirect('product_detail', product_id=product.id)  # Avoid resubmission
    else:
        form = RatingForm()  # Initialize the form for GET requests

    context = {
        'product': product,
        'ratings': ratings,
        'average_rating': average_rating,
        'form': form,
        'total_ratings': ratings.count()
    }

    return render(request, 'product_detail.html', context)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save the contact message to the database
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )

        # Return a JSON response to the frontend
        return JsonResponse({'success': 'Your message has been sent successfully!'})

    return render(request, 'contact.html')


def token():
    # Generate and return the access token
    consumer_key = '7DSWGTLpj62y9wHo0ljQ5AkvGa0pXFmmGpJdeeWFF9RiGJrc'
    consumer_secret = 'RWcJZnWOV7qQg5ebIEOvDPerZYbtXKeqImpWd8HIL4cSUWXMA0iYDdAOZy4t1XLk'
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    response = requests.get(api_url, auth=requests.auth.HTTPBasicAuth(consumer_key, consumer_secret))
    token_data = response.json()
    return token_data.get('access_token')


# Function to handle STK Push request
def pay(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        # Check if both phone and amount are provided
        if not phone or not amount:
            messages.error(request, "Phone number and amount are required.")
            return redirect('cerealconnect:pay')

        # Validate and format the phone number
        try:
            phone = format_phone_number(phone)
        except ValueError as e:
            messages.error(request, f"Invalid phone number: {e}")
            return redirect('cerealconnect:pay')

        # Fetch the access token
        access_token = get_access_token()
        if not access_token:
            messages.error(request, "Failed to retrieve access token. Please try again.")
            return redirect('cerealconnect:pay')

        # Safaricom API endpoint and headers
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}

        # Generate timestamp and password
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_code = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        password = base64.b64encode(f"{short_code}{passkey}{timestamp}".encode()).decode()

        # STK Push payload
        payload = {
            "BusinessShortCode": short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://your-domain.com/payment-callback",  # Replace with live callback URL
            "AccountReference": "CerealConnect",
            "TransactionDesc": "Payment for goods"
        }

        # Send STK Push request
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("ResponseCode") == "0":
                    messages.success(request, "Payment request sent. Please complete the transaction on your phone.")
                else:
                    error_message = response_data.get("errorMessage", "Unknown error occurred.")
                    messages.error(request, f"Error: {error_message}")
            else:
                messages.error(request, f"Failed to send STK Push request. Status code: {response.status_code}")
                print(f"Error details: {response.text}")
        except Exception as e:
            messages.error(request, f"An error occurred during payment processing: {e}")

        return redirect('cerealconnect:pay')

    return render(request, 'pay.html')


def get_access_token():
    """
    Fetches the access token from Safaricom API.
    """
    consumer_key = '7DSWGTLpj62y9wHo0ljQ5AkvGa0pXFmmGpJdeeWFF9RiGJrc'
    consumer_secret = 'RWcJZnWOV7qQg5ebIEOvDPerZYbtXKeqImpWd8HIL4cSUWXMA0iYDdAOZy4t1XLk'
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    try:
        response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
        else:
            print(f"Error fetching access token: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Exception during token retrieval: {e}")
        return None


# Function to handle payment callback
def payment_callback(request):
    if request.method == "POST":
        payment_data = request.POST
        print("Callback data:", payment_data)
        if payment_data.get("Status") == "Success":
            return JsonResponse({"message": "Payment successful!"})
        else:
            return JsonResponse({"message": "Payment failed!"})
    return JsonResponse({"error": "Invalid request"}, status=400)


def stk(request):
    return render(request, 'pay.html', {'navbar': 'stk'})


def format_phone_number(phone):
    """
    Formats the phone number to the required 2547XXXXXXXX format.
    """
    if phone.startswith("0"):
        return "254" + phone[1:]  # Replace leading 0 with 254
    elif phone.startswith("+"):
        return phone[1:]  # Remove leading +
    elif phone.startswith("254"):
        return phone  # Already in the correct format
    else:
        raise ValueError("Invalid phone number format.")


from django.core.mail import send_mail


def send_contact_email(name, email, message):
    subject = f"Contact Form Submission from {name}"
    message_body = f"Message: {message}\n\nFrom: {name}\nEmail: {email}"
    send_mail(
        subject,
        message_body,
        'your_email@example.com',  # DEFAULT_FROM_EMAIL
        ['recipient@example.com'],  # Replace with your recipient email
        fail_silently=False,
    )


def my_custom_admin_view(request):
    # Perform your logic here
    success = True  # Example: Result of some logic
    if success:
        messages.success(request, "Your operation was successful!")
    else:
        messages.error(request, "Something went wrong.")

    return redirect('admin:index')
