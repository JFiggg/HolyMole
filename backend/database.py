"""
SQLAlchemy setup and Ingredient model for Holy Mole inventory.
Stores dynamic data: ingredient stock levels.
"""
from sqlalchemy import create_engine, text
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
    daily_usage = Column(Float, nullable=False, default=0.0)


def get_db():
    """Dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables and add daily_usage column if missing (migration)."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        info = conn.execute(text("PRAGMA table_info(ingredients)")).fetchall()
        columns = [row[1] for row in info]
        if "daily_usage" not in columns:
            conn.execute(text("ALTER TABLE ingredients ADD COLUMN daily_usage REAL NOT NULL DEFAULT 0"))
        conn.commit()
