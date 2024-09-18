# -*- coding: utf-8 -*-
"""
    wechatpy.fields
    ~~~~~~~~~~~~~~~~

    This module defines some useful field types for parse WeChat messages
"""

import time
from datetime import datetime
import base64
import copy
from typing import Any, Callable, Optional, Dict, Union, List

from wechatpy.utils import to_text, to_binary, ObjectDict, timezone

default_timezone = timezone("Asia/Shanghai")


class FieldDescriptor:
    def __init__(self, field: "BaseField") -> None:
        self.field = field
        self.attr_name = field.name

    def __get__(self, instance: Any, instance_type: Optional[type] = None) -> Any:
        if instance is not None:
            value = instance._data.get(self.attr_name)
            if value is None:
                value = copy.deepcopy(self.field.default)
                instance._data[self.attr_name] = value
            if isinstance(value, dict):
                value = ObjectDict(value)
            if (
                value
                and not isinstance(value, (dict, list, tuple))
                and callable(self.field.converter)
            ):
                value = self.field.converter(value)
            return value
        return self.field

    def __set__(self, instance: Any, value: Any) -> None:
        instance._data[self.attr_name] = value


class BaseField:
    converter: Optional[Callable[..., Any]] = None

    def __init__(self, name: str, default: Optional[Any] = None) -> None:
        self.name = name
        self.default = default

    def to_xml(self, value: Any) -> str:
        raise NotImplementedError()

    @classmethod
    def from_xml(cls, value: str) -> Any:
        raise NotImplementedError()

    def __getitem__(self, item: Any) -> Any:
        """有时微信会推嵌套的消息，mypy 的类型检查会愣住，所以加个函数敷衍一下 mypy"""
        raise NotImplementedError()

    def __repr__(self) -> str:
        _repr = f"{self.__class__.__name__}({repr(self.name)})"
        return _repr

    def add_to_class(self, klass: type, name: str) -> None:
        self.klass = klass
        klass._fields[name] = self
        setattr(klass, name, FieldDescriptor(self))


class StringField(BaseField):
    def __to_text(self, value: Any) -> str:
        return to_text(value)

    converter = __to_text

    def to_xml(self, value: Any) -> str:
        value = self.converter(value)
        return f"<{self.name}><![CDATA[{value}]]></{self.name}>"

    @classmethod
    def from_xml(cls, value: str) -> str:
        return value


class IntegerField(BaseField):
    converter = int

    def to_xml(self, value: Any) -> str:
        value = self.converter(value) if value is not None else self.default
        return f"<{self.name}>{value}</{self.name}>"

    @classmethod
    def from_xml(cls, value: str) -> int:
        return cls.converter(value)


class DateTimeField(BaseField):
    def __converter(self, value: Any) -> datetime:
        v = int(value)
        return datetime.fromtimestamp(v, tz=default_timezone)

    converter = __converter

    def to_xml(self, value: datetime) -> str:
        value = time.mktime(datetime.timetuple(value))
        value = int(value)
        return f"<{self.name}>{value}</{self.name}>"

    @classmethod
    def from_xml(cls, value: str) -> datetime:
        return cls.converter(None, value)


class FloatField(BaseField):
    converter = float

    def to_xml(self, value: Any) -> str:
        value = self.converter(value) if value is not None else self.default
        return f"<{self.name}>{value}</{self.name}>"

    @classmethod
    def from_xml(cls, value: str) -> float:
        return cls.converter(value)


class ImageField(StringField):
    def to_xml(self, value: Any) -> str:
        value = self.converter(value)
        return f"""<Image>
        <MediaId><![CDATA[{value}]]></MediaId>
        </Image>"""

    @classmethod
    def from_xml(cls, value: Dict[str, str]) -> str:
        return value["MediaId"]


class VoiceField(StringField):
    def to_xml(self, value: Any) -> str:
        value = self.converter(value)
        return f"""<Voice>
        <MediaId><![CDATA[{value}]]></MediaId>
        </Voice>"""

    @classmethod
    def from_xml(cls, value: Dict[str, str]) -> str:
        return value["MediaId"]


