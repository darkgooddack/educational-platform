import secrets
from pydantic import BaseModel, HttpUrl, Field

class OAuthConfig(BaseModel):
    client_id: str
    client_secret: str
    auth_url: HttpUrl
    token_url: HttpUrl
    scope: str = ""

class OAuthParams(BaseModel):
    client_id: str
    redirect_uri: HttpUrl
    scope: str = ""
    response_type: str = "code"

class VKOAuthParams(OAuthParams):
    state: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    code_challenge: str
    code_challenge_method: str = "S256"
    v: str = "5.131"
