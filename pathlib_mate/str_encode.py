# -*- coding: utf-8 -*-

"""
utility functions for string encoding.
"""

import binascii


def encode_hexstr(text):
    """
    Convert any utf-8 string to hex string.

    :type text: str

    :rtype: str

    Example::

        >>> encode_hexstr("/home/your_username")
        2f686f6d652f796f75725f757365726e616d65

    **中文文档**

    将任意 utf-8 字符串编码为 16 进制字符串。
    """
    return binascii.b2a_hex(text.encode("utf-8")).decode("utf-8")


def decode_hexstr(text):
    """
    Reverse operation of :func:`encode_hexstr`.

    :type text: str

    :rtype: str

    **中文文档**

    将 16 进制字符串解码为原字符串。
    """
    return binascii.a2b_hex(text.encode("utf-8")).decode("utf-8")
