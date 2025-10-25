from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.endpoints import router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="CV Filtering System",
    description="Automated CV filtering system using OpenAI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger = logging.getLogger(__name__)
    logger.info("Starting CV Filtering System...")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    logger.info(f"Database Path: {settings.database_path}")
    logger.info(f"Match Threshold: {settings.match_threshold}")

    # Cleanup old cache entries
    from app.data.database import db
    db.cleanup_old_cache()
    logger.info("Old cache entries cleaned up")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CV Filtering System API",
        "docs": "/docs",
        "health": "/health"
    }
