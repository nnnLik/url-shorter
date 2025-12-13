import hashlib
import secrets
from dataclasses import dataclass
from typing import Self

import core.constants


@dataclass
class CodeGeneratorService:
    @classmethod
    def build(cls) -> Self:
        return cls()

    def _generate_code(self, length: int) -> str:
        random_bytes = secrets.token_bytes(32)
        hash_bytes = hashlib.sha256(random_bytes).digest()

        # Конвертируем в Base62
        num: int = int.from_bytes(hash_bytes, byteorder='big')
        code: list[str] = []
        for _ in range(length):
            code.append(core.constants.BASE62_CHARS[num % 62])
            num //= 62
        return ''.join(reversed(code))

    def _generate_codes_batch(self, count: int) -> list[str]:
        codes = set[str]()
        max_attempts = count * 10  # защита от бесконечного цикла

        for _ in range(max_attempts):
            if len(codes) >= count:
                break
            codes.add(self._generate_code(core.constants.CODE_LENGTH))

        return list[str](codes)[:count]

    def execute(self, count: int = 1) -> list[str]:
        if count == 1:
            return [self._generate_code(core.constants.CODE_LENGTH)]
        return self._generate_codes_batch(count)
