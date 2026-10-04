import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.router import api_router
from app.models.user import User
from app.auth.security import get_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def init_default_admin(db: Session):
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        logger.info(f"Creating initial admin user: {settings.ADMIN_EMAIL}")
        admin = User(
            email=settings.ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            full_name=settings.ADMIN_FULL_NAME,
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Initial admin user created successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema exists on startup if database is reachable
    try:
        logger.info("Initializing database schema...")
        Base.metadata.create_all(bind=engine)

        # Initialize default admin
        with SessionLocal() as db:
            init_default_admin(db)
        logger.info("Application startup database initialization completed.")
    except Exception as e:
        logger.warning(f"Could not connect to database at startup ({e}). Continuing with startup...")

    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Automotive Paint Formula Database & Calculation Platform for Azerbaijan Refinish Market",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }
