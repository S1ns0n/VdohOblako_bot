import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, BinaryIO, Dict
from config.config import Config
from yadisk import YaDisk
from database.database import get_user_by_tg_id
from database.models import User
from logger import main_logger
class YandexManager:
    def __init__(self, token: str):
        self.disk = YaDisk(token=token)
        self.BASE_WEB_URL = Config.YANDEX_MAIN_PATH
        self.executor = ThreadPoolExecutor(max_workers=10) # хватит на мелкий VPS 1 ядром

    async def _run_in_executor(self, func, *args):
        """Запускает синхронную функцию в executor'е"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: func(*args))

    async def close(self):
        """Закрывает executor"""
        self.executor.shutdown()


class UserSession:
    """Сессия для каждого пользователя"""

    def __init__(self, yandex_manager: YandexManager, user_tg_id: int):
        self.manager = yandex_manager
        self.user_tg_id = user_tg_id
        self.current_path = "/"
        self.folders: List[str] = []
        self._user: User | None = None
        self._initialized = False  # Добавляем флаг инициализации

    async def initialize(self):
        """Асинхронная инициализация"""
        if not self._initialized:
            self._user = await get_user_by_tg_id(self.user_tg_id)
            if self._user and self._user.path:
                self.current_path = self._user.path
            self._initialized = True

    async def upload_file(self, file_obj: BinaryIO, filename: str) -> bool:
        """Загружает файл на Яндекс.Диск в текущую директорию пользователя"""
        try:
            remote_path = f"{self.current_path.rstrip('/')}/{filename}"
            file_obj.seek(0)

            await self.manager._run_in_executor(
                self.manager.disk.upload, file_obj, remote_path
            )
            return True
        except Exception as e:
            await main_logger.error(f"Ошибка загрузки файла '{filename}' для пользователя {self.user_tg_id}: {e}")
            return False

    async def refresh_current_dir(self) -> None:
        """Обновление папок в директории пользователя"""
        self.folders = []
        try:
            items = await self.manager._run_in_executor(
                lambda: list(self.manager.disk.listdir(self.current_path))
            )
            self.folders = sorted(
            item.name for item in items
            if item.type == "dir"
        )
        except Exception as e:
            await main_logger.error(f"Ошибка у пользователя {self.user_tg_id}: {e}")

    async def get_files_count(self) -> int:
        """Подсчет файлов в директории пользователя"""
        try:
            items = await self.manager._run_in_executor(
                lambda: list(self.manager.disk.listdir(self.current_path))
            )
            return sum(1 for item in items if item.type == "file")
        except Exception as e:
            await main_logger.error(f"Ошибка подсчета файлов у пользователя {self.user_tg_id}: {e}")
            return 0

    async def change_dir(self, folder_index: int) -> bool:
        """Смена директории пользователя"""
        if 1 <= folder_index <= len(self.folders):
            selected_folder = self.folders[folder_index - 1]

            new_path = await self.manager._run_in_executor(
                lambda: os.path.join(self.current_path, selected_folder).replace("\\", "/")
            )

            self.current_path = new_path
            await self.refresh_current_dir()
            return True
        return False

    async def go_back(self) -> bool:
        """Возврат назад для пользователя"""
        if self.current_path != "/":
            parent_path = await self.manager._run_in_executor(
                lambda: os.path.dirname(self.current_path).replace("\\", "/")
            )

            path_exists = await self.manager._run_in_executor(
                lambda: self.manager.disk.exists(parent_path)
            )

            if path_exists:
                self.current_path = parent_path
                await self.refresh_current_dir()
                return True
        return False

    async def get_current_folder_url(self) -> str:
        """Генерация URL для пользователя"""
        if self.current_path == "/":
            return self.manager.BASE_WEB_URL

        encoded_path = await self.manager._run_in_executor(
            lambda: "/".join(part.replace(" ", "%20") for part in self.current_path.split("/") if part)
        )
        return f"{self.manager.BASE_WEB_URL}/{encoded_path}"


class SessionManager:
    """Менеджер сессий пользователей"""

    def __init__(self, yandex_token: str):
        self.yandex_manager = YandexManager(yandex_token)
        self.user_sessions: Dict[int, UserSession] = {}

    async def get_user_session(self, user_tg_id: int) -> UserSession:
        """Получает или создает и инициализирует сессию для пользователя"""
        if user_tg_id not in self.user_sessions:
            # Создаем новую сессию
            session = UserSession(self.yandex_manager, user_tg_id)
            self.user_sessions[user_tg_id] = session
            # Инициализируем ее
            await session.initialize()
        else:
            # Если сессия уже существует, убедимся что она инициализирована
            session = self.user_sessions[user_tg_id]
            if not session._initialized:
                await session.initialize()

        return self.user_sessions[user_tg_id]

    async def close_user_session(self, user_tg_id: int):
        """Закрывает сессию пользователя"""
        if user_tg_id in self.user_sessions:
            del self.user_sessions[user_tg_id]

    async def close_all(self):
        """Закрывает все сессии и менеджер"""
        self.user_sessions.clear()
        await self.yandex_manager.close()
