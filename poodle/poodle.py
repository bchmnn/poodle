import inspect
import logging
import re
from typing import Any, List, Optional

from .auth import AbstractSSOHandler, BrowserSSOHandler
from .corews import CoreWS
from .types.exception import (AuthError, CourseNotFoundError,
                              MissingPrivateAccessKeyError)
from .types.methods import DataTypeT, MoodleMethod, MoodleMethods, ReturnTypeT
from .types.site import CoreSitePublicConfig
from .util.cache import Cache, CacheItem
from .util.loggable import Loggable
from .util.tokens import Tokens


class Poodle(Loggable, CoreWS):
    cache: Cache = Cache()
    _auth_handlers: List[AbstractSSOHandler]

    def __init__(
        self,
        url: str,
        auth_handlers: Optional[List[AbstractSSOHandler]] = None,
    ):
        Loggable.__init__(self, "Poodle", logging.WARN)
        CoreWS.__init__(self, url)
        if auth_handlers is None:
            auth_handlers = []
        self._auth_handlers = [BrowserSSOHandler(0)]
        self._auth_handlers.extend(auth_handlers)

    @property
    def url(self):
        return self._url

    async def __aenter__(self):
        await super(CoreWS, self).__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await super(CoreWS, self).__aexit__(*args, **kwargs)

    async def authenticate(self):
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
                    tokens = await auth_handler.authenticate(public_config, self)
                else:
                    tokens = auth_handler.authenticate(public_config, self)
                if isinstance(tokens, Tokens):
                    self.tokens = tokens
                    return
                raise AuthError("Tokens has invalid type")
        raise AuthError("Authentication failed")

    async def fetch(
        self,
        method: MoodleMethod[Any, ReturnTypeT, DataTypeT],
        data: Optional[DataTypeT] = None,
        usecache=True,
        refetch=False,
    ) -> ReturnTypeT:
        key = method["key"]
        return_type = method["type"]
        cacheitem: CacheItem = {"key": key, "type": return_type}
        if usecache and not refetch:
            _item = self.cache.get(cacheitem)
            if _item is not None:
                return _item
        self.logger.debug("Fetching %s ...", key)
        item = return_type(**await self.call(key, data))  # type: ignore
        if usecache:
            self.cache.set(cacheitem, item)
        return item

    async def fetch_list(
        self,
        method: MoodleMethod[List, ReturnTypeT, DataTypeT],
        data: Optional[DataTypeT] = None,
        usecache=True,
        refetch=False,
    ) -> List[ReturnTypeT]:
        key = method["key"]
        return_type = method["type"]
        cacheitem: CacheItem = {"key": key, "type": return_type}
        if usecache and not refetch:
            _item = self.cache.get(cacheitem)
            if _item is not None:
                return _item
        self.logger.debug("Fetching %s ...", key)
        item = [return_type(**entry) for entry in await self.call(key, data)]
        if usecache:
            self.cache.set(cacheitem, item)
        return item  # type: ignore

    async def public_config(self) -> CoreSitePublicConfig:
        method = "tool_mobile_get_public_config"
        cacheitem: CacheItem = {"key": method, "type": CoreSitePublicConfig}
        item = self.cache.get(cacheitem)
        if item is not None:
            self.logger.debug("Fetching %s. Cache hit!", method)
            return item
        self.logger.debug("Fetching %s ...", method)
        public_config = CoreSitePublicConfig(
            **await self.call_ajax(
                method,
                presets={"use_get": True, "no_login": True},
            )
        )
        self.cache.set(cacheitem, public_config)
        return public_config

    async def core_webservice_get_site_info(self):
        return await self.fetch(MoodleMethods.CORE_WEBSERVICE_GET_SITE_INFO)

    @staticmethod
    def fix_file_url(url: str, token: str) -> str:
        return re.sub(
            r"(\/webservice)?\/pluginfile\.php", f"/tokenpluginfile.php/{token}", url
        )

    async def fetch_file(self, url):
        token = (await self.core_webservice_get_site_info()).userprivateaccesskey
        if token is None:
            raise MissingPrivateAccessKeyError(
                "Current site is missing userprivateaccesskey"
            )
        return await self.get(self.fix_file_url(url, token))

    async def core_enrol_get_users_courses(self, userid: Optional[int] = None):
        if userid is None:
            userid = (await self.core_webservice_get_site_info()).userid
        return await self.fetch_list(
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
            raise CourseNotFoundError(f"Could not find course: '{name}'")
        return courses[0]

    async def core_course_get_contents(self, courseid: int):
        return await self.fetch_list(
            MoodleMethods.CORE_COURSE_GET_CONTENTS,
            {"courseid": courseid},
            usecache=False,
        )

    async def mod_assign_get_assignments(self, courseids: List[int]):
        return await self.fetch(
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
            raise IndexError("Index out of bounds")
        return assignments[index]

    async def mod_assign_get_submissions(self, assignmentids: List[int]):
        return await self.fetch(
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
        return await self.fetch_list(
            MoodleMethods.MOD_ASSIGN_LIST_PARTICIPANTS,
            {"assignid": assignid, "groupid": 0, "filter": ""},
            usecache=False,
        )

    async def core_group_get_course_groups(self, courseid: int):
        return await self.fetch_list(
            MoodleMethods.CORE_GROUP_GET_COURSE_GROUPS,
            {"courseid": courseid},
            usecache=False,
        )
