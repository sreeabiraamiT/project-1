import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Load .env only if it exists (for local development)
load_dotenv()

# 2. Look up the environment variable. 
# If os.getenv() fails, os.environ.get() explicitly checks the OS environment (which Render uses)
DATABASE_URL = os.environ.get("DATABASE_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment or .env file")

# 3. CRUCIAL FIX FOR RENDER: 
# Render's database strings start with "postgres://", 
# but SQLAlchemy 1.4+ requires "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
