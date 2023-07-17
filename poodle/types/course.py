from enum import IntEnum
from typing import List, Optional

from .jsonable import Jsonable
from .tag import CoreTagItem


class CoreCourseModuleCompletionTracking(Jsonable, IntEnum):
    """
    Completion tracking valid values.
    """

    COMPLETION_TRACKING_NONE = 0
    COMPLETION_TRACKING_MANUAL = 1
    COMPLETION_TRACKING_AUTOMATIC = 2


class CoreCourseModuleCompletionStatus(Jsonable, IntEnum):
    """
    Course Module completion status enumeration.
    """

    COMPLETION_INCOMPLETE = 0
    COMPLETION_COMPLETE = 1
    COMPLETION_COMPLETE_PASS = 2
    COMPLETION_COMPLETE_FAIL = 3


class CoreCourseModuleWSRuleValue(Jsonable):
    status: int  # Completion status.
    description: str  # Completion description.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreCourseModuleWSRuleDetails(Jsonable):
    """
    Module completion rule details.
    """

    rulename: str  # Rule name.
    rulevalue: CoreCourseModuleWSRuleValue = CoreCourseModuleWSRuleValue(
        **{"status": 0, "description": ""}
    )

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "rulevalue" in keys:
            rulevalue = entries["rulevalue"]
            if rulevalue is not None:
                self.rulevalue = CoreCourseModuleWSRuleValue(**rulevalue)


class CoreCourseModuleWSCompletionData(Jsonable):
    """
    Module completion data.
    """

    state: CoreCourseModuleCompletionStatus = (
        CoreCourseModuleCompletionStatus.COMPLETION_INCOMPLETE
    )  # Completion state value.
    timecompleted: int  # Timestamp for completion status.
    overrideby: Optional[int] = None  # The user id who has overriden the status.
    valueused: Optional[
        bool
    ] = None  # Whether the completion status affects the availability of another activity.
    hascompletion: Optional[
        bool
    ] = None  # @since 3.11. Whether this activity module has completion enabled.
    isautomatic: Optional[
        bool
    ] = None  # @since 3.11. Whether this activity module instance tracks completion automatically.
    istrackeduser: Optional[
        bool
    ] = None  # @since 3.11. Whether completion is being tracked for this user.
    uservisible: Optional[
        bool
    ] = None  # @since 3.11. Whether this activity is visible to the user.
    details: Optional[
        List[CoreCourseModuleWSRuleDetails]
    ] = None  # @since 3.11. An array of completion details.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()

        if "state" in keys:
            state = entries["state"]
            if state is not None:
                self.state = CoreCourseModuleCompletionStatus(state)

        if "details" in keys:
            details = entries["details"]
            if details is not None:
                self.details = [
                    CoreCourseModuleWSRuleDetails(**entry) for entry in details
                ]


class CoreCourseModuleContentFile(Jsonable):
    """
    Common properties with CoreWSExternalFile.
    """

    filename: str  # Filename.
    filepath: str  # Filepath.
    filesize: int  # Filesize.
    fileurl: str  # Downloadable file url.
    timemodified: int  # Time modified.
    mimetype: Optional[str] = None  # File mime type.
    isexternalfile: Optional[int] = None  # Whether is an external file.
    repositorytype: Optional[str] = None  # The repository type for external files.

    type: str  # A file or a folder or external link.
    content: Optional[str] = None  # Raw content, will be used when type is content.
    timecreated: int  # Time created.
    sortorder: int  # Content sort order.
    userid: int  # User who added this content to moodle.
    author: str  # Content owner.
    license: str  # Content license.
    tags: Optional[List[CoreTagItem]] = None  # Tags.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()

        if "tags" in keys:
            tags = entries["tags"]
            if tags is not None:
                self.tags = [CoreTagItem(**entry) for entry in tags]


