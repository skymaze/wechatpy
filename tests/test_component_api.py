# -*- coding: utf-8 -*-
import os
import json
import inspect

import pytest
import httpx
from pytest_httpx import HTTPXMock

from wechatpy.component import WeChatComponent, ComponentOAuth
from wechatpy.exceptions import WeChatClientException


_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
_FIXTURE_PATH = os.path.join(_TESTS_PATH, "fixtures", "component")


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


def custom_response(request: httpx.Request):
    path = request.url.path.replace("/cgi-bin/component/", "").replace("/", "_")
    res_file = os.path.join(_FIXTURE_PATH, f"{path}.json")
    content = {
        "errcode": 99999,
        "errmsg": f"can not find fixture {res_file}",
    }
    headers = {"Content-Type": "application/json"}
    try:
        with open(res_file, "rb") as f:
            content = json.loads(f.read().decode("utf-8"))
    except (IOError, ValueError) as e:
        content["errmsg"] = f"Loads fixture {res_file} failed, error: {e}"
    return httpx.Response(
        status_code=200, json=content, request=request, headers=headers
    )


app_id = "123456"
app_secret = "123456"
token = "sdfusfsssdc"
encoding_aes_key = "yguy3495y79o34vod7843933902h9gb2834hgpB90rg"


def test_fetch_access_token_is_method(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    assert inspect.ismethod(client.fetch_access_token)


def test_fetch_access_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    token = client.fetch_access_token()
    assert token["component_access_token"] == "1234567890"
    assert 7200 == token["expires_in"]
    assert "1234567890" == client.access_token


def test_create_preauthcode(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    result = client.create_preauthcode()
    assert "1234567890" == result["pre_auth_code"]
    assert 600 == result["expires_in"]


def test_query_auth(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    authorization_code = "1234567890"
    result = client.query_auth(authorization_code)
    assert "wxf8b4f85f3a794e77" == result["authorization_info"]["authorizer_appid"]


def test_refresh_authorizer_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    appid = "appid"
    refresh_token = "refresh_token"

    result = client.refresh_authorizer_token(appid, refresh_token)
    assert "1234567890" == result["authorizer_access_token"]
    assert "123456789" == result["authorizer_refresh_token"]
    assert 7200 == result["expires_in"]


def test_get_authorizer_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    authorizer_appid = "wxf8b4f85f3a794e77"

    result = client.get_authorizer_info(authorizer_appid)
    assert "paytest01" == result["authorizer_info"]["alias"]


def test_get_authorizer_option(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    appid = "wxf8b4f85f3a794e77"
    result = client.get_authorizer_option(appid, "voice_recognize")
    assert "voice_recognize" == result["option_name"]
    assert "1" == result["option_value"]


def test_set_authorizer_option(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatComponent(app_id, app_secret, token, encoding_aes_key)
    appid = "wxf8b4f85f3a794e77"
    result = client.set_authorizer_option(appid, "voice_recognize", "0")
    assert 0 == result["errcode"]


app_id = "123456"
component_appid = "456789"
component_appsecret = "123456"
component_token = "654321"
encoding_aes_key = "yguy3495y79o34vod7843933902h9gb2834hgpB90rg"
redirect_uri = "http://localhost"


def test_get_authorize_url(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    component = WeChatComponent(
        component_appid,
        component_appsecret,
        component_token,
        encoding_aes_key,
    )
    oauth = ComponentOAuth(
        component,
        app_id,
    )
    authorize_url = oauth.get_authorize_url(redirect_uri)
    assert (
        "https://open.weixin.qq.com/connect/oauth2/authorize?appid=123456&redirect_uri=http%3A%2F%2Flocalhost"
        "&response_type=code&scope=snsapi_base&component_appid=456789#wechat_redirect"
        == authorize_url
    )


def test_fetch_access_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    component = WeChatComponent(
        component_appid,
        component_appsecret,
        component_token,
        encoding_aes_key,
    )
    oauth = ComponentOAuth(
        component,
        app_id,
    )
    res = oauth.fetch_access_token("123456")
    assert "ACCESS_TOKEN" == res["access_token"]


def test_refresh_access_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    component = WeChatComponent(
        component_appid,
        component_appsecret,
        component_token,
        encoding_aes_key,
    )
    oauth = ComponentOAuth(
        component,
        app_id,
    )
    res = oauth.refresh_access_token("123456")
    assert "ACCESS_TOKEN" == res["access_token"]


def test_get_user_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    component = WeChatComponent(
        component_appid,
        component_appsecret,
        component_token,
        encoding_aes_key,
    )
    oauth = ComponentOAuth(
        component,
        app_id,
    )
    oauth.fetch_access_token("123456")
    res = oauth.get_user_info()
    assert "OPENID" == res["openid"]


def test_reraise_requests_exception(httpx_mock: HTTPXMock):
    def not_found_response(request: httpx.Request):
        return httpx.Response(status_code=404, request=request, content="404 not found")

    httpx_mock.add_callback(not_found_response)
    component = WeChatComponent(
        component_appid,
        component_appsecret,
        component_token,
        encoding_aes_key,
    )
    oauth = ComponentOAuth(
        component,
        app_id,
    )
    try:
        oauth.fetch_access_token("123456")
    except WeChatClientException as e:
        assert 404 == e.response.status_code
