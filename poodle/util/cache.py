import logging
from typing import Any, Dict, Generic, Optional, Type, TypedDict, TypeVar

from .loggable import Loggable

T = TypeVar("T")


class CacheItem(TypedDict, Generic[T]):
    key: str
    type: Type[T]


class Cache(Loggable):
    store: Dict[str, Any] = {}

    def __init__(self):
        super().__init__("Cache", logging.INFO)

    def set(self, item: CacheItem[T], value: T):
        self.store[item["key"]] = value

    def get(self, item: CacheItem[T]) -> Optional[T]:
        key = item["key"]
        if key in self.store:
            self.logger.debug("Cache hit for item key: %s", key)
            return self.store[item["key"]]
        return None
