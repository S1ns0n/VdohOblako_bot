from sqlalchemy import select, update

from .models import User
from .session import AsyncSessionLocal


async def create_user(tg_id: int, path: str = "/") -> User | None:
    """Создание нового пользователя (асинхронно)"""
    async with AsyncSessionLocal() as db:
        try:
            user = User(tg_id=tg_id, path=path)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            print(f"Ошибка при создании записи: {e}")
            return None


async def check_user_exists(tg_id: int) -> bool:
    """Проверка наличия пользователя в базе данных"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(User).filter_by(tg_id=tg_id)
            )
            return result.scalar() is not None
        except Exception as e:
            print(f"Ошибка при проверке наличия пользователя: {e}")
            return False


async def get_all_users() -> list[User]:
    """Получение всех пользователей (асинхронно)"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User).order_by(User.created_at.desc()))
            return list(result.scalars().all())
        except Exception as e:
            print(f"Ошибка при получении пользователей: {e}")
            return []


async def get_user_by_tg_id(tg_id: int) -> User | None:
    """Получение пользователя по ID (асинхронно)"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(User).filter_by(tg_id=tg_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Ошибка при получении пользователя: {e}")
            return None


async def update_user_path(tg_id: int, path: str = "/") -> User | None:
    """Обновление пути пользователя (асинхронно)"""
    async with AsyncSessionLocal() as db:
        try:
            # Сначала получаем пользователя
            result = await db.execute(
                select(User).filter_by(tg_id=tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                user.path = path
                await db.commit()
                await db.refresh(user)
                return user
            return None
        except Exception as e:
            await db.rollback()
            print(f"Ошибка при обновлении записи: {e}")
            return None


async def delete_user(tg_id: int) -> bool:
    """Удаление пользователя (асинхронно)"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(User).filter_by(tg_id=tg_id)
            )
            user = result.scalar_one_or_none()

            if user:
                await db.delete(user)
                await db.commit()
                return True
            return False
        except Exception as e:
            await db.rollback()
            print(f"Ошибка при удалении записи: {e}")
            return False


async def get_user_count() -> int:
    """Получение количества пользователей в базе (асинхронно)"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User))
            return len(result.scalars().all())
        except Exception as e:
            print(f"Ошибка при подсчете пользователей: {e}")
            return 0

