import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # Reads the .env file into environment variables

# The DATABASE_URL tells SQLAlchemy everything it needs:
# postgresql://username:password@host:port/database_name
DATABASE_URL = os.getenv("DATABASE_URL")

# The 'engine' is your connection to PostgreSQL.
# Think of it as opening the door to the database.
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory for creating database sessions.
# A 'session' is like a conversation with the database —
# you open it, do some work, then close it.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all your database models will inherit from.
# It's what lets SQLAlchemy know "this class represents a table."
Base = declarative_base()


def get_db():
    """
    A dependency function that FastAPI will call automatically.
    It creates a fresh database session for each request,
    then closes it when the request is done — even if an error occurs.
    The 'yield' keyword is what makes this a context manager.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()