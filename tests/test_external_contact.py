# -*- coding: utf-8 -*-
import os
import json

import pytest
import httpx
from pytest_httpx import HTTPXMock
from wechatpy.work import WeChatClient

_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
_FIXTURE_PATH = os.path.join(_TESTS_PATH, "fixtures", "work")


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


def custom_response(request: httpx.Request):
    path = request.url.path.replace("/cgi-bin/", "").replace("/", "_")
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
secret = "123456"


def test_ec_addcorptag(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    tags = [{"name": "大鸟"}, {"name": "小菜"}]
    res = client.external_contact.add_corp_tag(None, "开发1组", 1, tags=tags)
    assert 0 == res["errcode"]


def test_ec_edit_corp_tag(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.external_contact.edit_corp_tag(
        "etm7wjCgAA-DYuu_JX8DrN0EUfa1ycDw", "开发2组", 1
    )
    assert 0 == res["errcode"]


def test_ec_del_corp_tag(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.external_contact.del_corp_tag(
        tag_id=["etm7wjCgAAADvErs_p_VhdNdN6-i2zAg"]
    )
    assert 0 == res["errcode"]


def test_ec_mark_tag(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.external_contact.mark_tag(
        "zm",
        "wmm7wjCgAAkLAv_eiVt53eBokOC3_Tww",
        add_tag=["etm7wjCgAAD5hhvyfhPUpBbCs0CYuQMg"],
    )
    assert 0 == res["errcode"]


def test_ec_batch_get_by_user(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.external_contact.batch_get_by_user("rocky")
    assert 0 == res["errcode"]


def test_ec_gen_all_by_user(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    external_contact_list = []
    for i in client.external_contact.gen_all_by_user("rocky"):
        external_contact_list.append(i)
    assert 2 == len(external_contact_list)
