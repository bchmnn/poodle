from typing import Tuple

from .credential_provider_interface import CredentialProviderInterface


class GenericCredentialProviderInterface(CredentialProviderInterface):
    _username: str
    _password: str

    def __init__(self, id_provider_url, priority):
        super().__init__(id_provider_url, priority)

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
