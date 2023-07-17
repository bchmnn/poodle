from typing import Optional

from poodle.types.jsonable import Jsonable


# Structure of warnings returned by WS.
class CoreWSExternalWarning(Jsonable):
    item: Optional[str] = None
    itemid: Optional[int] = None
    warningcode: Optional[
        str
    ] = None  # The warning code can be used by the client app to implement specific behaviour.
    message: Optional[
        str
    ] = None  # Untranslated english message to explain the warning.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreWSExternalFile(Jsonable):
    """
    Structure of files returned by WS.
    """

    fileurl: str  # Downloadable file url.
    filename: Optional[str] = None  # File name.
    filepath: Optional[str] = None  # File path.
    filesize: Optional[int] = None  # File size.
    timemodified: Optional[int] = None  # Time modified.
    mimetype: Optional[str] = None  # File mime type.
    isexternalfile: Optional[int] = None  # Whether is an external file.
    repositorytype: Optional[str] = None  # The repository type for external files.

    def __init__(self, **entries):
        self.__dict__.update(entries)
