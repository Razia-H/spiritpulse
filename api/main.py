import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from api.database import check_connection
from api.models import HealthOut
from api.routers import brands, sentiment, trends

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("spiritpulse.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SpiritPulse API starting up...")
    db_ok = await check_connection()
    if db_ok:
        logger.info("Database connection established")
    else:
        logger.error("Database connection FAILED")
    yield
    logger.info("SpiritPulse API shutting down...")


app = FastAPI(
    title="SpiritPulse API",
    description="Alcohol Industry Social Analytics Pipeline",
    version="1.0.0",
    contact={"name": "Razia H", "url": "https://github.com/Razia-H"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router)
app.include_router(sentiment.router)
app.include_router(trends.router)

app.mount("/static", StaticFiles(directory="dashboard"), name="static")


@app.get("/dashboard", include_in_schema=False)
async def dashboard():
    return FileResponse("dashboard/index.html")


@app.get("/", include_in_schema=False)
async def root():
    return {
        "project": "SpiritPulse",
        "description": "Alcohol industry social analytics pipeline",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "endpoints": ["/brands", "/sentiment", "/trends"],
    }


@app.get("/health", response_model=HealthOut, tags=["system"])
async def health():
    db_ok = await check_connection()
    return HealthOut(
        status="ok" if db_ok else "degraded",
        database="connected" if db_ok else "unreachable",
        **{"schema": os.getenv("DATABASE_SCHEMA", "spiritpulse")},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )