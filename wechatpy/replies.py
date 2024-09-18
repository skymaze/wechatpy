# -*- coding: utf-8 -*-
"""
    wechatpy.replies
    ~~~~~~~~~~~~~~~~~~
    This module defines all kinds of replies you can send to WeChat

    :copyright: (c) 2014 by messense.
    :license: MIT, see LICENSE for more details.
"""

import time
import xmltodict

from wechatpy.fields import (
    StringField,
    IntegerField,
    ImageField,
    VoiceField,
    VideoField,
    MusicField,
    ArticlesField,
    Base64EncodeField,
    HardwareField,
)
from wechatpy.messages import BaseMessage, MessageMetaClass
from typing import Dict, Any, Optional, List, Union


REPLY_TYPES: Dict[str, Any] = {}


def register_reply(reply_type: str):
    def register(cls):
        REPLY_TYPES[reply_type] = cls
        return cls

    return register


class BaseReply(metaclass=MessageMetaClass):
    """Base class for all replies"""

    source: StringField = StringField("FromUserName")
    target: StringField = StringField("ToUserName")
    time: IntegerField = IntegerField("CreateTime", time.time())
    type: str = "unknown"

    def __init__(self, **kwargs: Any):
        self._data: Dict[str, Any] = {}
        message: Optional[BaseMessage] = kwargs.pop("message", None)
        if message and isinstance(message, BaseMessage):
            if "source" not in kwargs:
                kwargs["source"] = message.target
            if "target" not in kwargs:
                kwargs["target"] = message.source
            if hasattr(message, "agent") and "agent" not in kwargs:
                kwargs["agent"] = message.agent
        if "time" not in kwargs:
            kwargs["time"] = time.time()
        for name, value in kwargs.items():
            field = self._fields.get(name)
            if field:
                self._data[field.name] = value
            else:
                setattr(self, name, value)

    def render(self) -> str:
        """Render reply from Python object to XML string"""
        nodes = []
        msg_type = f"<MsgType><![CDATA[{self.type}]]></MsgType>"
        nodes.append(msg_type)
        for name, field in self._fields.items():
            value = getattr(self, name, field.default)
            node_xml = field.to_xml(value)
            nodes.append(node_xml)
        data = "\n".join(nodes)
        return f"<xml>\n{data}\n</xml>"

    def __str__(self) -> str:
        return self.render()


@register_reply("empty")
class EmptyReply(BaseReply):
    """
    回复空串

    微信服务器不会对此作任何处理，并且不会发起重试
    """

    def __init__(self):
        pass

    def render(self) -> str:
        return ""


@register_reply("text")
class TextReply(BaseReply):
    """
    文本回复
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
    """

    type: str = "text"
    content: StringField = StringField("Content")


@register_reply("image")
class ImageReply(BaseReply):
    """
    图片回复
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
    """

    type: str = "image"
    image: ImageField = ImageField("Image")

    @property
    def media_id(self) -> str:
        return self.image

    @media_id.setter
    def media_id(self, value: str) -> None:
        self.image = value


@register_reply("voice")
class VoiceReply(BaseReply):
    """
    语音回复
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
    """

    type: str = "voice"
    voice: VoiceField = VoiceField("Voice")

    @property
    def media_id(self) -> str:
        return self.voice

    @media_id.setter
    def media_id(self, value: str) -> None:
        self.voice = value


@register_reply("video")
class VideoReply(BaseReply):
    """
    视频回复
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
    """

    type: str = "video"
    video: VideoField = VideoField("Video", {})

    @property
    def media_id(self) -> str:
        return self.video.get("media_id")

    @media_id.setter
    def media_id(self, value: str) -> None:
        video = self.video
        video["media_id"] = value
        self.video = video

    @property
    def title(self) -> str:
        return self.video.get("title")

    @title.setter
    def title(self, value: str) -> None:
        video = self.video
        video["title"] = value
        self.video = video

    @property
    def description(self) -> str:
        return self.video.get("description")

    @description.setter
    def description(self, value: str) -> None:
        video = self.video
        video["description"] = value
        self.video = video


