import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import all_routers
from api.middlewares.logging import LoggingMiddleware
from api.core.config import app_config, env_config

app = FastAPI(**app_config.app_params)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware, **env_config.cors_params)
app.include_router(all_routers())

if __name__ == "__main__":
    uvicorn.run(app, **app_config.uvicorn_params)
