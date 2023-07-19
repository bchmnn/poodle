from typing import Generic, List, Optional, Type, TypedDict, TypeVar

from .assign import (AddonModAssignGetAssignments,
                     AddonModAssignGetSubmissions, AddonModAssignParticipant)
from .course import CoreCourseGetContentsWSSection
from .courses import CoreEnrolledCourseData
from .groups import CoreGroupGetCourseGroup
from .site import CoreSiteInfo

TypedDictT = TypedDict("TypedDictT", {})
ReturnContainerT = TypeVar("ReturnContainerT", List, Type[None])
ReturnTypeT = TypeVar("ReturnTypeT")
DataTypeT = TypeVar("DataTypeT", bound=TypedDictT)


class MoodleMethod(TypedDict, Generic[ReturnContainerT, ReturnTypeT, DataTypeT]):
    key: str
    container: Optional[Type[ReturnContainerT]]
    type: Type[ReturnTypeT]
    data: Type[DataTypeT]


class NoArgs(TypedDict):
    pass


class CoreEnrolGetUsersCoursesArgs(TypedDict):
    # TODO add missing args
    userid: int
    returnusercount: int  # 0 for False, 1 for True


class CoreCourseGetContentsArgs(TypedDict):
    # TODO add missing args
    courseid: int


class CoreGroupGetCourseGroupsArgs(TypedDict):
    # TODO add missing args
    courseid: int


class ModAssignGetAssignmentsArgs(TypedDict):
    # TODO add missing args
    courseids: List[int]


class ModAssignGetSubmissionsArgs(TypedDict):
    # TODO add missing args
    assignmentids: List[int]


class ModAssignParticipantArgs(TypedDict):
    # TODO add missing args
    assignid: int
    groupid: int
    filter: str


class MoodleMethods:
    @staticmethod
    def __generate(
        key: str,
        data_type: Type[DataTypeT],
        return_type: Type[ReturnTypeT],
        container_type: Optional[Type[ReturnContainerT]] = None,
    ) -> MoodleMethod[ReturnContainerT, ReturnTypeT, DataTypeT]:
        return {
            "key": key,
            "container": container_type,
            "type": return_type,
            "data": data_type,
        }

    CORE_WEBSERVICE_GET_SITE_INFO = __generate(
        key="core_webservice_get_site_info",
        return_type=CoreSiteInfo,
        data_type=NoArgs,
    )

    CORE_ENROL_GET_USERS_COURSES = __generate(
        key="core_enrol_get_users_courses",
        container_type=List,
        return_type=CoreEnrolledCourseData,
        data_type=CoreEnrolGetUsersCoursesArgs,
    )

    CORE_COURSE_GET_CONTENTS = __generate(
        key="core_course_get_contents",
        container_type=List,
        return_type=CoreCourseGetContentsWSSection,
        data_type=CoreCourseGetContentsArgs,
    )

    CORE_GROUP_GET_COURSE_GROUPS = __generate(
        key="core_group_get_course_groups",
        container_type=List,
        return_type=CoreGroupGetCourseGroup,
        data_type=CoreGroupGetCourseGroupsArgs,
    )

    MOD_ASSIGN_GET_ASSIGNMENTS = __generate(
        key="mod_assign_get_assignments",
        return_type=AddonModAssignGetAssignments,
        data_type=ModAssignGetAssignmentsArgs,
    )

    MOD_ASSIGN_GET_SUBMISSIONS = __generate(
        key="mod_assign_get_submissions",
        return_type=AddonModAssignGetSubmissions,
        data_type=ModAssignGetSubmissionsArgs,
    )

    MOD_ASSIGN_LIST_PARTICIPANTS = __generate(
        key="mod_assign_list_participants",
        container_type=List,
        return_type=AddonModAssignParticipant,
        data_type=ModAssignParticipantArgs,
    )
