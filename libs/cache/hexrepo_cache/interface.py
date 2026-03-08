from abc import abstractmethod


class CacheInterface:
    @abstractmethod
    async def get(self, key: str) -> str:
        ...

    @abstractmethod
    async def set(self, key: str, value: str, **kwargs) -> bool:
        ...
