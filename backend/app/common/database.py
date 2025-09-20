from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL database for both development and production
# Auto-detect environment and use appropriate database URL
def get_database_url():
    # Check if running on Render (Render sets RENDER environment variable)
    if os.getenv("RENDER"):
        # Production environment - use DATABASE_PROD_URL
        return os.getenv("DATABASE_PROD_URL")
    else:
        # Local development - use DATABASE_URL or local default
        return os.getenv("DATABASE_URL", "postgresql://postgres:paswd188!!@localhost:5432/tasks_web_app")

SQLALCHEMY_DATABASE_URL = get_database_url()

# Handle Render.com's DATABASE_URL format (includes sslmode)
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()