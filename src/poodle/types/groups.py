from .jsonable import Jsonable


class CoreGroupGetCourseGroup(Jsonable):
    id: int
    courseid: int
    name: str
    description: str
    descriptionformat: int
    enrolmentkey: str
    idnumber: str

    def __init__(self, **entries):
        self.__dict__.update(entries)
