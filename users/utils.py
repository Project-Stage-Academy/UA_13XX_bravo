import time
import base64
import os
from argon2 import PasswordHasher
from django.contrib.auth import get_user_model

User = get_user_model()
ph = PasswordHasher()
TOKEN_EXPIRATION = 3600

def generate_verification_token(user):
    """
    Generates a token for email verification.
    """
    user_id = str(user.id)
    timestamp = str(int(time.time()))
    salt = os.urandom(16)

    raw_token = f"{user_id}:{timestamp}".encode()
    hashed_token = ph.hash(raw_token + salt)

    token = base64.urlsafe_b64encode(f"{user_id}:{timestamp}:{hashed_token}:{salt.hex()}".encode()).decode()

    return token

def verify_token(token):
    """
    Verifies the verification token and returns the user if the token is valid.
    """
    try:
        decoded_data = base64.urlsafe_b64decode(token).decode()
        user_id, timestamp, hashed_token, salt = decoded_data.split(":")
        salt = bytes.fromhex(salt)

        if int(time.time()) - int(timestamp) > TOKEN_EXPIRATION:
            return None

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

        raw_token = f"{user.id}:{timestamp}".encode()
        if ph.verify(hashed_token, raw_token + salt):
            return user

    except Exception:
        return None

    return None
