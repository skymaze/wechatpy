# -*- coding: utf-8 -*-
import os
import json

import pytest
import httpx
from pytest_httpx import HTTPXMock

from wechatpy import WeChatOAuth
from wechatpy.exceptions import WeChatClientException

_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
_FIXTURE_PATH = os.path.join(_TESTS_PATH, "fixtures")


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


def custom_response(request: httpx.Request):
    path = request.url.path[1:].replace("/", "_")
    res_file = os.path.join(_FIXTURE_PATH, f"{path}.json")
    content = {"errcode": 99999, "errmsg": f"can not find fixture: {res_file}"}
    headers = {"Content-Type": "application/json"}
    try:
        with open(res_file) as f:
            content = json.loads(f.read())
    except (IOError, ValueError):
        content["errmsg"] = f"Fixture {res_file} json decode error"
    return httpx.Response(
        status_code=200, json=content, request=request, headers=headers
    )


app_id = "123456"
secret = "123456"
redirect_uri = "http://localhost"


def test_get_authorize_url(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    oauth = WeChatOAuth(app_id, secret, redirect_uri)
    authorize_url = oauth.authorize_url
    assert (
        "https://open.weixin.qq.com/connect/oauth2/authorize?appid=123456&redirect_uri=http%3A%2F%2Flocalhost&response_type=code&scope=snsapi_base#wechat_redirect"
        == authorize_url
    )


def test_get_qrconnect_url(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    oauth = WeChatOAuth(app_id, secret, redirect_uri)
    url = oauth.qrconnect_url
    assert (
        "https://open.weixin.qq.com/connect/qrconnect?appid=123456&redirect_uri=http%3A%2F%2Flocalhost&response_type=code&scope=snsapi_login#wechat_redirect"
        == url
    )


def test_fetch_access_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    oauth = WeChatOAuth(app_id, secret, redirect_uri)
    res = oauth.fetch_access_token("123456")
    assert res["access_token"] == "ACCESS_TOKEN"


def test_refresh_access_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    oauth = WeChatOAuth(app_id, secret, redirect_uri)
    res = oauth.refresh_access_token("123456")
    assert res["access_token"] == "ACCESS_TOKEN"


def test_get_user_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    oauth = WeChatOAuth(app_id, secret, redirect_uri)
    oauth.fetch_access_token("123456")
    res = oauth.get_user_info()
    assert res["openid"] == "OPENID"


def test_check_access_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    oauth = WeChatOAuth(app_id, secret, redirect_uri)
    oauth.fetch_access_token("123456")
    res = oauth.check_access_token()
    assert res is True


def test_reraise_requests_exception(httpx_mock: HTTPXMock):
    def _wechat_api_mock(request: httpx.Request):
        return httpx.Response(status_code=404, content="404 not found")

    httpx_mock.add_callback(_wechat_api_mock)

    oauth = WeChatOAuth(app_id, secret, redirect_uri)
    try:
        oauth.fetch_access_token("123456")
    except WeChatClientException as e:
        assert e.response.status_code == 404