class CoreCourseModuleDate(Jsonable):
    label: str
    timestamp: int

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreCourseModuleContentsInfo(Jsonable):
    filescount: int  # Total number of files.
    filessize: int  # Total files size.
    lastmodified: int  # Last time files were modified.
    mimetypes: List[str]  # Files mime types.
    repositorytype: Optional[str] = None  # The repository type for the main file.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class CoreCourseGetContentsWSModule(Jsonable):
    """
    Module data returned by core_course_get_contents WS.
    """

    id: int  # Activity id.
    url: Optional[str] = None  # Activity url.
    name: str  # Activity module name.
    instance: int  # Instance id. Cannot be undefined.
    contextid: Optional[int] = None  # @since 3.10. Activity context id.
    description: Optional[str] = None  # Activity description.
    visible: int  # Is the module visible. Cannot be undefined.
    uservisible: bool  # Is the module visible for the user?. Cannot be undefined.
    availabilityinfo: Optional[str] = None  # Availability information.
    visibleoncoursepage: int  # Is the module visible on course page. Cannot be undefined.
    modicon: str  # Activity icon url.
    modname: str  # Activity module type.
    modplural: str  # Activity module plural name.
    availability: Optional[str] = None  # Module availability settings.
    indent: int  # Number of identation in the site.
    onclick: Optional[str] = None  # Onclick action.
    afterlink: Optional[str] = None  # After link info to be displayed.
    customdata: Optional[str] = None  # Custom data (JSON encoded).
    noviewlink: Optional[bool] = None  # Whether the module has no view page.
    completion: Optional[
        CoreCourseModuleCompletionTracking
    ] = None  # Type of completion tracking: 0 means none, 1 manual, 2 automatic.
    completiondata: Optional[
        CoreCourseModuleWSCompletionData
    ] = None  # Module completion data.
    contents: Optional[List[CoreCourseModuleContentFile]] = None
    downloadcontent: Optional[int] = None  # @since 4.0 The download content value.
    dates: Optional[List[CoreCourseModuleDate]] = None  # @since 3.11. Activity dates.
    contentsinfo: Optional[
        CoreCourseModuleContentsInfo
    ] = None  # @since v3.7.6 Contents summary information.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()

        if "completion" in keys:
            completion = entries["completion"]
            if completion is not None:
                self.completion = CoreCourseModuleCompletionTracking(completion)

        if "completiondata" in keys:
            completiondata = entries["completiondata"]
            if completiondata is not None:
                self.completiondata = CoreCourseModuleWSCompletionData(**completiondata)

        if "contents" in keys:
            contents = entries["contents"]
            if contents is not None:
                self.contents = [
                    CoreCourseModuleContentFile(**entry) for entry in contents
                ]

        if "dates" in keys:
            dates = entries["dates"]
            if dates is not None:
                self.dates = [CoreCourseModuleDate(**entry) for entry in dates]

        if "contentsinfo" in keys:
            contentsinfo = entries["contentsinfo"]
            if contentsinfo is not None:
                self.contentsinfo = CoreCourseModuleContentsInfo(**contentsinfo)


class CoreCourseGetContentsWSSection(Jsonable):
    """
    Section data returned by core_course_get_contents WS.
    """

    id: int  # Section ID.
    name: str  # Section name.
    visible: Optional[int] = None  # Is the section visible.
    summary: str  # Section description.
    summaryformat: int  # Summary format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN).
    section: Optional[int] = None  # Section number inside the course.
    hiddenbynumsections: Optional[
        int
    ] = None  # Whether is a section hidden in the course format.
    uservisible: Optional[bool] = None  # Is the section visible for the user?.
    availabilityinfo: Optional[str] = None  # Availability information.
    modules: List[CoreCourseGetContentsWSModule] = []  # List of module.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()

        if "modules" in keys:
            modules = entries["modules"]
            if modules is not None:
                self.modules = [
                    CoreCourseGetContentsWSModule(**entry) for entry in modules
                ]
