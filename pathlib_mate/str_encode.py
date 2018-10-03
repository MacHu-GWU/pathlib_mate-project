# -*- coding: utf-8 -*-


import binascii


def encode_hexstr(text):
    """
    Convert any utf-8 string to hex string.

    **中文文档**

    将任意utf-8字符串编码为16进制字符串。
    """
    return binascii.b2a_hex(text.encode("utf-8")).decode("utf-8")


def decode_hexstr(text):
    """
    Reverse operation of :func:`encode_hexstr`.

    **中文文档**

    将16进制字符串解码为原字符串。
    """
    return binascii.a2b_hex(text.encode("utf-8")).decode("utf-8")
