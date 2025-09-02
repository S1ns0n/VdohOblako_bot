import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, BinaryIO

from yadisk import YaDisk


class YandexManager:
    def __init__(self, token: str):
        self.disk = YaDisk(token=token)
        self.current_path = "/"
        self.folders: List[str] = []
        self._files_count: int = 0
        self.BASE_WEB_URL = "https://disk.yandex.ru/client/disk"
        self.executor = ThreadPoolExecutor()

    async def _run_in_executor(self, func, *args):
        """Запускает синхронную функцию в executor'е"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: func(*args))

    async def upload_file(self, file_obj: BinaryIO, filename: str) -> bool:
        """Загружает файл на Яндекс.Диск в текущую директорию"""
        try:
            remote_path = f"{self.current_path.rstrip('/')}/{filename}"
            file_obj.seek(0)

            await self._run_in_executor(
                self.disk.upload, file_obj, remote_path
            )
            return True

        except Exception as e:
            print(f"Ошибка загрузки файла '{filename}': {e}")
            return False

    async def refresh_current_dir(self) -> None:
        """Обновление папок в директории"""
        self.folders = []
        try:
            items = await self._run_in_executor(
                lambda: list(self.disk.listdir(self.current_path))
            )
            self.folders = [item.name for item in items if item.type == "dir"]
        except Exception as e:
            print(f"Ошибка: {e}")

    async def get_files_count(self) -> int:
        """Подсчет файлов"""
        try:
            items = await self._run_in_executor(
                lambda: list(self.disk.listdir(self.current_path))
            )
            return sum(1 for item in items if item.type == "file")
        except Exception as e:
            print(f"Ошибка подсчета файлов: {e}")
            return 0

    async def change_dir(self, folder_index: int) -> bool:
        """Смена директории"""
        if 1 <= folder_index <= len(self.folders):
            selected_folder = self.folders[folder_index - 1]

            # Асинхронное построение пути
            new_path = await self._run_in_executor(
                lambda: os.path.join(self.current_path, selected_folder).replace("\\", "/")
            )

            self.current_path = new_path
            await self.refresh_current_dir()
            return True
        return False

    async def go_back(self) -> bool:
        """Возврат назад"""
        if self.current_path != "/":
            # Асинхронное получение родительской директории
            parent_path = await self._run_in_executor(
                lambda: os.path.dirname(self.current_path).replace("\\", "/")
            )

            # Проверяем, что путь существует на диске
            path_exists = await self._run_in_executor(
                lambda: self.disk.exists(parent_path)
            )

            if path_exists:
                self.current_path = parent_path
                await self.refresh_current_dir()
                return True
        return False

    async def get_current_folder_url(self) -> str:
        """Генерация URL"""
        if self.current_path == "/":
            return self.BASE_WEB_URL

        encoded_path = await self._run_in_executor(
            lambda: "/".join(part.replace(" ", "%20") for part in self.current_path.split("/") if part)
        )
        return f"{self.BASE_WEB_URL}/{encoded_path}"

    async def close(self):
        """Закрывает executor"""
        self.executor.shutdown()
