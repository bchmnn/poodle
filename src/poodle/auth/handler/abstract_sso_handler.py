import base64
import hashlib
import random
from typing import List, Optional

import aiohttp

from poodle.types.site import CoreSitePublicConfig
from poodle.util.logging import Loggable
from poodle.util.tokens import Tokens


class AbstractSSOHandler(Loggable):
    _priority: int
    # supported id provider workflows
    _id_provider_urls: List[str]

    def __init__(self, priority: int, id_provider_urls: List[str]):
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
        if token == None or "://token=" not in token:
            raise Exception("SSO failed. Aborting ...")

        token = token.split("://token=", 1)[1]
        token = base64.b64decode(token).decode("utf-8")
        tokens = token.split(":::")
        if len(tokens) == 2:
            pub = tokens[0]
            priv = tokens[1]
        elif len(tokens) == 3:
            hash = hashlib.md5((url_moodle + str(passport)).encode("utf-8")).hexdigest()
            if hash != tokens[0]:
                print(f"passport: {passport}")
                raise Exception(f"Hash does not match. {hash}!={tokens[0]}")
            pub = tokens[1]
            priv = tokens[2]
            pass
        else:
            raise Exception(f"Received invalid tokens: {tokens}. Aborting ...")

        return Tokens(token=pub, private_token=priv)

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
