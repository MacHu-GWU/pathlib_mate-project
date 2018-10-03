#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import str_encode


def test():
    assert __file__ == str_encode.decode_hexstr(str_encode.encode_hexstr(__file__))


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
