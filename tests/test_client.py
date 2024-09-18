# -*- coding: utf-8 -*-
import io
import json
import os
import re
import inspect
import time
import pytest
from datetime import datetime

from httmock import HTTMock, response, urlmatch
import httpx
from pytest_httpx import HTTPXMock

from wechatpy import WeChatClient
from wechatpy.exceptions import WeChatClientException
from wechatpy.schemes import JsApiCardExt

_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
_FIXTURE_PATH = os.path.join(_TESTS_PATH, "fixtures")


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


def custom_response(request: httpx.Request):
    path = request.url.path.replace("/cgi-bin/", "").replace("/", "_")
    if path.startswith("_"):
        path = path[1:]
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


def test_two_client_not_equal(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    client2 = WeChatClient("654321", "654321", "987654321")
    assert client != client2
    assert client.user != client2.user
    assert id(client.menu) != id(client2.menu)
    client.fetch_access_token()
    assert client.access_token != client2.access_token


def test_subclass_client_ok(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)

    class TestClient(WeChatClient):
        pass

    client = TestClient("12345", "123456", "123456789")
    assert client == client.user._client


def test_fetch_access_token_is_method(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)

    assert inspect.ismethod(client.fetch_access_token)

    class TestClient(WeChatClient):
        @property
        def fetch_access_token(httpx_mock: HTTPXMock):
            pass

    client = TestClient("12345", "123456", "123456789")
    assert not inspect.ismethod(client.fetch_access_token)


def test_fetch_access_token(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    token = client.fetch_access_token()
    assert "1234567890" == token["access_token"]
    assert 7200 == token["expires_in"]
    assert "1234567890" == client.access_token


def test_upload_media(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    media_file = io.BytesIO(b"nothing")

    media = client.media.upload("image", media_file)
    assert "image" == media["type"]
    assert "12345678" == media["media_id"]


def test_user_get_group_id(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    group_id = client.user.get_group_id("123456")
    assert 102 == group_id


def test_create_group(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    group = client.group.create("test")
    assert 1 == group["group"]["id"]
    assert "test" == group["group"]["name"]


def test_group_get(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    groups = client.group.get()
    assert 5 == len(groups)


def test_group_getid(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    group = client.group.get("123456")
    assert 102 == group


def test_group_update(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.group.update(102, "test")
    assert 0 == result["errcode"]


def test_group_move_user(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.group.move_user("test", 102)
    assert 0 == result["errcode"]


def test_group_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.group.delete(123456)
    assert 0 == result["errcode"]


def test_send_text_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_text(1, "test", account="test")
    assert 0 == result["errcode"]


def test_send_image_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_image(1, "123456")
    assert 0 == result["errcode"]


def test_send_voice_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_voice(1, "123456")
    assert 0 == result["errcode"]


def test_send_video_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_video(1, "123456", "test", "test")
    assert 0 == result["errcode"]


def test_send_music_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_music(
        1, "http://www.qq.com", "http://www.qq.com", "123456", "test", "test"
    )
    assert 0 == result["errcode"]


def test_send_articles_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    articles = [
        {
            "title": "test",
            "description": "test",
            "url": "http://www.qq.com",
            "image": "http://www.qq.com",
        }
    ]
    result = client.message.send_articles(1, articles)
    assert 0 == result["errcode"]


def test_send_card_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_card(1, "123456")
    assert 0 == result["errcode"]


def test_send_mini_program_page(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_mini_program_page(1, {})
    assert 0 == result["errcode"]


def test_send_mass_text_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_mass_text("test", [1])
    assert 0 == result["errcode"]


def test_send_mass_image_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_mass_image("123456", [1])
    assert 0 == result["errcode"]


def test_send_mass_voice_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_mass_voice("test", [1])
    assert 0 == result["errcode"]


def test_send_mass_video_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_mass_video(
        "test", [1], title="title", description="desc"
    )
    assert 0 == result["errcode"]


def test_send_mass_article_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_mass_article("test", [1])
    assert 0 == result["errcode"]


def test_send_mass_card_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.send_mass_card("test", [1])
    assert 0 == result["errcode"]


def test_get_mass_message(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.message.get_mass(201053012)
    assert "SEND_SUCCESS" == result["msg_status"]


def test_create_menu(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.menu.create(
        {"button": [{"type": "click", "name": "test", "key": "test"}]}
    )
    assert 0 == result["errcode"]


def test_get_menu(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    menu = client.menu.get()
    assert "menu" in menu


def test_delete_menu(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.menu.delete()
    assert 0 == result["errcode"]


def test_update_menu(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.menu.update(
        {"button": [{"type": "click", "name": "test", "key": "test"}]}
    )
    assert 0 == result["errcode"]


def test_short_url(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.misc.short_url("http://www.qq.com")
    assert "http://qq.com" == result["short_url"]


def test_get_wechat_ips(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.misc.get_wechat_ips()
    assert ["127.0.0.1"] == result


def test_check_network(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.misc.check_network()
    dns = result["dns"]
    assert [
        {"ip": "111.161.64.40", "real_operator": "UNICOM"},
        {"ip": "111.161.64.48", "real_operator": "UNICOM"},
    ] == dns


def test_get_user_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    openid = "o6_bmjrPTlm6_2sgVt7hMZOPfL2M"
    user = client.user.get(openid)
    assert "Band" == user["nickname"]


def test_get_followers(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.user.get_followers()
    assert 2 == result["total"]
    assert 2 == result["count"]


def test_iter_followers(httpx_mock: HTTPXMock):
    def next_openid_response(request: httpx.Request):
        if "next_openid" in request.url.query.decode("utf-8"):
            content = {"total": 2, "count": 0, "next_openid": ""}
            headers = {"Content-Type": "application/json"}
            return httpx.Response(200, json=content, request=request, headers=headers)
        return custom_response(request)

    httpx_mock.add_callback(next_openid_response)
    client = WeChatClient(app_id, secret)
    users = list(client.user.iter_followers())
    assert 2 == len(users)
    assert "OPENID1" in users
    assert "OPENID2" in users


def test_update_user_remark(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    openid = "openid"
    remark = "test"
    result = client.user.update_remark(openid, remark)
    assert 0 == result["errcode"]


def test_get_user_info_batch(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    user_list = [
        {"openid": "otvxTs4dckWG7imySrJd6jSi0CWE", "lang": "zh-CN"},
        {"openid": "otvxTs_JZ6SEiP0imdhpi50fuSZg", "lang": "zh-CN"},
    ]

    result = client.user.get_batch(user_list)
    assert user_list[0]["openid"] == result[0]["openid"]
    assert "iWithery" == result[0]["nickname"]
    assert user_list[1]["openid"] == result[1]["openid"]


def test_get_user_info_batch_openid_list(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    user_list = ["otvxTs4dckWG7imySrJd6jSi0CWE", "otvxTs_JZ6SEiP0imdhpi50fuSZg"]

    result = client.user.get_batch(user_list)
    assert user_list[0] == result[0]["openid"]
    assert "iWithery" == result[0]["nickname"]
    assert user_list[1] == result[1]["openid"]


def test_get_tag_users(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.tag.get_tag_users(101)
    assert 2 == result["count"]


def test_iter_tag_users(httpx_mock: HTTPXMock):
    def next_openid_response(request: httpx.Request):
        if "user/tag/get" in request.url.path:
            data = json.loads(request.content.decode("utf-8"))
            if not data.get("next_openid"):
                return custom_response(request)
            content = {"count": 0}
            headers = {"Content-Type": "application/json"}
            return httpx.Response(200, json=content, request=request, headers=headers)
        return custom_response(request)

    httpx_mock.add_callback(next_openid_response)
    client = WeChatClient(app_id, secret)
    users = list(client.tag.iter_tag_users(101))
    assert 2 == len(users)
    assert "OPENID1" in users
    assert "OPENID2" in users


def test_create_qrcode(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    data = {
        "expire_seconds": 1800,
        "action_name": "QR_SCENE",
        "action_info": {"scene": {"scene_id": 123}},
    }

    result = client.qrcode.create(data)
    assert 1800 == result["expire_seconds"]


def test_get_qrcode_url_with_str_ticket(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    ticket = "123"
    url = client.qrcode.get_url(ticket)
    assert "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=123" == url


def test_get_qrcode_url_with_dict_ticket(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    ticket = {
        "ticket": "123",
    }
    url = client.qrcode.get_url(ticket)
    assert "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=123" == url


def test_customservice_add_account(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.add_account("test1@test", "test1", "test1")
    assert 0 == result["errcode"]


def test_customservice_update_account(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.update_account("test1@test", "test1", "test1")
    assert 0 == result["errcode"]


def test_customservice_delete_account(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.delete_account(
        "test1@test",
    )
    assert 0 == result["errcode"]


def test_customservice_upload_headimg(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    media_file = io.BytesIO(b"nothing")
    result = client.customservice.upload_headimg("test1@test", media_file)
    assert 0 == result["errcode"]


def test_customservice_get_accounts(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.get_accounts()
    assert 2 == len(result)


def test_customservice_get_online_accounts(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.get_online_accounts()
    assert 2 == len(result)


def test_customservice_create_session(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.create_session("openid", "test1@test")
    assert 0 == result["errcode"]


def test_customservice_close_session(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.close_session("openid", "test1@test")
    assert 0 == result["errcode"]


def test_customservice_get_session(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.get_session("openid")
    assert "test1@test" == result["kf_account"]


def test_customservice_get_session_list(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.get_session_list("test1@test")
    assert 2 == len(result)


def test_customservice_get_wait_case(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.get_wait_case()
    assert 150 == result["count"]


def test_customservice_get_records(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.customservice.get_records(123456789, 987654321, 1)
    assert 2 == len(result["recordlist"])


def test_datacube_get_user_summary(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_user_summary("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_user_cumulate(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_user_cumulate(
        datetime(2014, 12, 6), datetime(2014, 12, 7)
    )
    assert 1 == len(result)


def test_datacube_get_interface_summary(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_interface_summary("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_interface_summary_hour(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_interface_summary_hour("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_article_summary(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_article_summary("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_article_total(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_article_total("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_user_read(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_user_read("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_user_read_hour(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_user_read_hour("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_user_share(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_user_share("2014-12-06", "2014-12-07")
    assert 2 == len(result)


def test_datacube_get_user_share_hour(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_user_share_hour("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_upstream_msg(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_upstream_msg("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_upstream_msg_hour(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_upstream_msg_hour("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_upstream_msg_week(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_upstream_msg_week("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_upstream_msg_month(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_upstream_msg_month("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_upstream_msg_dist(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_upstream_msg_dist("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_upstream_msg_dist_week(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_upstream_msg_dist_week("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_datacube_get_upstream_msg_dist_month(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.datacube.get_upstream_msg_dist_month("2014-12-06", "2014-12-07")
    assert 1 == len(result)


def test_device_get_qrcode_url(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    qrcode_url = client.device.get_qrcode_url(123)
    assert "https://we.qq.com/d/123" == qrcode_url
    qrcode_url = client.device.get_qrcode_url(123, {"a": "a"})
    assert "https://we.qq.com/d/123#YT1h" == qrcode_url


def test_jsapi_get_ticket_response(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.jsapi.get_ticket()
    assert (
        "bxLdikRXVbTPdHSM05e5u5sUoXNKd8-41ZO3MhKoyN5OfkWITDGgnr2fwJ0m9E8NYzWKVZvdVtaUgWvsdshFKA"
        == result["ticket"]
    )
    assert 7200 == result["expires_in"]


def test_jsapi_get_jsapi_signature(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    noncestr = "Wm3WZYTPz0wzccnW"
    ticket = "sM4AOVdWfPE4DxkXGEs8VMCPGGVi4C3VM0P37wVUCFvkVAy_90u5h9nbSlYy3-Sl-HhTdfl2fzFy1AOcHKP7qg"  # NOQA
    timestamp = 1414587457
    url = "http://mp.weixin.qq.com?params=value"
    signature = client.jsapi.get_jsapi_signature(
        noncestr, ticket, timestamp, url
    )
    assert "0f9de62fce790f9a083d5c99e95740ceb90c27ed" == signature

def test_jsapi_get_jsapi_card_ticket(httpx_mock: HTTPXMock):
    """card_ticket 与 jsapi_ticket 的 api 都相同，除了请求参数 type 为 wx_card
    所以这里使用与 `test_jsapi_get_ticket` 相同的测试文件"""
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    ticket = client.jsapi.get_jsapi_card_ticket()
    assert "bxLdikRXVbTPdHSM05e5u5sUoXNKd8-41ZO3MhKoyN5OfkWITDGgnr2fwJ0m9E8NYzWKVZvdVtaUgWvsdshFKA" == ticket
    assert 7200 < client.session.get( f"{client.appid}_jsapi_card_ticket_expires_at")
    assert client.session.get(f"{client.appid}_jsapi_card_ticket") == "bxLdikRXVbTPdHSM05e5u5sUoXNKd8-41ZO3MhKoyN5OfkWITDGgnr2fwJ0m9E8NYzWKVZvdVtaUgWvsdshFKA"

def test_jsapi_card_ext(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    card_ext = json.loads(JsApiCardExt("asdf", openid="2").to_json())
    assert "outer_str" not in card_ext
    assert "code" not in card_ext

    card_ext = json.loads(JsApiCardExt("asdf", code="4", openid="2").to_json())
    assert "code" in card_ext

def test_jsapi_get_jsapi_add_card_params(httpx_mock: HTTPXMock):
    """微信签名测试工具：http://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=cardsign"""
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    nonce_str = "Wm3WZYTPz0wzccnW"
    card_ticket = "sM4AOVdWfPE4DxkXGEs8VMCPGGVi4C3VM0P37wVUCFvkVAy_90u5h9nbSlYy3-Sl-HhTdfl2fzFy1AOcHKP7qg"
    timestamp = "1414587457"
    card_id = "random_card_id"
    code = "random_code"
    openid = "random_openid"

    # 测试最少填写
    card_params = client.jsapi.get_jsapi_add_card_params(
        card_ticket=card_ticket,
        timestamp=timestamp,
        card_id=card_id,
        nonce_str=nonce_str,
    )
    assert JsApiCardExt(
            signature="22dce6bad4db532d4a2ef82ca2ca7bbe1e10ef28",
            nonce_str=nonce_str,
            timestamp=timestamp,
        ) == card_params
    # 测试自定义code
    card_params = client.jsapi.get_jsapi_add_card_params(
        card_ticket=card_ticket,
        timestamp=timestamp,
        card_id=card_id,
        nonce_str=nonce_str,
        code=code,
    )
    assert JsApiCardExt(
            nonce_str=nonce_str,
            timestamp=timestamp,
            code=code,
            signature="2e9c6d12952246e071717d7baeab20c30420b5cd",
        ) == card_params
    # 测试指定用户领取
    card_params = client.jsapi.get_jsapi_add_card_params(
        card_ticket=card_ticket,
        timestamp=timestamp,
        card_id=card_id,
        nonce_str=nonce_str,
        openid=openid,
    )
    assert JsApiCardExt(
            nonce_str=nonce_str,
            timestamp=timestamp,
            openid=openid,
            signature="ded860a5dd4467312764bd86e544ad0579cbfad0",
        ) == card_params
    # 测试指定用户领取且自定义code
    card_params = client.jsapi.get_jsapi_add_card_params(
        card_ticket=card_ticket,
        timestamp=timestamp,
        card_id=card_id,
        nonce_str=nonce_str,
        openid=openid,
        code=code,
    )
    assert JsApiCardExt(
            nonce_str=nonce_str,
            timestamp=timestamp,
            openid=openid,
            code=code,
            signature="950dc1842852457ea573d4d6af34879c1ec093c8",
        ) == card_params
def test_menu_get_menu_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)

    menu_info = client.menu.get_menu_info()
    assert 1 == menu_info["is_menu_open"]

def test_message_get_autoreply_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    autoreply = client.message.get_autoreply_info()
    assert 1 == autoreply["is_autoreply_open"]

def test_shakearound_apply_device_id(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.apply_device_id(1, "test")
    assert 123 == res["apply_id"]

def test_shakearound_update_device(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.update_device("1234", comment="test")
    assert 0 == res["errcode"]

def test_shakearound_bind_device_location(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.bind_device_location(123, 1234)
    assert 0 == res["errcode"]

def test_shakearound_search_device(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.search_device(apply_id=123)
    assert 151 == res["total_count"]
    assert 2 == len(res["devices"])

def test_shakearound_add_page(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.add_page(
        "test", "test", "http://www.qq.com", "http://www.qq.com"
    )
    assert 28840 == res["page_id"]

def test_shakearound_update_page(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.update_page(
        123, "test", "test", "http://www.qq.com", "http://www.qq.com"
    )
    assert 28840 == res["page_id"]

def test_shakearound_delete_page(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.delete_page(123)
    assert 0 == res["errcode"]

def test_shakearound_search_page(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.search_pages(123)
    assert 2 == res["total_count"]
    assert 2 == len(res["pages"])

def test_shakearound_add_material(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    media_file = io.BytesIO(b"nothing")
    res = client.shakearound.add_material(media_file, "icon")
    assert "http://shp.qpic.cn/wechat_shakearound_pic/0/1428377032e9dd2797018cad79186e03e8c5aec8dc/120" ==res["pic_url"]


def test_shakearound_bind_device_pages(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.shakearound.bind_device_pages(123, 1, 1, 1234)
    assert 0 == result["errcode"]

def test_shakearound_get_shake_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.get_shake_info("123456")
    assert 14211 == res["page_id"]
    assert "oVDmXjp7y8aG2AlBuRpMZTb1-cmA" == res["openid"]

def test_shakearound_get_device_statistics(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.get_device_statistics(
        "2015-04-01 00:00:00", "2015-04-17 00:00:00", 1234
    )
    assert 2 == len(res)

def test_shakearound_get_page_statistics(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.get_page_statistics(
        "2015-04-01 00:00:00", "2015-04-17 00:00:00", 1234
    )
    assert 2 == len(res)

def test_material_get_count(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.material.get_count()
    assert 1 == res["voice_count"]
    assert 2 == res["video_count"]
    assert 3 == res["image_count"]
    assert 4 == res["news_count"]

def test_shakearound_get_apply_status(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.shakearound.get_apply_status(1234)
    assert 4 == len(res)

def test_reraise_requests_exception(httpx_mock: HTTPXMock):
    def raise_requests_exception(request: httpx.Request):
         return httpx.Response(404, request=request, content="404 not found")
    httpx_mock.add_callback(raise_requests_exception)
    client = WeChatClient(app_id, secret)

    try:
        client.material.get_count()
    except WeChatClientException as e:
        assert 404, e.response.status_code

def test_wifi_list_shops(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.wifi.list_shops()
    assert 16 == res["totalcount"]
    assert 1 == res["pageindex"]

def test_wifi_get_shop(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.wifi.get_shop(1)
    assert 1 == res["bar_type"]
    assert 2 == res["ap_count"]

def test_wifi_add_device(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.wifi.add_device(
        123, "WX-test", "12345678", "00:1f:7a:ad:5c:a8"
    )
    assert 0 == result["errcode"]

def test_wifi_list_devices(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.wifi.list_devices()
    assert 2 == res["totalcount"]
    assert 1 == res["pageindex"]

def test_wifi_delete_device(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.wifi.delete_device("00:1f:7a:ad:5c:a8")
    assert 0 == result["errcode"]

def test_wifi_get_qrcode_url(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    qrcode_url = client.wifi.get_qrcode_url(123, 0)
    assert "http://www.qq.com" == qrcode_url

def test_wifi_set_homepage(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.wifi.set_homepage(123, 0)
    assert 0 == result["errcode"]

def test_wifi_get_homepage(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.wifi.get_homepage(429620)
    assert 1 == res["template_id"]
    assert "http://wifi.weixin.qq.com/" == res["url"]

def test_wifi_list_statistics(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.wifi.list_statistics("2015-05-01", "2015-05-02")
    assert 2 == len(res)

def test_upload_mass_image(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    media_file = io.BytesIO(b"nothing")
    res = client.media.upload_mass_image(media_file)
    assert "http://mmbiz.qpic.cn/mmbiz/gLO17UPS6FS2xsypf378iaNhWacZ1G1UplZYWEYfwvuU6Ont96b1roYs CNFwaRrSaKTPCUdBK9DgEHicsKwWCBRQ/0" == res

def test_scan_get_merchant_info(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.scan.get_merchant_info()
    assert 8888 == res["verified_firm_code_list"][0]

def test_scan_create_product(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.scan.create_product(
        {
            "keystandard": "ean13",
            "keystr": "6900000000000",
        }
    )
    assert "5g0B4A90aqc" == res["pid"]

def test_scan_publish_product(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.scan.publish_product("ean13", "6900873042720")
    assert 0 == result["errcode"]

def test_scan_unpublish_product(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.scan.unpublish_product("ean13", "6900873042720")
    assert 0 == result["errcode"]

def test_scan_set_test_whitelist(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.scan.set_test_whitelist(["openid1"], ["messense"])
    assert 0 == result["errcode"]

def test_scan_get_product(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.scan.get_product("ean13", "6900873042720")
    assert "brand_info" in result

def test_scan_list_product(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.scan.list_product()
    assert 2 == res["total"]

def test_scan_update_product(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.scan.update_product(
        {
            "keystandard": "ean13",
            "keystr": "6900000000000",
        }
    )
    assert "5g0B4A90aqc" == res["pid"]

def test_scan_clear_product(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    result = client.scan.clear_product("ean13", "6900873042720")
    assert 0 == result["errcode"]

def test_scan_check_ticket(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.scan.check_ticket("Ym1haDlvNXJqY3Ru1")
    assert "otAzGjrS4AYCmeJM1GhEOcHXXTAo" == res["openid"]

def test_change_openid(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)

    res = client.user.change_openid(
        "xxxxx",
        ["oEmYbwN-n24jxvk4Sox81qedINkQ", "oEmYbwH9uVd4RKJk7ZZg6SzL6tTo"],
    )
    assert 2 == len(res)
    assert "o2FwqwI9xCsVadFah_HtpPfaR-X4" == res[0]["new_openid"]
    assert "ori_openid error" == res[1]["err_msg"]

def test_code_to_session(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.wxa.code_to_session("023dUeGW1oeGOZ0JXvHW1SDVFW1dUeGu")
    assert "session_key" in res
    assert "D1ZWEygStjuLCnZ9IN2l4Q==" == res["session_key"]
    assert "o16wA0b4AZKzgVJR3MBwoUdTfU_E" == res["openid"]
    assert "or4zX05h_Ykt4ju0TUfx3CQsvfTo" == res["unionid"]

def test_get_phone_number(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)
    client = WeChatClient(app_id, secret)
    res = client.wxa.get_phone_number("code")
    assert "13123456789" == res["phone_info"]["purePhoneNumber"]

def test_client_expires_at_consistency(httpx_mock: HTTPXMock):
    httpx_mock.add_callback(custom_response)

    from redis import Redis
    from wechatpy.session.redisstorage import RedisStorage

    redis = Redis()
    session = RedisStorage(redis)
    client1 = WeChatClient(app_id, secret, session=session)
    client2 = WeChatClient(app_id, secret, session=session)
    assert client1.expires_at == client2.expires_at
    expires_at = time.time() + 7200
    client1.expires_at = expires_at
    assert client1.expires_at == client2.expires_at == expires_at
