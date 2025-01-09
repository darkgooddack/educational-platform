from typing import Optional, Union, Any
from ..utils.logger import logger
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
import base64
from datetime import datetime, timedelta

SPECIAL_CHARACTERS: list[str] = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>']
pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/auth/login")  # The endpoint where the user can get a token

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def is_password_strong_enough(password: str) -> bool:
    """if len(password < 5):
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
    return base64.b85encode(string.encode('ascii')).decode('ascii')

def str_decode(string: str) -> str:
    return base64.b85decode(string.encode('ascii')).decode('ascii')

def get_token_payload(token: str, secret: str, algo: Union[str, list[str]]) -> Optional[dict[str, Any]]:
    try:
        payload = jwt.decode(token, secret, algorithms=algo)
    except Exception as jwt_exec:
        logger.info(f"JWT Error: {str(jwt_exec)}")
        payload = None
    return payload

def generate_token(payload: dict[str, Any], secret: str, algo: str, expiry: timedelta) -> str:
    expire = datetime.utcnow() + expiry
    payload.update({"exp": expire})
    return jwt.encode(payload, secret, algorithm=algo)
