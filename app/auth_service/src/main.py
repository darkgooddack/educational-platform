from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.exceptions import AppException
from .core.exceptions_handler import app_exceptions_handler
from .api.routes import auth

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.auth_router)
app.add_exception_handler(AppException, app_exceptions_handler)
