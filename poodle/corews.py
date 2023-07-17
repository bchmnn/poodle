import json
import typing
from typing import Dict, Mapping, Optional
from urllib import parse

import aiohttp

from .constants import CONTENT_TYPE, X_WWW_FORM_URLENCODED
from .types.exception import CoreAjaxWSError, CoreConnectionError, CoreWSError
from .util.parse_form import parse_form
from .util.tokens import Tokens


class CoreWS(aiohttp.ClientSession):
    _url: str
    _tokens: Tokens

    def __init__(self, url):
        super().__init__()
        self._url = url

    @property
    def tokens(self):
        return None

    @tokens.setter
    def tokens(self, value: Tokens):
        self._tokens = value

    async def call(
        self,
        method: str,
        data: Optional[Mapping[str, typing.Any]] = None,
        presets: Optional[Mapping[str, typing.Any]] = None,
    ):
        """
        ref: moodleapp/src/core/services/ws.ts::CoreWSProvider::call
        """
        _data = dict(data) if data is not None else {}
        _presets = dict(presets) if presets is not None else {}
        _data["wsfunction"] = method
        _data["wstoken"] = self._tokens.token

        url = (
            self._url
            + "/webservice/rest/server.php?moodlewsrestformat=json&wsfunction="
            + method
        )
        __data = parse_form(_data)
        res = await self.post(
            url,
            data=__data,
            headers={CONTENT_TYPE: X_WWW_FORM_URLENCODED},
        )
        response = await res.text()
        if response is None and not _presets.get("response_expected"):
            response = "[{}]"

        if response is None:
            raise CoreConnectionError("connection error")
        result = json.loads(response)

        if "exception" in result:
            raise CoreWSError(
                result["exception"], result["errorcode"], result["message"]
            )

        return result

    async def call_ajax(
        self,
        method: str,
        data: Optional[dict] = None,
        presets: Optional[Dict[str, bool]] = None,
    ):
        if data is None:
            data = {}
        if presets is None:
            presets = {}
        ajax_data = [{"index": 0, "methodname": method, "args": data}]

        script = "service.php"
        if presets.get("use_get") and presets.get("no_login"):
            script = "service-nologin.php"

        url = self._url + "/lib/ajax/" + script + "?info=" + method

        res = None
        if presets.get("use_get") and presets.get("no_login"):
            res = await self.get(url + "&args=" + parse.quote(json.dumps(ajax_data)))
        else:
            res = await self.post(
                url,
                data=json.dumps(ajax_data),
                headers={CONTENT_TYPE: X_WWW_FORM_URLENCODED},
            )

        payload = await res.text()

        if payload is None and not presets.get("response_expected"):
            payload = "[{}]"

        if payload is None:
            raise CoreConnectionError("connection error")

        result = json.loads(payload)
        result = result[0]

        if "error" in result and result["error"] is not False:
            raise CoreAjaxWSError(
                result["exception"], result["errorcode"], result["message"]
            )

        return result["data"]
