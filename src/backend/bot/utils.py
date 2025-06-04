from django.contrib.auth.hashers import make_password, check_password
import jwt
from datetime import datetime, timedelta
from django.conf import settings

SECRET_KEY = settings.SECRET_KEY
def create_jwt_token(user):
    payload = {
        'id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=1),  # Expiry time (1 hour)
        'iat': datetime.utcnow(),  # Issued at time
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def hash_password(password: str) -> str:
    return make_password(password)

def verify_password(raw_password: str, hashed_password: str) -> bool:
    return check_password(raw_password, hashed_password)
