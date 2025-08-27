import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from yadisk import YaDisk


# class YandexManager:
#     def __init__(self, token):
#         self.disk = YaDisk(token=token)
#         self.current_path = "/"
#         self.folders = []
#         self.BASE_WEB_URL = "https://disk.yandex.ru/client/disk"
#
#     def refresh_current_dir(self):
#         self.folders = []
#
#         try:
#             items = list(self.disk.listdir(self.current_path))
#             for item in items:
#                 if item.type == "dir":
#                     self.folders.append(item.name)
#         except Exception as e:
#             print(f"Ошибка: {e}")
#
#     def get_current_folder_url(self):
#         """Генерирует URL текущей папки"""
#         if self.current_path == "/":
#             return self.BASE_WEB_URL
#
#         encoded_path = "/".join(part.replace(" ", "%20") for part in self.current_path.split("/") if part)
#         return f"{self.BASE_WEB_URL}/{encoded_path}"
#
#     def print_current_dir(self):
#         folders = []
#         for i, folder in enumerate(self.folders, 1):
#             folders.append(folder)
#
#         return folders
#
#     def get_files_count(self):
#         items = list(self.disk.listdir(self.current_path))
#         files = [item for item in items if item.type == "file"]
#         return len(files)
#
#     def change_dir(self, folder_index: int):
#         if 1 <= folder_index <= len(self.folders):
#             selected_folder = self.folders[folder_index - 1]
#             self.current_path = os.path.join(self.current_path, selected_folder).replace("\\", "/")
#             self.refresh_current_dir()
#
#     def go_back(self):
#         if self.current_path != "/":
#             self.current_path = os.path.dirname(self.current_path).replace("\\", "/")
#             self.refresh_current_dir()
#             print(f"\nВернулись в: {self.current_path}")
#         else:
#             print("Вы уже в корневой папке!")


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

    async def refresh_current_dir(self) -> None:
        """Только папки, без подсчета файлов если не нужно"""
        self.folders = []
        try:
            items = await self._run_in_executor(
                lambda: list(self.disk.listdir(self.current_path))
            )
            self.folders = [item.name for item in items if item.type == "dir"]
        except Exception as e:
            print(f"Ошибка: {e}")

    async def get_files_count(self) -> int:
        """Подсчет файлов через executor"""
        try:
            items = await self._run_in_executor(
                lambda: list(self.disk.listdir(self.current_path))
            )
            return sum(1 for item in items if item.type == "file")
        except Exception as e:
            print(f"Ошибка подсчета файлов: {e}")
            return 0

    async def change_dir(self, folder_index: int) -> bool:
        """Смена директории с проверкой через executor"""
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
        """Возврат назад с проверкой через executor"""
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
        """Генерация URL через executor"""
        if self.current_path == "/":
            return self.BASE_WEB_URL

        encoded_path = await self._run_in_executor(
            lambda: "/".join(part.replace(" ", "%20") for part in self.current_path.split("/") if part)
        )
        return f"{self.BASE_WEB_URL}/{encoded_path}"

    async def close(self):
        """Закрывает executor"""
        self.executor.shutdown()
