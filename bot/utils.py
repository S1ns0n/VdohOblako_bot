import re
from typing import Optional


class Utils:
    @staticmethod
    async def extract_number(text: str, pattern: str = r'_(\d+)$') -> Optional[int]:
        match = re.search(pattern, text)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, TypeError):
                return None
        return None