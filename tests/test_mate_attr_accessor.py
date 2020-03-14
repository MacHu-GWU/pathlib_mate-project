# -*- coding: utf-8 -*-

import pytest
from pytest import raises

import os
import six
from datetime import datetime
from pathlib_mate.pathlib2 import Path


class TestAttrAccessor(object):
    def test(self):
        HEXSTR_CHARSET = set("0123456789abcdef")

        def assert_hexstr(text):
            assert len(HEXSTR_CHARSET.union(set(text))) <= 16

        p = Path(__file__).absolute()
        assert isinstance(p.abspath, six.string_types)
        assert isinstance(p.dirpath, six.string_types)

        assert p.abspath == __file__
        assert p.dirpath == os.path.dirname(__file__)
        assert p.dirname == os.path.basename(os.path.dirname(__file__))
        assert p.basename == os.path.basename(__file__)
        assert p.fname == os.path.splitext(os.path.basename(__file__))[0]
        assert p.ext == os.path.splitext(__file__)[1]

        assert_hexstr(p.abspath_hexstr)
        assert_hexstr(p.dirpath_hexstr)
        assert_hexstr(p.dirname_hexstr)
        assert_hexstr(p.basename_hexstr)
        assert_hexstr(p.fname_hexstr)

        assert len(p.md5) == 32
        assert len(p.get_partial_md5(1)) == 32
        assert p.size >= 1024

        ts_2016_1_1 = (datetime(2016, 1, 1) -
                       datetime(1970, 1, 1)).total_seconds()
        assert p.ctime >= ts_2016_1_1
        assert p.mtime >= ts_2016_1_1
        assert p.atime >= ts_2016_1_1
        assert p.modify_datetime >= datetime(2016, 1, 1)
        assert p.access_datetime >= datetime(2016, 1, 1)
        assert p.create_datetime >= datetime(2016, 1, 1)
        assert "KB" in p.size_in_text
        assert p.get_partial_md5(
            nbytes=10) == "52ee8aa6c482035e08afabda0f0f8dd8"
        with raises(ValueError):
            p.get_partial_md5(-1)

    def test_contains(self):
        p = Path(__file__).absolute()
        assert p in p.parent
        assert p.abspath in p.parent  # string also works
        assert p.parent not in p

    def test_iter(self):
        p = Path(__file__).absolute()
        for ancestor in p:
            assert p in ancestor


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