@register_reply("music")
class MusicReply(BaseReply):
    """
    音乐回复
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
    """

    type: str = "music"
    music: MusicField = MusicField("Music", {})

    @property
    def thumb_media_id(self) -> str:
        return self.music.get("thumb_media_id")

    @thumb_media_id.setter
    def thumb_media_id(self, value: str) -> None:
        music = self.music
        music["thumb_media_id"] = value
        self.music = music

    @property
    def title(self) -> str:
        return self.music.get("title")

    @title.setter
    def title(self, value: str) -> None:
        music = self.music
        music["title"] = value
        self.music = music

    @property
    def description(self) -> str:
        return self.music.get("description")

    @description.setter
    def description(self, value: str) -> None:
        music = self.music
        music["description"] = value
        self.music = music

    @property
    def music_url(self) -> str:
        return self.music.get("music_url")

    @music_url.setter
    def music_url(self, value: str) -> None:
        music = self.music
        music["music_url"] = value
        self.music = music

    @property
    def hq_music_url(self) -> str:
        return self.music.get("hq_music_url")

    @hq_music_url.setter
    def hq_music_url(self, value: str) -> None:
        music = self.music
        music["hq_music_url"] = value
        self.music = music


@register_reply("news")
class ArticlesReply(BaseReply):
    """
    图文回复
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
    """

    type: str = "news"
    articles: ArticlesField = ArticlesField("Articles", [])

    def add_article(self, article: Dict[str, Any]) -> None:
        if len(self.articles) == 10:
            raise AttributeError("Can't add more than 10 articles in an ArticlesReply")
        articles = self.articles
        articles.append(article)
        self.articles = articles


@register_reply("transfer_customer_service")
class TransferCustomerServiceReply(BaseReply):
    """
    将消息转发到多客服
    详情请参阅
    https://developers.weixin.qq.com/doc/offiaccount/Customer_Service/Forwarding_of_messages_to_service_center.html
    """

    type: str = "transfer_customer_service"


@register_reply("device_text")
class DeviceTextReply(BaseReply):
    type: str = "device_text"
    device_type: StringField = StringField("DeviceType")
    device_id: StringField = StringField("DeviceID")
    session_id: StringField = StringField("SessionID")
    content: Base64EncodeField = Base64EncodeField("Content")


@register_reply("device_event")
class DeviceEventReply(BaseReply):
    type: str = "device_event"
    event: StringField = StringField("Event")
    device_type: StringField = StringField("DeviceType")
    device_id: StringField = StringField("DeviceID")
    session_id: StringField = StringField("SessionID")
    content: Base64EncodeField = Base64EncodeField("Content")


@register_reply("device_status")
class DeviceStatusReply(BaseReply):
    type: str = "device_status"
    device_type: StringField = StringField("DeviceType")
    device_id: StringField = StringField("DeviceID")
    status: IntegerField = IntegerField("DeviceStatus")


@register_reply("hardware")
class HardwareReply(BaseReply):
    type: str = "hardware"
    func_flag: IntegerField = IntegerField("FuncFlag", 0)
    hardware: HardwareField = HardwareField("HardWare")


def create_reply(reply: Union[str, List[Dict[str, Any]], BaseReply, None], message: Optional[BaseMessage] = None, render: bool = False) -> Optional[BaseReply]:
    """
    Create a reply quickly
    """
    r: Optional[BaseReply] = None
    if not reply:
        r = EmptyReply()
    elif isinstance(reply, BaseReply):
        r = reply
        if message:
            r.source = message.target
            r.target = message.source
    elif isinstance(reply, str):
        r = TextReply(message=message, content=reply)
    elif isinstance(reply, (tuple, list)):
        if len(reply) > 10:
            raise AttributeError("Can't add more than 10 articles in an ArticlesReply")
        r = ArticlesReply(message=message, articles=reply)
    if r and render:
        return r.render()
    return r


def deserialize_reply(xml: str, update_time: bool = False) -> BaseReply:
    """
    反序列化被动回复
    :param xml: 待反序列化的xml
    :param update_time: 是否用当前时间替换xml中的时间
    :raises ValueError: 不能辨识的reply xml
    :rtype: wechatpy.replies.BaseReply
    """
    if not xml:
        return EmptyReply()

    try:
        reply_dict = xmltodict.parse(xml)["xml"]
        msg_type = reply_dict["MsgType"]
    except (xmltodict.expat.ExpatError, KeyError):
        raise ValueError("bad reply xml")
    if msg_type not in REPLY_TYPES:
        raise ValueError("unknown reply type")

    cls = REPLY_TYPES[msg_type]
    kwargs = {}
    for attr, field in cls._fields.items():
        if field.name in reply_dict:
            str_value = reply_dict[field.name]
            kwargs[attr] = field.from_xml(str_value)

    if update_time:
        kwargs["time"] = time.time()

    return cls(**kwargs)
