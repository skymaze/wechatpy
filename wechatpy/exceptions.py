# -*- coding: utf-8 -*-
"""
    wechatpy.exceptions
    ~~~~~~~~~~~~~~~~~~~~

    Basic exceptions definition.
"""
from typing import Any, Optional


class WeChatException(Exception):
    """Base exception for wechatpy"""

    def __init__(self, errcode: int, errmsg: str) -> None:
        """
        :param errcode: Error code
        :param errmsg: Error message
        """
        self.errcode = errcode
        self.errmsg = errmsg

    def __str__(self) -> str:
        s = f"Error code: {self.errcode}, message: {self.errmsg}"
        return s

    def __repr__(self) -> str:
        _repr = f"{self.__class__.__name__}({self.errcode}, {self.errmsg})"
        return _repr


class WeChatClientException(WeChatException):
    """WeChat API client exception class"""

    def __init__(
        self,
        errcode: int,
        errmsg: str,
        client: Optional[Any] = None,
        request: Optional[Any] = None,
        response: Optional[Any] = None,
    ) -> None:
        super().__init__(errcode, errmsg)
        self.client = client
        self.request = request
        self.response = response


class InvalidSignatureException(WeChatException):
    """Invalid signature exception class"""

    def __init__(self, errcode: int = -40001, errmsg: str = "Invalid signature") -> None:
        super().__init__(errcode, errmsg)


class APILimitedException(WeChatClientException):
    """WeChat API call limited exception class"""

    pass


class InvalidAppIdException(WeChatException):
    """Invalid app_id exception class"""

    def __init__(self, errcode: int = -40005, errmsg: str = "Invalid AppId") -> None:
        super().__init__(errcode, errmsg)


class InvalidMchIdException(WeChatException):
    """Invalid mch_id exception class"""

    def __init__(self, errcode: int = -40006, errmsg: str = "Invalid MchId") -> None:
        super().__init__(errcode, errmsg)


class WeChatOAuthException(WeChatClientException):
    """WeChat OAuth API exception class"""

    pass


class WeChatComponentOAuthException(WeChatClientException):
    """WeChat Component OAuth API exception class"""

    pass


class WeChatPayException(WeChatClientException):
    """WeChat Pay API exception class"""

    def __init__(
        self,
        return_code: str,
        result_code: Optional[str] = None,
        return_msg: Optional[str] = None,
        errcode: Optional[int] = None,
        errmsg: Optional[str] = None,
        client: Optional[Any] = None,
        request: Optional[Any] = None,
        response: Optional[Any] = None,
    ) -> None:
        super().__init__(errcode, errmsg, client, request, response)
        self.return_code = return_code
        self.result_code = result_code
        self.return_msg = return_msg

    def __str__(self) -> str:
        _str = f"Error code: {self.return_code}, message: {self.return_msg}. Pay Error code: {self.errcode}, message: {self.errmsg}"
        return _str

    def __repr__(self) -> str:
        _repr = f"{self.__class__.__name__}({self.return_code}, {self.return_msg}). Pay({self.errcode}, {self.errmsg})"
        return _repr
