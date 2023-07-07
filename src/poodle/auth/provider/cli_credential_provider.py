from getpass import getpass
from typing import Tuple

from .generic_credential_provider_interface import GenericCredentialProviderInterface


class CLICredentialProvider(GenericCredentialProviderInterface):
    def __init__(self, id_provider_url="*", priority=1):
        super().__init__(id_provider_url, priority)

    def retrieve(self) -> Tuple[str, str]:
        self._username = input("Username: ")
        self._password = getpass("Password: ")
        return (self._username, self.password)

    @property
    def name(self) -> str:
        return "CLILoginProvider"
