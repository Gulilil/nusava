from django.contrib.auth.hashers import make_password, check_password
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import requests
import tempfile
from pathlib import Path
from typing import Optional
import os

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


def download_image_from_url(url: str, filename: Optional[str] = None) -> Path:
    """
    Download image from URL to temporary file for Instagram posting
    
    Parameters
    ----------
    url: str
        Cloudinary or any image URL
    filename: str, optional
        Custom filename, if None will generate from URL
        
    Returns
    -------
    Path
        Path to temporary file
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Get file extension from URL or content-type
    if filename:
        file_ext = Path(filename).suffix
    else:
        content_type = response.headers.get('content-type', '')
        if 'jpeg' in content_type or 'jpg' in content_type:
            file_ext = '.jpg'
        elif 'png' in content_type:
            file_ext = '.png'
        elif 'webp' in content_type:
            file_ext = '.webp'
        else:
            file_ext = '.jpg'  # default
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=file_ext,
        prefix='instagram_post_'
    )
    
    # Download and save
    with open(temp_file.name, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return Path(temp_file.name)

def cleanup_temp_file(file_path: Path):
    """Clean up temporary file after posting"""
    try:
        if file_path.exists():
            os.unlink(file_path)
    except Exception as e:
        print(f"Error cleaning up temp file: {e}")