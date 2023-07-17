import urllib.parse
from typing import Any, Dict, List


def is_primitive(value: Any):
    return isinstance(value, (int, str, bool))


def is_collection(value: Any):
    return isinstance(value, (set, list))


def _parse_form(data: Any, prefix: str = "") -> List[str]:
    if data is None:
        return []
    if is_primitive(data):
        value = str(data).lower() if isinstance(data, bool) else str(data)
        return [urllib.parse.quote(prefix) + "=" + urllib.parse.quote(value)]
    result: List[str] = []
    if is_collection(data):
        for i, value in enumerate(data):
            result = result + _parse_form(
                value, prefix + (f"{i}" if prefix == "" else f"[{i}]")
            )
    else:
        dictionary = data.__dict__ if hasattr(data, "__dict__") else data
        for key in dictionary.keys():
            value = dictionary[key]
            result = result + _parse_form(
                value, prefix + (f"{key}" if prefix == "" else f"[{key}]")
            )
    return result


def parse_form(data: Dict[str, Any]):
    res = _parse_form(data)
    return "&".join(res)
