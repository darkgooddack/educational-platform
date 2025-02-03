"""
Пакет схем данных.

Предоставляет единую точку доступа ко всем Pydantic схемам.
"""

from .v1.auth.auth import AuthSchema, TokenSchema
from .v1.auth.register import RegistrationResponseSchema, RegistrationSchema
from .v1.base import (BaseInputSchema, BaseResponseSchema, BaseSchema,
                      CommonBaseSchema, ErrorResponseSchema,
                      ItemResponseSchema, ListResponseSchema)
from .v1.feedbacks.feedbacks import (FeedbackCreateSchema, FeedbackResponse,
                                     FeedbackSchema, FeedbackStatus,
                                     FeedbackUpdateSchema)
from .v1.oauth.oauth import (GoogleUserData, OAuthConfig, OAuthParams,
                             OAuthProvider, OAuthProviderResponse,
                             OAuthResponse, OAuthTokenParams, OAuthUserData,
                             OAuthUserSchema, VKOAuthParams, VKUserData,
                             YandexUserData)
from .v1.pagination import Page, PaginationParams
from .v1.content import ContentType
from .v1.users.users import (ManagerSelectSchema, UserCredentialsSchema,
                             UserResponseSchema, UserRole, UserSchema,
                             UserUpdateSchema)
from .v1.videos.videos import VideoLectureResponseSchema, VideoLectureSchema, VideoLectureCreateSchema
from .v1.tests.tests import QuestionType
from .v1.posts.posts import PostStatus
__all__ = [
    "BaseSchema",
    "BaseInputSchema",
    "CommonBaseSchema",
    "BaseResponseSchema",
    "ErrorResponseSchema",
    "ItemResponseSchema",
    "ListResponseSchema",
    "PaginationParams",
    "Page",
    "OAuthUserSchema",
    "OAuthResponse",
    "OAuthConfig",
    "OAuthParams",
    "OAuthProvider",
    "OAuthProviderResponse",
    "OAuthTokenParams",
    "VKOAuthParams",
    "RegistrationSchema",
    "RegistrationResponseSchema",
    "UserSchema",
    "UserCredentialsSchema",
    "UserUpdateSchema",
    "ManagerSelectSchema",
    "UserResponseSchema",
    "TokenSchema",
    "UserRole",
    "AuthSchema",
    "OAuthUserData",
    "YandexUserData",
    "GoogleUserData",
    "VKUserData",
    "FeedbackStatus",
    "FeedbackSchema",
    "FeedbackCreateSchema",
    "FeedbackUpdateSchema",
    "FeedbackResponse",
    "VideoLectureSchema",
    "VideoLectureCreateSchema",
    "VideoLectureResponseSchema",
    "ContentType",
    "PostStatus",
    "QuestionType"
]
