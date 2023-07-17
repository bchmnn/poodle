import base64
import hashlib
import logging
import random
from abc import abstractmethod
from typing import List, Optional

import aiohttp

from .types.exception import AuthError
from .types.site import CoreSitePublicConfig
from .util.loggable import Loggable
from .util.tokens import Tokens


class AbstractSSOHandler(Loggable):
    _priority: int
    # supported id provider workflows
    _id_provider_urls: List[str]

    def __init__(
        self, priority: int, id_provider_urls: List[str], name="AbstractSSOHandler"
    ):
        super().__init__(name)
        self._priority = priority
        self._id_provider_urls = id_provider_urls

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def id_provider_urls(self) -> List[str]:
        return self._id_provider_urls

    @staticmethod
    def generate_passport() -> float:
        return random.random() * 1000

    @staticmethod
    def extract_token(token: str, url_moodle: str, passport: float) -> Tokens:
        if token is None or "://token=" not in token:
            raise AuthError("SSO failed. Aborting ...")

        token = token.split("://token=", 1)[1]
        token = base64.b64decode(token).decode("utf-8")
        tokens = token.split(":::")
        if len(tokens) == 2:
            pub = tokens[0]
            priv = tokens[1]
        elif len(tokens) == 3:
            checksum = hashlib.md5(
                (url_moodle + str(passport)).encode("utf-8")
            ).hexdigest()
            if checksum != tokens[0]:
                print(f"passport: {passport}")
                raise AuthError(f"Hash does not match. {checksum}!={tokens[0]}")
            pub = tokens[1]
            priv = tokens[2]
        else:
            raise AuthError(f"Received invalid tokens: {tokens}. Aborting ...")

        return Tokens(token=pub, private_token=priv)

    @abstractmethod
    async def authenticate(
        self,
        public_config: CoreSitePublicConfig,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> Tokens:
        """
        Authenticates the user using given public config.
        Args:
            public_config (CoreSitePublicConfigResponse): public config returned by moodle instance
        Returns:
            Tokens: {token, private_token}
        """
        return Tokens("", "")


LOGGER_NAME = "BrowserSSOHandler"
LOGGING_LEVEL = logging.WARN


class BrowserSSOHandler(AbstractSSOHandler):
    def __init__(self, priority: int):
        AbstractSSOHandler.__init__(self, priority, ["*"], LOGGER_NAME)
        self.logger.setLevel(LOGGING_LEVEL)

    # @staticmethod
    # def __init_dir() -> Tuple[tempfile.TemporaryDirectory, str]:
    #     directory = tempfile.TemporaryDirectory()
    #     file = directory.name + r"/token"
    #     return (directory, file)

    # @staticmethod
    # def __register_protocol(file: str):
    #     if exists("moodlemobile"):
    #         delete("moodlemobile")
    #     register(
    #         "moodlemobile",
    #         " ".join(
    #             [
    #                 "python.exe",
    #                 '"-c"',
    #      "\"import sys; f = open(sys.argv[-2], 'a'); f.write(sys.argv[-1]); f.close()\"",
    #                 f'"{file}"',
    #                 '"%1"',
    #             ]
    #         ),
    #     )

    # @staticmethod
    # def __unregister_protocol():
    #     if URLProtocol.exists("moodlemobile"):
    #         URLProtocol.delete("moodlemobile")

    # @staticmethod
    # def __open_browser(public_config: CoreSitePublicConfig, passport: float):
    #     webbrowser.open(
    #         f"{public_config.launchurl}?service=moodle_mobile_app&passport={passport}"
    #     )

    # @staticmethod
    # def __retrieve_token(file) -> str:
    #     secs = 60
    #     for i in range(secs):
    #         if os.path.isfile(file):
    #             break
    #         if i == secs - 1:
    #             raise AuthError("Timeout")
    #         time.sleep(1)
    #     with open(file, "r", encoding="utf-8") as f:
    #         token = f.read()
    #         f.close()
    #         return token

    async def authenticate(
        self,
        public_config: CoreSitePublicConfig,
        _: Optional[aiohttp.ClientSession] = None,
    ) -> Tokens:
        raise NotImplementedError()
        # self.logger.info("Starting browser auth ...")

        # (directory, file) = self.__init_dir()
        # self.__register_protocol(file)

        # httpswwwroot = public_config.httpswwwroot
        # if httpswwwroot is None:
        #     raise AuthError("httpswwwroot is None")

        # passport = self.generate_passport()
        # self.logger.debug("Using passport: %s", passport)

        # self.logger.debug("Opening browser")
        # self.__open_browser(public_config, passport)

        # self.logger.debug("Fetching tokens ...")
        # token = self.__retrieve_token(file)
        # directory.cleanup()
        # self.__unregister_protocol()

        # self.logger.debug("Extracting tokens ...")
        # tokens = self.extract_token(token, httpswwwroot, passport)

        # self.logger.debug("Success: token: %s (private token omitted)", tokens.token)
        # self.logger.info("Successfully authenticated")

        # return tokens
