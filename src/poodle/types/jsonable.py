import json
from enum import Enum


class Jsonable:
    def json(self):
        return json.dumps(self.__dict__, default=lambda obj: obj.__dict__, indent=4)

    def __repr__(self):
        if isinstance(self, Enum):
            v = self.value
            return f"'{v}'" if isinstance(v, str) else str(self.value)
        return super().__repr__()

    def __str__(self):
        return self.json()
