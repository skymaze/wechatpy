# -*- coding: utf-8 -*-
"""
    wechatpy.oauth
    ~~~~~~~~~~~~~~~

    This module provides OAuth2 library for WeChat
"""

import json
from urllib.parse import quote
import requests
from wechatpy.exceptions import WeChatOAuthException


class WeChatOAuth:
    """微信公众平台 OAuth 网页授权"""

    API_BASE_URL: str = "https://api.weixin.qq.com/"
    OAUTH_BASE_URL: str = "https://open.weixin.qq.com/connect/"

    def __init__(
        self,
        app_id: str,
        secret: str,
        redirect_uri: str,
        scope: str = "snsapi_base",
        state: str = "",
    ) -> None:
        self.app_id = app_id
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.state = state
        self._http = requests.Session()

    def _request(self, method: str, url_or_endpoint: str, **kwargs) -> dict:
        if not url_or_endpoint.startswith(("http://", "https://")):
            url = f"{self.API_BASE_URL}{url_or_endpoint}"
        else:
            url = url_or_endpoint

        if isinstance(kwargs.get("data", ""), dict):
            body = json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode("utf-8")
            kwargs["data"] = body

        res = self._http.request(method=method, url=url, **kwargs)
        try:
            res.raise_for_status()
        except requests.RequestException as reqe:
            raise WeChatOAuthException(
                errcode=None,
                errmsg=None,
                client=self,
                request=reqe.request,
                response=reqe.response,
            )
        result = json.loads(res.content.decode("utf-8", "ignore"), strict=False)

        if "errcode" in result and result["errcode"] != 0:
            errcode = result["errcode"]
            errmsg = result["errmsg"]
            raise WeChatOAuthException(
                errcode, errmsg, client=self, request=res.request, response=res
            )

        return result

    def _get(self, url: str, **kwargs) -> dict:
        return self._request(method="get", url_or_endpoint=url, **kwargs)

    @property
    def authorize_url(self) -> str:
        redirect_uri = quote(self.redirect_uri, safe=b"")
        url_list = [
            self.OAUTH_BASE_URL,
            "oauth2/authorize?appid=",
            self.app_id,
            "&redirect_uri=",
            redirect_uri,
            "&response_type=code&scope=",
            self.scope,
        ]
        if self.state:
            url_list.extend(["&state=", self.state])
        url_list.append("#wechat_redirect")
        return "".join(url_list)

    @property
    def qrconnect_url(self) -> str:
        redirect_uri = quote(self.redirect_uri, safe=b"")
        url_list = [
            self.OAUTH_BASE_URL,
            "qrconnect?appid=",
            self.app_id,
            "&redirect_uri=",
            redirect_uri,
            "&response_type=code&scope=",
            "snsapi_login",  # scope
        ]
        if self.state:
            url_list.extend(["&state=", self.state])
        url_list.append("#wechat_redirect")
        return "".join(url_list)

    def fetch_access_token(self, code: str) -> dict:
        res = self._get(
            "sns/oauth2/access_token",
            params={
                "appid": self.app_id,
                "secret": self.secret,
                "code": code,
                "grant_type": "authorization_code",
            },
        )
        self.access_token = res["access_token"]
        self.open_id = res["openid"]
        self.refresh_token = res["refresh_token"]
        self.expires_in = res["expires_in"]
        return res

    def refresh_access_token(self, refresh_token: str) -> dict:
        res = self._get(
            "sns/oauth2/refresh_token",
            params={
                "appid": self.app_id,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        self.access_token = res["access_token"]
        self.open_id = res["openid"]
        self.refresh_token = res["refresh_token"]
        self.expires_in = res["expires_in"]
        return res

    def get_user_info(
        self, openid: str = None, access_token: str = None, lang: str = "zh_CN"
    ) -> dict:
        openid = openid or self.open_id
        access_token = access_token or self.access_token
        return self._get(
            "sns/userinfo",
            params={"access_token": access_token, "openid": openid, "lang": lang},
        )

    def check_access_token(self, openid: str = None, access_token: str = None) -> bool:
        openid = openid or self.open_id
        access_token = access_token or self.access_token
        res = self._get(
            "sns/auth", params={"access_token": access_token, "openid": openid}
        )
        if res["errcode"] == 0:
            return True
        return False
