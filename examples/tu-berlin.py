import os
import logging
import re
from typing import List, Optional, Tuple

import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs4
from poodle import (
    Poodle,
    CONTENT_TYPE,
    X_WWW_FORM_URLENCODED,
    AbstractSSOHandler,
    AuthError,
    CLICredentialProvider,
    CoreSitePublicConfig,
    GenericCredentialProviderInterface,
    Tokens,
)

LOGGER_NAME = "IsisAuthHandler"
LOGGING_LEVEL = logging.DEBUG


class IsisAuthHandler(AbstractSSOHandler):
    _url_sso: str = "https://shibboleth.tubit.tu-berlin.de"

    _login_providers: List[GenericCredentialProviderInterface]
    _credentials: Optional[Tuple[str, str]] = None

    def __init__(
        self,
        priority: int = 0,
        login_providers: Optional[List[GenericCredentialProviderInterface]] = None,
    ):
        AbstractSSOHandler.__init__(
            self,
            priority,
            ["https://isis.tu-berlin.de/auth/shibboleth/index.php"],
            name="IsisAuthHandler",
        )
        self._login_providers = [
            CLICredentialProvider("https://isis.tu-berlin.de/auth/shibboleth/index.php")
        ]
        if login_providers is not None:
            self._login_providers.extend(login_providers)

    def __retrieve_credentials(self):
        self._login_providers.sort(key=lambda v: v.priority, reverse=True)
        for login_provider in self._login_providers:
            id_prov_url = login_provider.id_provider_url
            if id_prov_url != "*" and id_prov_url not in self.id_provider_urls:
                continue
            try:
                self.logger.debug("Using login provider %s ...", login_provider.name)
                self._credentials = login_provider.retrieve()
                break
            except AuthError:
                continue

        if self._credentials is None:
            raise AuthError("All login providers failed.")

    async def __shibboleth_execution_e1s1(self, session: aiohttp.ClientSession):
        return await session.post(
            self._url_sso + "/idp/profile/SAML2/Redirect/SSO",
            params={"execution": "e1s1"},
            data={
                "shib_idp_ls_exception.shib_idp_session_ss": "",
                "shib_idp_ls_success.shib_idp_session_ss": "true",
                "shib_idp_ls_value.shib_idp_session_ss": "",
                "shib_idp_ls_exception.shib_idp_persistent_ss": "",
                "shib_idp_ls_success.shib_idp_persistent_ss": "true",
                "shib_idp_ls_value.shib_idp_persistent_ss": "",
                "shib_idp_ls_supported": "true",
                "_eventId_proceed": "",
            },
            headers={CONTENT_TYPE: X_WWW_FORM_URLENCODED},
        )

    async def __shibboleth_execution_e1s2(self, session: aiohttp.ClientSession):
        if self._credentials is None:
            raise AuthError("credentials is None")
        # we have to do this hack, since the scheme
        # "moodlemobile" will raise an exception
        # if redirects are handled by aiohttp
        token: Optional[str] = None

        async def on_request_redirect(
            session, context, params: aiohttp.TraceRequestRedirectParams
        ):
            nonlocal token
            _location = params.response.headers.get("Location")
            if _location and "://token=" in _location:
                token = _location

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_redirect.append(on_request_redirect)
        trace_config.freeze()
        session.trace_configs.append(trace_config)

        try:
            response = await session.post(
                self._url_sso + "/idp/profile/SAML2/Redirect/SSO",
                params={"execution": "e1s2"},
                data={
                    "j_username": self._credentials[0],
                    "j_password": self._credentials[1],
                    "_eventId_proceed": "",
                },
                headers={CONTENT_TYPE: X_WWW_FORM_URLENCODED},
            )

            soup = bs4(await response.text(), "lxml")

            form = soup.find("form")
            if form is None:
                raise AuthError("No form found in response")

            inputs = soup.find_all("input")
            data = {input_.get("name"): input_.get("value") for input_ in inputs}

            await session.post(
                form.get("action"),
                data=data,
                headers={CONTENT_TYPE: X_WWW_FORM_URLENCODED},
            )

        except (
            ValueError,
            aiohttp.client_exceptions.NonHttpUrlRedirectClientError,
        ) as error:
            # this is the exception raised due to
            # aiohttp not knowing how to handle
            # "moodlemobile" scheme
            if not token:
                raise error
        finally:
            if "j_password" in data.keys():
                raise ValueError("Your Credentials were refused. Please check them.")
            session.trace_configs.remove(trace_config)

        if not token:
            raise AuthError("Location was None. Aborting ...")

        return token

    async def authenticate(
        self,
        public_config: CoreSitePublicConfig,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> Tokens:
        if session is None:
            raise AuthError("Session required for IsisAuthHandler")
        self.logger.info(
            "Starting auth for: %s ...", public_config.identityproviders[0].name
        )
        passport = self.generate_passport()
        self.logger.debug("Using passport: %s", passport)
        self.logger.debug("Fetching launchurl: %s ...", public_config.launchurl)
        if public_config.launchurl is None:
            raise AuthError("public_config did not provide launchurl")
        await session.get(
            public_config.launchurl,
            params={"service": "moodle_mobile_app", "passport": passport},
        )
        self.logger.debug(
            "Fetching identityprovider url: %s ...",
            public_config.identityproviders[0].url,
        )
        identityprovider = public_config.identityproviders[0].url
        if identityprovider is None:
            raise AuthError("identityprovider is missing url")
        response = await session.get(identityprovider)
        url_sso = str(response.history[-1].url)
        match = re.search("(https?://[A-Za-z_0-9.-]+).*", url_sso)
        if not match:
            raise AuthError("Invalid identity provider")

        url_sso = match.group(1)
        if url_sso != self._url_sso:
            raise AuthError(f"Unsupported identity provider: ${url_sso}")

        self.logger.debug("Fetching shibboleth execution e1s1 ...")
        await self.__shibboleth_execution_e1s1(session)
        if self._credentials is None:
            self.logger.debug("Retrieving credentials ...")
            self.__retrieve_credentials()
        self.logger.debug(
            "Fetching shibboleth execution e1s2 (posting credentials) ..."
        )
        token = await self.__shibboleth_execution_e1s2(session)

        httpswwwroot = public_config.httpswwwroot
        if httpswwwroot is None:
            raise AuthError("httpswwwroot is None")
        self.logger.debug("Extracting tokens ...")
        tokens = self.extract_token(token, httpswwwroot, passport)

        self.logger.debug("Success: token: %s (private token omitted)", tokens.token)
        self.logger.info("Successfully authenticated")

        return tokens


class StaticCredentialProvider(GenericCredentialProviderInterface):
    def __init__(self, username: str, password: str, id_provider_url="*", priority=3):
        super().__init__(id_provider_url, priority, name="StaticCredentialProvider")
        self._username = username
        self._password = password

    def retrieve(self) -> Tuple[str, str]:
        return (self._username, self._password)

    @property
    def name(self) -> str:
        return "StaticCredentialProvider"


async def main():
    if all(
        creds := (
            os.environ.get("MOODLEGRADE_USER"),
            os.environ.get("MOODLEGRADE_PASS"),
        )
    ):
        credential_provider = StaticCredentialProvider(creds[0], creds[1])
        auth_handler = IsisAuthHandler(
            priority=3, login_providers=[credential_provider]
        )
        async with Poodle(
            "https://isis.tu-berlin.de", auth_handlers=[auth_handler]
        ) as poodle:
            await poodle.authenticate()
            await poodle.core_enrol_get_users_courses()


asyncio.run(main())
