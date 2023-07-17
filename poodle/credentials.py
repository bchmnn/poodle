from getpass import getpass
from typing import Tuple

from .util.loggable import Loggable


class CredentialProviderInterface(Loggable):
    _priority: int
    _id_provider_url: str

    def __init__(self, id_provider_url: str, priority: int, name="CredentialProvider"):
        super().__init__(name)
        self._id_provider_url = id_provider_url
        self._priority = priority

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def id_provider_url(self) -> str:
        return self._id_provider_url

    @property
    def name(self) -> str:
        return "LoginProviderInterface"


class GenericCredentialProviderInterface(CredentialProviderInterface):
    _username: str
    _password: str

    def __init__(self, id_provider_url, priority, name):
        super().__init__(id_provider_url, priority, name)

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    def retrieve(self) -> Tuple[str, str]:
        """
        This method processes the credential retrieval
        and will be called once an authentication
        process is triggered.
        """
        return ("", "")

    @property
    def name(self) -> str:
        return "GenericLoginProviderInterface"


class CLICredentialProvider(GenericCredentialProviderInterface):
    def __init__(self, id_provider_url="*", priority=1):
        super().__init__(id_provider_url, priority, name="CLICredentialProvider")

    def retrieve(self) -> Tuple[str, str]:
        self._username = input("Username: ")
        self._password = getpass("Password: ")
        return (self._username, self.password)

    @property
    def name(self) -> str:
        return "CLILoginProvider"
