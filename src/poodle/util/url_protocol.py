from sys import platform


def exists(key: str):
    if platform != "windows":
        raise Exception("only windows")
    import poodle.util.win_registry as WinRegistry

    return WinRegistry.exists(r"SOFTWARE\\Classes\\" + key)


def delete(key: str):
    if platform != "windows":
        raise Exception("only windows")
    import poodle.util.win_registry as WinRegistry

    WinRegistry.rdelete(r"SOFTWARE\\Classes\\" + key)


def register(key: str, command: str):
    if platform != "windows":
        raise Exception("only windows")
    import poodle.util.win_registry as WinRegistry

    WinRegistry.rcreate(
        [
            (
                r"SOFTWARE\\Classes\\" + key,
                {"": f"URL:{key} Protocol", "URL Protocol": ""},
            ),
            (r"shell\\open\\command", {"": command}),
        ]
    )
