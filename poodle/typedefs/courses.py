from typing import List, Optional

from .jsonable import Jsonable
from .ws import CoreWSExternalFile


class CoreCourseBasicData(Jsonable):
    """
    Basic data obtained form any course.
    """

    id: int  # Course id.
    fullname: str  # Course full name.
    displayname: Optional[str] = None  # Course display name.
    shortname: str  # Course short name.
    summary: str  # Summary.
    summaryformat: int  # Summary format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN).
    categoryid: Optional[int] = None  # Course category id.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreEnrolledCourseBasicData(CoreCourseBasicData, Jsonable):
    """
    Basic data obtained from a course when the user is enrolled.
    """

    idnumber: Optional[str] = None  # Id number of course.
    visible: Optional[int] = None  # 1 means visible, 0 means not yet visible course.
    format: Optional[str] = None  # Course format: weeks, topics, social, site.
    showgrades: Optional[bool] = None  # True if grades are shown, otherwise false.
    lang: Optional[str] = None  # Forced course language.
    enablecompletion: Optional[
        bool
    ] = None  # True if completion is enabled, otherwise false.
    startdate: Optional[int] = None  # Timestamp when the course start.
    enddate: Optional[int] = None  # Timestamp when the course end.

    def __init__(self, **entries):
        CoreCourseBasicData.__init__(self, **entries)


class CoreEnrolledCourseData(CoreEnrolledCourseBasicData, Jsonable):
    """
    Course Data model received when the user is enrolled.
    """

    enrolledusercount: Optional[int] = None  # Number of enrolled users in this course.
    completionhascriteria: Optional[bool] = None  # If completion criteria is set.
    completionusertracked: Optional[bool] = None  # If the user is completion tracked.
    progress: Optional[int] = None  # Progress percentage.
    completed: Optional[bool] = None  # @since 3.6. Whether the course is completed.
    marker: Optional[int] = None  # @since 3.6. Course section marker.
    lastaccess: Optional[
        int
    ] = None  # @since 3.6. Last access to the course (timestamp).
    isfavourite: Optional[bool] = None  # If the user marked this course a favourite.
    hidden: Optional[bool] = None  # If the user hide the course from the dashboard.
    overviewfiles: List[CoreWSExternalFile] = []  # @since 3.6.
    showactivitydates: Optional[
        bool
    ] = None  # @since 3.11. Whether the activity dates are shown or not.
    showcompletionconditions: Optional[
        bool
    ] = None  # @since 3.11. Whether the activity completion conditions are shown or not.
    timemodified: Optional[
        int
    ] = None  # @since 4.0. Last time course settings were updated (timestamp).

    def __init__(self, **entries):
        CoreEnrolledCourseBasicData.__init__(self, **entries)
        keys = entries.keys()
        if "overviewfiles" in keys:
            overviewfiles = entries["overviewfiles"]
            if overviewfiles is not None:
                self.overviewfiles = [
                    CoreWSExternalFile(**entry) for entry in overviewfiles
                ]
