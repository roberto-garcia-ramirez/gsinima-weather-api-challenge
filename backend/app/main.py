from __future__ import annotations

import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints.weather import router as weather_router
from app.core.config import get_settings
from app.db.base_class import Base
from app.db.session import engine


logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting GS Inima Weather API")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured")
    yield
    logger.info("Shutting down GS Inima Weather API")


settings = get_settings()

app = FastAPI(title="GS Inima Weather API", lifespan=lifespan)

# Strict but direct CORS configuration to enable React/Vite communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global interceptor to force console capture of hidden exceptions
@app.middleware("http")
async def super_logger(request: Request, call_next):
    print(f"\n[INTERCEPTOR] Petición entrando a: {request.url}")
    try:
        return await call_next(request)
    except Exception as e:
        print("\n[INTERCEPTOR] BUG CAZADO:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": "Fallo interno", "detalle": str(e)})

app.include_router(weather_router, prefix="/api")
