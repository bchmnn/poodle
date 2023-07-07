import logging
from typing import Generic, Optional, Type, TypedDict, TypeVar

from .logging import Loggable

T = TypeVar("T")


class CacheItem(TypedDict, Generic[T]):
    key: str
    type: Type[T]


class Cache(Loggable):
    store = {}

    def __init__(self) -> None:
        self.init_logger("Cache", logging.INFO)

    def set(self, item: CacheItem[T], value: T):
        self.store[item["key"]] = value

    def get(self, item: CacheItem[T]) -> Optional[T]:
        key = item["key"]
        if key in self.store.keys():
            self._logger.debug(f"Cache hit for item key: {key}")
            return self.store[item["key"]]
        return None
