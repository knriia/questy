import asyncio

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError


class Argon2PasswordHasher:
    def __init__(self):
        self._hasher = PasswordHasher()

    async def hash(self, password: str) -> str:
        return await asyncio.to_thread(self._hasher.hash, password)

    async def verify(self, password: str, password_hash: str) -> bool:
        try:
            return await asyncio.to_thread(self._hasher.verify, password_hash, password)
        except VerificationError:
            return False
