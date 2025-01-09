from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
SPECIAL_CHARACTERS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>']

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def is_password_strong_enough(password: str) -> bool:
    """if len(password) < 5:
        return False
    
    if not any(char.isupper() for char in password):
        return False
    
    if not any(char.islower() for char in password):
        return False
    
    if not any(char.isdigit() for char in password):
        return False
    
    if not any(char in SPECIAL_CHARACTERS for char in password):
        return False"""
    
    return True

def str_encode(string: str) -> str:
    return base64.b85encode(string.encode('ascii').decode('ascii'))

def str_decode(string: str) -> str:
    return base64.b85decode(string.encode('ascii').decode('ascii'))

