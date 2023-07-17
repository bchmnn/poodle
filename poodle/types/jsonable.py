import json
from enum import Enum
from typing import Any


class Jsonable:
    value: Any

    def json(self):
        return json.dumps(self.__dict__, default=lambda obj: obj.__dict__, indent=4)

    def __repr__(self):
        if isinstance(self, Enum):
            value = self.value
            return f"'{value}'" if isinstance(value, str) else str(self.value)
        return super().__repr__()

    def __str__(self):
        return self.json()
