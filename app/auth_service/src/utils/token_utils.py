import jwt
from ..utils.logger import logger

async def get_token_payload(token: str, secret: str, algo: str):
    try:
        payload = jwt.decode(token, secret, algorithms=[algo])
    except Exception as jwt_exec:
        logger.info(f"JWT Error: {str(jwt_exec)}")
        payload = None
    return payload