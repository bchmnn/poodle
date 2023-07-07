import inspect
import logging
import re
from typing import Any, Dict, Generic, List, Optional, Type, TypedDict, TypeVar

import aiohttp

from .types.exception import CoreWSError


from .auth.handler.abstract_sso_handler import AbstractSSOHandler
from .auth.handler.browser_sso_handler import BrowserSSOHandler
from .corews import CoreWS
from .types.assign import (
    AddonModAssignGetAssignments,
    AddonModAssignGetSubmissions,
    AddonModAssignParticipant,
)
from .types.groups import CoreGroupGetCourseGroup
from .types.course import CoreCourseGetContentsWSSection
from .types.courses import CoreEnrolledCourseData
from .types.site import CoreSiteInfo, CoreSitePublicConfig
from .util.cache import Cache, CacheItem
from .util.logging import Loggable
from .util.tokens import TokenPolicy, Tokens

T = TypeVar("T")
U = TypeVar("U", bound=TypedDict)


class MoodleMethod(TypedDict, Generic[T, U]):
    key: str
    type: Type[T]
    data: Type[U]


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
    CORE_WEBSERVICE_GET_SITE_INFO: MoodleMethod[CoreSiteInfo, NoArgs] = {
        "key": "core_webservice_get_site_info",
        "type": CoreSiteInfo,
        "data": NoArgs,
    }

    CORE_ENROL_GET_USERS_COURSES: MoodleMethod[
        List[CoreEnrolledCourseData], CoreEnrolGetUsersCoursesArgs
    ] = {
        "key": "core_enrol_get_users_courses",
        "type": List[CoreEnrolledCourseData],
        "data": CoreEnrolGetUsersCoursesArgs,
    }

    CORE_COURSE_GET_CONTENTS: MoodleMethod[
        List[CoreCourseGetContentsWSSection], CoreCourseGetContentsArgs
    ] = {
        "key": "core_course_get_contents",
        "type": List[CoreCourseGetContentsWSSection],
        "data": CoreCourseGetContentsArgs,
    }

    CORE_GROUP_GET_COURSE_GROUPS: MoodleMethod[
        List[CoreGroupGetCourseGroup], CoreGroupGetCourseGroupsArgs
    ] = {
        "key": "core_group_get_course_groups",
        "type": List[CoreGroupGetCourseGroup],
        "data": CoreGroupGetCourseGroupsArgs,
    }

    MOD_ASSIGN_GET_ASSIGNMENTS: MoodleMethod[
        AddonModAssignGetAssignments, ModAssignGetAssignmentsArgs
    ] = {
        "key": "mod_assign_get_assignments",
        "type": AddonModAssignGetAssignments,
        "data": ModAssignGetAssignmentsArgs,
    }

    MOD_ASSIGN_GET_SUBMISSIONS: MoodleMethod[
        AddonModAssignGetSubmissions, ModAssignGetSubmissionsArgs
    ] = {
        "key": "mod_assign_get_submissions",
        "type": AddonModAssignGetSubmissions,
        "data": ModAssignGetSubmissionsArgs,
    }

    # mod_assign_list_participants
    MOD_ASSIGN_LIST_PARTICIPANTS: MoodleMethod[
        List[AddonModAssignParticipant], ModAssignParticipantArgs
    ] = {
        "key": "mod_assign_list_participants",
        "type": List[AddonModAssignParticipant],
        "data": ModAssignParticipantArgs,
    }


