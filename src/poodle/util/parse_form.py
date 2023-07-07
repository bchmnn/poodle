import urllib.parse
from typing import Any, Dict, List


def is_primitive(value: Any):
    return type(value) is int or type(value) is str or type(value) is bool


def is_collection(value: Any):
    return type(value) is set or type(value) is list


def _parse_form(data: Any, prefix: str = "") -> List:
    if data is None:
        return []
    if is_primitive(data):
        value = str(data).lower() if type(data) is bool else str(data)
        return [urllib.parse.quote(prefix) + "=" + urllib.parse.quote(value)]
    result = []
    if is_collection(data):
        for i, value in enumerate(data):
            value = data[i]
            result = result + _parse_form(
                value, prefix + (f"{i}" if prefix == "" else f"[{i}]")
            )
    else:
        dict = data.__dict__ if hasattr(data, "__dict__") else data
        for key in dict.keys():
            value = dict[key]
            result = result + _parse_form(
                value, prefix + (f"{key}" if prefix == "" else f"[{key}]")
            )
    return result


def parse_form(data: Dict[str, Any]):
    res = _parse_form(data)
    return "&".join(res)
