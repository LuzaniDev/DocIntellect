from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    @abstractmethod
    async def save(self, file_path: str, content: bytes) -> str:
        ...

    @abstractmethod
    async def read(self, file_path: str) -> bytes:
        ...

    @abstractmethod
    async def delete(self, file_path: str) -> None:
        ...

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        ...


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file_path: str, content: bytes) -> str:
        full_path = self.base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)
        return str(full_path)

    async def read(self, file_path: str) -> bytes:
        return (self.base_path / file_path).read_bytes()

    async def delete(self, file_path: str) -> None:
        (self.base_path / file_path).unlink(missing_ok=True)

    async def exists(self, file_path: str) -> bool:
        return (self.base_path / file_path).exists()