class Poodle(Loggable):
    _url: str
    _corews: CoreWS
    _cache: Dict[str, Any]
    cache: Cache = Cache()
    _auth_handlers: List[AbstractSSOHandler]
    _token_policy: TokenPolicy

    def __init__(
        self,
        url: str,
        auth_handlers: List[AbstractSSOHandler] = [],
        token_policy: Optional[TokenPolicy] = None,
    ):
        self.init_logger("Poodle", level=logging.DEBUG)
        self._url = url
        self._cache = {}
        self._auth_handlers = [BrowserSSOHandler(0)]
        self._auth_handlers.extend(auth_handlers)
        self._token_policy = (
            token_policy if token_policy is not None else TokenPolicy.DONT_CACHE()
        )

    @property
    def url(self):
        return self._url

    async def __aenter__(self):
        self._corews = await CoreWS(self._url).__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._corews.__aexit__(*args, **kwargs)

    async def auth(self):
        if self._token_policy.cache:
            tokens = self._token_policy.retrieve()
            if tokens is not None:
                self._corews.tokens = tokens
                try:
                    await self.core_webservice_get_site_info()
                    return
                except CoreWSError as e:
                    self._logger.warn(
                        f"CoreWS raised error {e.errorcode}: {str(e)}. Reauthenticating"
                    )
        self._auth_handlers.sort(key=lambda handler: handler.priority, reverse=True)
        public_config = await self.public_config()
        for auth_handler in self._auth_handlers:
            if set(auth_handler.id_provider_urls).intersection(
                [
                    "*",
                    *map(
                        lambda identityprovider: identityprovider.url,
                        public_config.identityproviders,
                    ),
                ]
            ):
                if inspect.iscoroutinefunction(auth_handler.authenticate):
                    tokens = await auth_handler.authenticate(
                        public_config, self._corews
                    )
                else:
                    tokens = auth_handler.authenticate(public_config, self._corews)
                if isinstance(tokens, Tokens):
                    if self._token_policy.cache:
                        self._token_policy.persist(tokens)
                    self._corews.tokens = tokens
                    return
                else:
                    raise Exception("Tokens has invalid type")
        raise Exception("Authentication failed")

    async def get(
        self, method: MoodleMethod[T, U], data: U = {}, usecache=True, refetch=False
    ) -> T:
        key = method["key"]
        type = method["type"]
        cacheitem: CacheItem = {"key": key, "type": type}
        if usecache and not refetch:
            item = self.cache.get(cacheitem)
            if item is not None:
                return item
        self._logger.debug(f"Fetching {key} ...")
        if hasattr(type, "_name") and getattr(type, "_name") == "List":
            type = getattr(type, "__args__")[0]
            item = [type(**entry) for entry in await self._corews.call(key, data=data)]
        else:
            item = type(**await self._corews.call(key, data=data))
        if usecache:
            self.cache.set(cacheitem, item)  # type: ignore
        return item  # type: ignore

    async def public_config(self) -> CoreSitePublicConfig:
        method = "tool_mobile_get_public_config"
        cachekey = method
        if cachekey in self._cache.keys():
            self._logger.debug(f"Fetching {cachekey}. Cache hit!")
            return self._cache[cachekey]
        self._logger.debug(f"Fetching {cachekey} ...")
        public_config = CoreSitePublicConfig(
            **await self._corews.call_ajax(
                method,
                presets={"use_get": True, "no_login": True},
            )
        )
        self._cache["tool_mobile_get_public_config"] = public_config
        return public_config

    async def core_webservice_get_site_info(self):
        return await self.get(MoodleMethods.CORE_WEBSERVICE_GET_SITE_INFO)

    @staticmethod
    def fix_file_url(url: str, token: str) -> str:
        return re.sub(
            r"(\/webservice)?\/pluginfile\.php", f"/tokenpluginfile.php/{token}", url
        )

    async def fetch_file(self, url):
        token = (await self.core_webservice_get_site_info()).userprivateaccesskey
        if token is None:
            raise Exception("Current site is missing userprivateaccesskey")
        return await self._corews.get(self.fix_file_url(url, token))

    async def core_enrol_get_users_courses(self, userid: Optional[int] = None):
        if userid is None:
            userid = (await self.core_webservice_get_site_info()).userid
        return await self.get(
            MoodleMethods.CORE_ENROL_GET_USERS_COURSES,
            {"userid": userid, "returnusercount": 0},
            usecache=False,
        )

    async def get_user_courses(self, name: str, userid: Optional[int] = None):
        courses = await self.core_enrol_get_users_courses(userid)
        return [item for item in courses if name.lower() in item.fullname.lower()]

    async def get_user_course(self, name: str, userid: Optional[int] = None):
        courses = await self.get_user_courses(name, userid)
        if len(courses) == 0:
            raise Exception(f"Could not find course: '{name}'")
        return courses[0]

    async def core_course_get_contents(self, courseid: int):
        return await self.get(
            MoodleMethods.CORE_COURSE_GET_CONTENTS,
            {"courseid": courseid},
            usecache=False,
        )

    async def mod_assign_get_assignments(self, courseids: List[int]):
        return await self.get(
            MoodleMethods.MOD_ASSIGN_GET_ASSIGNMENTS,
            {"courseids": courseids},
            usecache=False,
        )

    async def get_assignments(self, courseid: int):
        return (
            (await self.mod_assign_get_assignments([courseid])).courses[0].assignments
        )

    async def get_assignment(self, courseid: int, index: int = 0):
        assignments = await self.get_assignments(courseid)
        if (
            index >= 0
            and index >= len(assignments)
            or index < 0
            and -index >= len(assignments)
        ):
            raise Exception("Index out of bounds")
        return assignments[index]

    async def mod_assign_get_submissions(self, assignmentids: List[int]):
        return await self.get(
            MoodleMethods.MOD_ASSIGN_GET_SUBMISSIONS,
            {"assignmentids": assignmentids},
            usecache=False,
        )

    async def get_submissions(self, assignmentid: int):
        return (
            (await self.mod_assign_get_submissions([assignmentid]))
            .assignments[0]
            .submissions
        )

    async def mod_assign_list_participants(self, assignid: int):
        return await self.get(
            MoodleMethods.MOD_ASSIGN_LIST_PARTICIPANTS,
            {"assignid": assignid, "groupid": 0, "filter": ""},
            usecache=False,
        )

    async def core_group_get_course_groups(self, courseid: int):
        return await self.get(
            MoodleMethods.CORE_GROUP_GET_COURSE_GROUPS,
            {"courseid": courseid},
            usecache=False,
        )
