import base64
import hashlib
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Optional

from .logging import Loggable


@dataclass
class Tokens:
    token: str
    private_token: str


class TokenPolicy(Loggable):
    _name: str
    _cache: bool
    _path: str = tempfile.gettempdir()
    _prefix: str = "0xDEADBEEF"
    _hash: bool

    def __init__(
        self,
        name: str,
        cache=False,
        path: Optional[str] = None,
        prefix: Optional[str] = None,
        hash=True,
    ):
        self.init_logger("TokenPolicy", logging.INFO)
        self._name = name
        self._cache = cache
        if path is not None:
            self._path = path
        if prefix is not None:
            self._prefix = prefix
        self._hash = hash

    @staticmethod
    def DONT_CACHE():
        return TokenPolicy("")

    @staticmethod
    def CACHE(name: str):
        return TokenPolicy(name, cache=True)

    @staticmethod
    def hash(s: str):
        h = hashlib.sha256(s.encode()).digest()
        b = base64.b64encode(h).decode()
        return b

    @staticmethod
    def escape(s: str):
        res = re.sub(r"([A-Z])", lambda m: "^" + m.group(1).lower(), s)
        return res.replace("/", "_").replace("+", "-")

    @property
    def cache(self):
        return self._cache

    def file(self):
        filename = self._name
        if self._hash:
            filename = self.escape(self.hash(self._name))
        return self._path + "/" + self._prefix + filename

    def persist(self, tokens: Tokens):
        if not self._cache:
            raise Exception("TokenPolicy set to not cache")
        file = self.file()
        self._logger.debug(f"Persisting tokens in {file} ...")
        f = open(file, "w")
        f.write(f"{tokens.token}:::{tokens.private_token}")
        f.close()

    def retrieve(self) -> Optional[Tokens]:
        if not self._cache:
            raise Exception("TokenPolicy set to not cache")
        file = self.file()
        self._logger.debug(f"Retrieving tokens from {file} ...")
        if not os.path.isfile(file):
            self._logger.debug(f"File does not exist: {file}")
            return None
        f = open(file, "r")
        token = f.read()
        f.close()
        tokens = token.split(":::")
        if len(tokens) == 2:
            pub = tokens[0]
            priv = tokens[1]
        elif len(tokens) == 3:
            pub = tokens[1]
            priv = tokens[2]
        else:
            self._logger.debug(f"File had invalid content: {file}")
            return None
        return Tokens(token=pub, private_token=priv)

    def clean(self) -> None:
        file = self.file()
        self._logger.debug(f"Cleaning tokens in {file}")
        if not os.path.isfile(file):
            return None
        os.remove(file)
