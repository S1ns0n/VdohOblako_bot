from sqlalchemy import select, update

from .models import User, ActionHistory
from .session import AsyncSessionLocal
from logger import main_logger

async def create_user(tg_id: int, path: str = "/") -> User | None:
    """Создание нового пользователя"""
    async with AsyncSessionLocal() as db:
        try:
            user = User(tg_id=tg_id, path=path)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            await main_logger.error(f"Ошибка создания пользователя: {e}")
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
            await main_logger.error(f"Ошибка при проверке наличия пользователя: {e}")
            return False


async def get_all_users() -> list[User]:
    """Получение всех пользователей"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User).order_by(User.created_at.desc()))
            return list(result.scalars().all())
        except Exception as e:
            await main_logger.error(f"Ошибка при получении пользователей: {e}")
            return []


async def get_user_by_tg_id(tg_id: int) -> User | None:
    """Получение объекта пользователя по ID"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(User).filter_by(tg_id=tg_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            await main_logger.error(f"Ошибка при получении пользователя: {e}")
            return None


async def update_user_path(tg_id: int, path: str = "/") -> User | None:
    """Обновление пути пользователя"""
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
            await main_logger.error(f"Ошибка при обновлении записи: {e}")
            return None



async def delete_user(tg_id: int) -> bool:
    """Удаление пользователя"""
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
            await main_logger.error(f"Ошибка при удалении записи: {e}")
            return False


async def get_user_count() -> int:
    """Получение количества пользователей в базе"""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User))
            return len(result.scalars().all())
        except Exception as e:
            await main_logger.error(f"Ошибка при подсчете пользователей: {e}")
            return 0

async def create_action(user_tg_id: int, action_id: int, desc: str = "")-> None:
    async with AsyncSessionLocal() as db:
        try:
            action = ActionHistory(user_tg_id=user_tg_id, action_type_id=action_id, description=desc)
            db.add(action)
            await db.commit()
            await db.refresh(action)
        except Exception as e:
            await db.rollback()
            await main_logger.error(f"Ошибка создания действия: {e}")
