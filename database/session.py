from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

DATABASE_URL = "sqlite+aiosqlite:///./bot_database.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_default_action_types():
    """Создает стандартные типы действий в базе данных"""
    from .models import ActionType

    async with AsyncSessionLocal() as session:
        default_types = ["login", "input_media", "get_media", "check_path"]

        for type_name in default_types:
            existing = await session.execute(
                select(ActionType).filter_by(name=type_name)
            )
            existing = existing.scalar_one_or_none()

            if not existing:
                action_type = ActionType(name=type_name)
                session.add(action_type)

        await session.commit()

async def init_db():
    """инициализация базы данных"""
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await create_default_action_types()

async def get_async_session() -> AsyncSession:
    """Получение сессии"""
    async with AsyncSessionLocal() as session:
        yield session
