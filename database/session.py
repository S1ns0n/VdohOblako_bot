from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Создание движка
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Инициализация базы данных (создание таблиц)"""
    from .models import Base
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """
    Получение сессии базы данных.
    Возвращает сессию, которую нужно закрыть после использования.
    """
    return SessionLocal()