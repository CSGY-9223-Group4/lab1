from ..config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Construct the Database URL
DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for SQL query logging

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class for declarative models
Base = declarative_base()

# Dependency for session management (useful in web frameworks like FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
