import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from registration_service.api.routers import all_routers
from registration_service.api.middlewares.logging import LoggingMiddleware
from registration_service.api.core.config import app_config, env_config

app = FastAPI(**app_config.app_params)
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware, **env_config.cors_params)
app.include_router(all_routers())

if __name__ == "__main__":
    uvicorn.run(app, **app_config.uvicorn_params)
