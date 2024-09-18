# -*- coding: utf-8 -*-
"""
    wechatpy.messages
    ~~~~~~~~~~~~~~~~~~

    This module defines all the messages you can get from WeChat server
"""

import copy
from typing import Dict, Type

from wechatpy.fields import BaseField, DateTimeField, FieldDescriptor, IntegerField, StringField

MESSAGE_TYPES: Dict[str, Type] = {}
COMPONENT_MESSAGE_TYPES: Dict[str, Type] = {}


def register_message(msg_type: str):
    def register(cls: Type):
        MESSAGE_TYPES[msg_type] = cls
        return cls

    return register


def register_component_message(msg_type: str):
    def register(cls: Type):
        COMPONENT_MESSAGE_TYPES[msg_type] = cls
        return cls

    return register


class MessageMetaClass(type):
    """Metaclass for all messages"""

    def __new__(mcs, name: str, bases: tuple, attrs: dict):
        for b in bases:
            if not hasattr(b, "_fields"):
                continue

            for k, v in b.__dict__.items():
                if k in attrs:
                    continue
                if isinstance(v, FieldDescriptor):
                    attrs[k] = copy.deepcopy(v.field)

        mcs = super().__new__(mcs, name, bases, attrs)
        mcs._fields = {}

        for name, field in mcs.__dict__.items():
            if isinstance(field, BaseField):
                field.add_to_class(mcs, name)
        return mcs


class BaseMessage(metaclass=MessageMetaClass):
    """Base class for all messages and events"""

    type: str = "unknown"
    id: IntegerField = IntegerField("MsgId", 0)
    source: StringField = StringField("FromUserName")
    target: StringField = StringField("ToUserName")
    create_time: DateTimeField = DateTimeField("CreateTime")
    time: IntegerField = IntegerField("CreateTime")

    def __init__(self, message):
        self._data = message

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self._data)})"


@register_message("text")
class TextMessage(BaseMessage):
    """
    文本消息
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
    """

    type: str = "text"
    content: StringField = StringField("Content")


@register_message("image")
class ImageMessage(BaseMessage):
    """
    图片消息
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
    """

    type: str = "image"
    media_id: StringField = StringField("MediaId")
    image: StringField = StringField("PicUrl")


@register_message("voice")
class VoiceMessage(BaseMessage):
    """
    语音消息
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
    """

    type: str = "voice"
    media_id: StringField = StringField("MediaId")
    format: StringField = StringField("Format")
    recognition: StringField = StringField("Recognition")


@register_message("shortvideo")
class ShortVideoMessage(BaseMessage):
    """
    短视频消息
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
    """

    type: str = "shortvideo"
    media_id: StringField = StringField("MediaId")
    thumb_media_id: StringField = StringField("ThumbMediaId")


@register_message("video")
class VideoMessage(BaseMessage):
    """
    视频消息
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
    """

    type: str = "video"
    media_id: StringField = StringField("MediaId")
    thumb_media_id: StringField = StringField("ThumbMediaId")


@register_message("location")
class LocationMessage(BaseMessage):
    """
    地理位置消息
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
    """

    type: str = "location"
    location_x: StringField = StringField("Location_X")
    location_y: StringField = StringField("Location_Y")
    scale: StringField = StringField("Scale")
    label: StringField = StringField("Label")

    @property
    def location(self):
        return self.location_x, self.location_y


@register_message("link")
class LinkMessage(BaseMessage):
    """
    链接消息
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html
    """

    type: str = "link"
    title: StringField = StringField("Title")
    description: StringField = StringField("Description")
    url: StringField = StringField("Url")


@register_message("miniprogrampage")
class MiniProgramPageMessage(BaseMessage):
    """
    小程序卡片消息
    详情请参阅
    https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/customer-message/receive.html#小程序卡片消息
    """

    type: str = "miniprogrampage"
    app_id: StringField = StringField("AppId")
    title: StringField = StringField("Title")
    page_path: StringField = StringField("PagePath")
    thumb_url: StringField = StringField("ThumbUrl")
    thumb_media_id: StringField = StringField("ThumbMediaId")


class UnknownMessage(BaseMessage):
    """未知消息类型"""

    pass


class BaseComponentMessage(metaclass=MessageMetaClass):
    """Base class for all component messages and events"""

    type: str = "unknown"
    appid: StringField = StringField("AppId")
    create_time: DateTimeField = DateTimeField("CreateTime")

    def __init__(self, message):
        self._data = message

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self._data)})"


@register_component_message("component_verify_ticket")
class ComponentVerifyTicketMessage(BaseComponentMessage):
    """
    component_verify_ticket协议
    """

    type: str = "component_verify_ticket"
    verify_ticket: StringField = StringField("ComponentVerifyTicket")


@register_component_message("unauthorized")
class ComponentUnauthorizedMessage(BaseComponentMessage):
    """
    取消授权通知
    """

    type: str = "unauthorized"
    authorizer_appid: StringField = StringField("AuthorizerAppid")


@register_component_message("authorized")
class ComponentAuthorizedMessage(BaseComponentMessage):
    """
    新增授权通知
    """

    type: str = "authorized"
    authorizer_appid: StringField = StringField("AuthorizerAppid")
    authorization_code: StringField = StringField("AuthorizationCode")
    authorization_code_expired_time: StringField = StringField("AuthorizationCodeExpiredTime")
    pre_auth_code: StringField = StringField("PreAuthCode")


@register_component_message("updateauthorized")
class ComponentUpdateAuthorizedMessage(BaseComponentMessage):
    """
    更新授权通知
    """

    type: str = "updateauthorized"
    authorizer_appid: StringField = StringField("AuthorizerAppid")
    authorization_code: StringField = StringField("AuthorizationCode")
    authorization_code_expired_time: StringField = StringField("AuthorizationCodeExpiredTime")
    pre_auth_code: StringField = StringField("PreAuthCode")


class ComponentUnknownMessage(BaseComponentMessage):
    """
    未知通知
    """

    type: str = "unknown"
