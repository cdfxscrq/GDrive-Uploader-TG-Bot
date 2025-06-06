from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session as SessionType
from sqlalchemy.exc import SQLAlchemyError
from config import Config

# Base class for models
BASE = declarative_base()

def get_engine():
    """Create a SQLAlchemy engine."""
    try:
        engine = create_engine(Config.DATABASE_URL)
        return engine
    except SQLAlchemyError as e:
        print(f"Error creating engine: {e}")
        raise

def start() -> scoped_session:
    """Create and return a scoped session."""
    engine = get_engine()
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))

# Global session object for database operations
SESSION: scoped_session = start()
