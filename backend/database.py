"""
SQLAlchemy setup and Ingredient model for Holy Mole inventory.
Stores dynamic data: ingredient stock levels.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float

SQLALCHEMY_DATABASE_URL = "sqlite:///./holymole.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False)
    unit_cost = Column(Float, nullable=False, default=0.0)
    par_level = Column(Float, nullable=False, default=0.0)


def get_db():
    """Dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)
