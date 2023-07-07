import logging
import os
import tempfile
import time
import webbrowser
from typing import Tuple

import poodle.util.url_protocol as URLProtocol
from poodle.types.site import CoreSitePublicConfig
from poodle.util.tokens import Tokens

from .abstract_sso_handler import AbstractSSOHandler

LOGGER_NAME = "BrowserAuthHandler"
LOGGING_LEVEL = logging.DEBUG


class BrowserSSOHandler(AbstractSSOHandler):
    def __init__(self, priority: int):
        super().__init__(priority, ["*"])
        self.init_logger(LOGGER_NAME)
        self._logger.setLevel(LOGGING_LEVEL)

    @staticmethod
    def __init_dir() -> Tuple[tempfile.TemporaryDirectory, str]:
        dir = tempfile.TemporaryDirectory()
        file = dir.name + r"/token"
        return (dir, file)

    @staticmethod
    def __register_protocol(file: str):
        if URLProtocol.exists("moodlemobile"):
            URLProtocol.delete("moodlemobile")
        URLProtocol.register(
            "moodlemobile",
            " ".join(
                [
                    "python.exe",
                    '"-c"',
                    "\"import sys; f = open(sys.argv[-2], 'a'); f.write(sys.argv[-1]); f.close()\"",
                    f'"{file}"',
                    '"%1"',
                ]
            ),
        )

    @staticmethod
    def __unregister_protocol():
        if URLProtocol.exists("moodlemobile"):
            URLProtocol.delete("moodlemobile")

    @staticmethod
    def __open_browser(public_config: CoreSitePublicConfig, passport: float):
        webbrowser.open(
            f"{public_config.launchurl}?service=moodle_mobile_app&passport={passport}"
        )

    @staticmethod
    def __retrieve_token(file) -> str:
        secs = 60
        for i in range(secs):
            if os.path.isfile(file):
                break
            if i == secs - 1:
                raise Exception("Timeout")
            time.sleep(1)
        f = open(file, "r")
        token = f.read()
        f.close()
        return token

    def authenticate(self, public_config: CoreSitePublicConfig, _) -> Tokens:
        self._logger.info("Starting browser auth ...")

        (dir, file) = self.__init_dir()
        self.__register_protocol(file)

        httpswwwroot = public_config.httpswwwroot
        if httpswwwroot is None:
            raise Exception("httpswwwroot is None")

        passport = self.generate_passport()
        self._logger.debug("Using passport: %s", passport)

        self._logger.debug("Opening browser")
        self.__open_browser(public_config, passport)

        self._logger.debug("Fetching tokens ...")
        token = self.__retrieve_token(file)
        dir.cleanup()
        self.__unregister_protocol()

        self._logger.debug("Extracting tokens ...")
        tokens = self.extract_token(token, httpswwwroot, passport)

        self._logger.debug("Success: token: %s (private token omitted)", tokens.token)
        self._logger.info("Successfully authenticated")

        return tokens
