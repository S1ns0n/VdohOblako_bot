from typing import Any

from models import User
from session import SessionLocal


def create_user(tg_id: int, path: str = "/") -> User:
    """Создание нового пользователя"""
    db = SessionLocal()
    try:
        record = User(tg_id=tg_id, path=path)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        print(f"Ошибка при создании записи: {e}")
    finally:
        db.close()


def get_all_users() -> list[User]:
    """Получение всех пользователей"""
    db = SessionLocal()
    try:
        return db.query(User).order_by(User.created_at.desc()).all()
    finally:
        db.close()


def get_user_by_tg_id(tg_id: int) -> User:
    """Получение пользователя по ID"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.tg_id == tg_id).first()
    finally:
        db.close()


def update_record(tg_id: int, path: str = "/") -> Any | None:
    """Обновление пользователя"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            user.path = path
            db.commit()
            db.refresh(user)
            return user
        return None
    except Exception as e:
        db.rollback()
        print(f"Ошибка при обновлении записи: {e}")
        return None
    finally:
        db.close()


def delete_user(tg_id: int) -> bool:
    """ Удаление записи"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Ошибка при удалении записи: {e}")
        return False
    finally:
        db.close()


def get_user_count() -> int:
    """Получение количества пользователей в базе"""
    db = SessionLocal()
    try:
        return db.query(User).count()
    finally:
        db.close()
