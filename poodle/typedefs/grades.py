from typing import List, Optional

from .jsonable import Jsonable
from .ws import CoreWSExternalWarning


class CoreGradesGradeItem(Jsonable):
    id: int  # Grade item id.
    itemname: str  # Grade item name.
    itemtype: str  # Grade item type.
    itemmodule: str  # Grade item module.
    iteminstance: int  # Grade item instance.
    itemnumber: int  # Grade item item number.
    idnumber: str  # Grade item idnumber.
    categoryid: int  # Grade item category id.
    outcomeid: int  # Outcome id.
    scaleid: int  # Scale id.
    locked: Optional[bool] = None  # Grade item for user locked?.
    cmid: Optional[int] = None  # Course module id (if type mod).
    weightraw: Optional[int] = None  # Weight raw.
    weightformatted: Optional[str] = None  # Weight.
    status: Optional[str] = None  # Status.
    graderaw: Optional[int] = None  # Grade raw.
    gradedatesubmitted: Optional[int] = None  # Grade submit date.
    gradedategraded: Optional[int] = None  # Grade graded date.
    gradehiddenbydate: Optional[bool] = None  # Grade hidden by date?.
    gradeneedsupdate: Optional[bool] = None  # Grade needs update?.
    gradeishidden: Optional[bool] = None  # Grade is hidden?.
    gradeislocked: Optional[bool] = None  # Grade is locked?.
    gradeisoverridden: Optional[bool] = None  # Grade overridden?.
    gradeformatted: Optional[str] = None  # The grade formatted.
    grademin: Optional[int] = None  # Grade min.
    grademax: Optional[int] = None  # Grade max.
    rangeformatted: Optional[str] = None  # Range formatted.
    percentageformatted: Optional[str] = None  # Percentage.
    lettergradeformatted: Optional[str] = None  # Letter grade.
    rank: Optional[int] = None  # Rank in the course.
    numusers: Optional[int] = None  # Num users in course.
    averageformatted: Optional[str] = None  # Grade average.
    feedback: Optional[str] = None  # Grade feedback.
    feedbackformat: Optional[int] = (
        None  # Feedback format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN).
    )

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreGradesGetUserGradeItemsUserGrade(Jsonable):
    courseid: int  # Course id.
    userid: int  # User id.
    userfullname: str  # User fullname.
    useridnumber: str  # User idnumber.
    maxdepth: int  # Table max depth (needed for printing it).
    gradeitems: List[CoreGradesGradeItem] = []

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "gradeitems" in keys:
            gradeitems = entries.get("gradeitems")
            if gradeitems is not None:
                self.gradeitems = [CoreGradesGradeItem(**entry) for entry in gradeitems]


class CoreGradesGetUserGradeItems(Jsonable):
    """
    Originally: CoreGradesGetUserGradeItemsWSResponse
    Data returned by gradereport_user_get_grade_items
    """

    usergrades: List[CoreGradesGetUserGradeItemsUserGrade] = []
    warnings: Optional[List[CoreWSExternalWarning]] = None

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "usergrades" in keys:
            usergrades = entries.get("usergrades")
            if usergrades is not None:
                self.usergrades = [
                    CoreGradesGetUserGradeItemsUserGrade(**entry)
                    for entry in usergrades
                ]
        if "warnings" in keys:
            warnings = entries.get("warnings")
            if warnings is not None:
                self.warnings = [CoreWSExternalWarning(**entry) for entry in warnings]
