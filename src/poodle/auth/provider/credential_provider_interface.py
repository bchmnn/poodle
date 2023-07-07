from poodle.util.logging import Loggable


class CredentialProviderInterface(Loggable):
    _priority: int
    _id_provider_url: str

    def __init__(self, id_provider_url, priority):
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
