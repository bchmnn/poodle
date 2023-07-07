import winreg
from typing import Dict, List, Optional, Tuple


def exists(child: str, parent: Optional[winreg.HKEYType | int] = None):
    if parent is None:
        parent = winreg.HKEY_CURRENT_USER
    try:
        winreg.OpenKey(parent, child).Close()
        return True
    except FileNotFoundError:
        return False


def delete(child: str, parent: Optional[winreg.HKEYType | int] = None):
    if parent is None:
        parent = winreg.HKEY_CURRENT_USER
    if exists(child, parent):
        winreg.DeleteKeyEx(parent, child)


def rdelete(child: str, parent: Optional[winreg.HKEYType | int] = None):
    if parent is None:
        parent = winreg.HKEY_CURRENT_USER
    if not exists(child, parent):
        return
    key = winreg.OpenKey(parent, child)
    i = 0
    while True:
        try:
            subkey = winreg.EnumKey(key, i)
        except WindowsError:
            break
        rdelete(subkey, key)
        i += 1
    key.Close()
    delete(child, parent)


def create(
    child: str, parent: Optional[winreg.HKEYType | int] = None
) -> winreg.HKEYType:
    if parent is None:
        parent = winreg.HKEY_CURRENT_USER
    return winreg.CreateKey(parent, child)


def rcreate(entries: List[Tuple[str, Optional[Dict[str, str]]]]):
    parent = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "")
    for entry, values in entries:
        for key in entry.split(r"\\"):
            p = (
                winreg.OpenKey(parent, key)
                if exists(key, parent)
                else create(key, parent)
            )
            parent.Close()
            parent = p
        if values is not None:
            for k, v in values.items():
                winreg.SetValueEx(parent, k, 0, winreg.REG_SZ, v)
    parent.Close()
