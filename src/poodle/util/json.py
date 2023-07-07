import json
from typing import Any


def toPrettyJson(obj: Any):
    dict = obj.__dict__ if hasattr(obj, "__dict__") else obj
    return json.dumps(dict, default=lambda obj: obj.__dict__, indent=4)
