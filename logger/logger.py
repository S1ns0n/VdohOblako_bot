import logging
import traceback
import asyncio
from typing import Optional


class AsyncLogger:

    def __init__(self, name: str = "logger", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    async def _log(self, level: int, message: str, include_stack: bool = False):
        if include_stack:
            stack = traceback.format_exc()
            if stack != 'NoneType: None\n':
                message = f"{message}\n{stack}"
            else:
                current_stack = ''.join(traceback.format_stack()[:-1])
                message = f"{message}\n{current_stack}"

        await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.logger.log(level, message)
        )

    async def debug(self, message: str):
        await self._log(logging.DEBUG, message)

    async def info(self, message: str):
        await self._log(logging.INFO, message)

    async def warning(self, message: str):
        await self._log(logging.WARNING, message)

    async def error(self, message: str, include_stack: bool = True):
        await self._log(logging.ERROR, message, include_stack)