class VideoField(StringField):
    def to_xml(self, value: Dict[str, Union[str, Dict[str, str]]]) -> str:
        kwargs = dict(media_id=self.converter(value["media_id"]))
        content = "<MediaId><![CDATA[{media_id}]]></MediaId>"
        if "title" in value:
            kwargs["title"] = self.converter(value["title"])
            content += "<Title><![CDATA[{title}]]></Title>"
        if "description" in value:
            kwargs["description"] = self.converter(value["description"])
            content += "<Description><![CDATA[{description}]]></Description>"
        tpl = f"""<Video>{content}</Video>"""
        return tpl.format(**kwargs)

    @classmethod
    def from_xml(
        cls, value: Dict[str, Union[str, Dict[str, str]]]
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        rv = dict(media_id=value["MediaId"])
        if "Title" in value:
            rv["title"] = value["Title"]
        if "Description" in value:
            rv["description"] = value["Description"]
        return rv


class MusicField(StringField):
    def to_xml(self, value: Dict[str, Union[str, Dict[str, str]]]) -> str:
        kwargs = dict(thumb_media_id=self.converter(value["thumb_media_id"]))
        content = "<ThumbMediaId><![CDATA[{thumb_media_id}]]></ThumbMediaId>"
        if "title" in value:
            kwargs["title"] = self.converter(value["title"])
            content += "<Title><![CDATA[{title}]]></Title>"
        if "description" in value:
            kwargs["description"] = self.converter(value["description"])
            content += "<Description><![CDATA[{description}]]></Description>"
        if "music_url" in value:
            kwargs["music_url"] = self.converter(value["music_url"])
            content += "<MusicUrl><![CDATA[{music_url}]]></MusicUrl>"
        if "hq_music_url" in value:
            kwargs["hq_music_url"] = self.converter(value["hq_music_url"])
            content += "<HQMusicUrl><![CDATA[{hq_music_url}]]></HQMusicUrl>"
        tpl = f"""<Music>{content}</Music>"""
        return tpl.format(**kwargs)

    @classmethod
    def from_xml(
        cls, value: Dict[str, Union[str, Dict[str, str]]]
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        rv = dict(thumb_media_id=value["ThumbMediaId"])
        if "Title" in value:
            rv["title"] = value["Title"]
        if "Description" in value:
            rv["description"] = value["Description"]
        if "MusicUrl" in value:
            rv["music_url"] = value["MusicUrl"]
        if "HQMusicUrl" in value:
            rv["hq_music_url"] = value["HQMusicUrl"]
        return rv


class ArticlesField(StringField):
    def to_xml(self, articles: List[Dict[str, str]]) -> str:
        article_count = len(articles)
        items = []
        for article in articles:
            title = self.converter(article.get("title", ""))
            description = self.converter(article.get("description", ""))
            image = self.converter(article.get("image", ""))
            url = self.converter(article.get("url", ""))
            item = f"""<item>
            <Title><![CDATA[{title}]]></Title>
            <Description><![CDATA[{description}]]></Description>
            <PicUrl><![CDATA[{image}]]></PicUrl>
            <Url><![CDATA[{url}]]></Url>
            </item>"""
            items.append(item)
        items_str = "\n".join(items)
        return f"""<ArticleCount>{article_count}</ArticleCount>
        <Articles>{items_str}</Articles>"""

    @classmethod
    def from_xml(cls, value: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
        return [
            dict(
                title=item["Title"],
                description=item["Description"],
                image=item["PicUrl"],
                url=item["Url"],
            )
            for item in value["item"]
        ]


class TaskCardField(StringField):
    def to_xml(self, value: Any) -> str:
        value = self.converter(value)
        return f"""<TaskCard>
            <ReplaceName><![CDATA[{value}]]></ReplaceName>
        </TaskCard>"""

    @classmethod
    def from_xml(cls, value: Dict[str, str]) -> str:
        return value["ReplaceName"]


class Base64EncodeField(StringField):
    def __base64_encode(self, text: str) -> str:
        return to_text(base64.b64encode(to_binary(text)))

    converter = __base64_encode


class Base64DecodeField(StringField):
    def __base64_decode(self, text: str) -> str:
        return to_text(base64.b64decode(to_binary(text)))

    converter = __base64_decode


class HardwareField(StringField):
    def to_xml(self, value: Optional[Dict[str, str]] = None) -> str:
        value = value or {"view": "myrank", "action": "ranklist"}
        return f"""<{self.name}>
        <MessageView><![CDATA[{value.get("view")}]]></MessageView>
        <MessageAction><![CDATA[{value.get("action")}]]></MessageAction>
        </{self.name}>
"""
