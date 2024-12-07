# import requests
# from requests.auth import HTTPBasicAuth
# import json
# import base64
# from datetime import datetime
#
#
# # MPesa API credentials from your image
# class MpesaCredentials:
#     consumer_key = '7DSWGTLpj62y9wHo0ljQ5AkvGa0pXFmmGpJdeeWFF9RiGJrc'  # Consumer Key
#     consumer_secret = 'RWcJZnWOV7qQg5ebIEOvDPerZYbtXKeqImpWd8HIL4cSUWXMA0iYDdAOZy4t1XLk'  # Consumer Secret
#     api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'  # OAuth URL
#     business_short_code = '174379'  # Business Shortcode
#     pass_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey
#     phone_number = '254708374149'  # Example phone number (should be dynamic in real usage)
#     party_a = '600584'  # Party A (your shortcode for receiving payment)
#     party_b = '600000'  # Party B (MPesa's shortcode)
import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import json


class MpesaC2bCredential:
    """Class to hold Mpesa C2B credentials."""
    consumer_key = os.getenv('MPESA_CONSUMER_KEY', '7DSWGTLpj62y9wHo0ljQ5AkvGa0pXFmmGpJdeeWFF9RiGJrc')  # Use environment variables for security
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', 'RWcJZnWOV7qQg5ebIEOvDPerZYbtXKeqImpWd8HIL4cSUWXMA0iYDdAOZy4t1XLk')
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'


class MpesaAccessToken:
    """Class to fetch and store the Mpesa access token."""
    r = requests.get(MpesaC2bCredential.api_URL, auth=HTTPBasicAuth(
        MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]


class LipanaMpesaPpassword:
    """Class to handle STK Push password generation."""
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = "174379"  # Replace with your shortcode
    passkey = os.getenv('MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')  # Environment variable for passkey
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
