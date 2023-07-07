from .jsonable import Jsonable


class CoreTagItem(Jsonable):
    """
    Structure of a tag item returned by WS.
    """

    id: int  # Tag id.
    name: str  # Tag name.
    rawname: str  # The raw, unnormalised name for the tag as entered by users.
    isstandard: bool  # Whether this tag is standard.
    tagcollid: int  # Tag collection id.
    taginstanceid: int  # Tag instance id.
    taginstancecontextid: int  # Context the tag instance belongs to.
    itemid: int  # Id of the record tagged.
    ordering: int  # Tag ordering.
    flag: int  # Whether the tag is flagged as inappropriate.

    def __init__(self, **entries):
        self.__dict__.update(entries)
