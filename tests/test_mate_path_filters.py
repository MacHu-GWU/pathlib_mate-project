#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from pathlib_mate.pathlib2 import Path


def is_increasing(array):
    if len(array) >= 2:
        for i, j in zip(array[:-1], array[1:]):
            if i > j:
                return False
    else:
        raise ValueError("array size has to be greater than 1.")
    return True


def is_decreasing(array):
    if len(array) >= 2:
        for i, j in zip(array[:-1], array[1:]):
            if i < j:
                return False
    else:
        raise ValueError("array size has to be greater than 1.")
    return True


class TestPathFilters(object):
    def test_assert_is_file_and_exists(self):
        Path(__file__).assert_is_file_and_exists()
        with raises(Exception):
            Path(__file__).parent.assert_is_file_and_exists()
        with raises(Exception):
            Path("THIS-FILE-NOT-EXIST").assert_is_file_and_exists()

    def test_assert_is_dir_and_exists(self):
        Path(__file__).parent.assert_is_dir_and_exists()
        with raises(Exception):
            Path(__file__).assert_is_dir_and_exists()
        with raises(Exception):
            Path("THIS-FILE-NOT-EXIST").assert_is_dir_and_exists()

    def test_assert_exists(self):
        with raises(Exception):
            Path("THIS-FILE-NOT-EXIST").assert_exists()

    def test_select(self):
        def filters(p):
            if p.fname.startswith("f"):
                return True
            else:
                return False

        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project
        for p in path.select(filters):
            assert p.fname.startswith("f")

    def test_select_file(self):
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project
        for p in path.select_file():
            assert p.is_file()

    def test_select_dir(self):
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project
        for p in path.select_dir():
            assert p.is_dir()

    def test_select_by_ext(self):
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project
        for p in path.select_by_ext(".Bat"):
            assert p.ext.lower() == ".bat"

    def test_select_by_pattern_in_fname(self):
        path = Path(__file__).absolute().parent  # pathlibm_mate-project/tests

        for p in path.select_by_pattern_in_fname("test", case_sensitive=True):
            assert "test" in p.fname

        for p in path.select_by_pattern_in_fname("TEST", case_sensitive=False):
            assert "test" in p.fname.lower()

    def test_select_by_pattern_in_abspath(self):
        path = Path(__file__).absolute().parent  # pathlibm_mate-project/tests

        for p in path.select_by_pattern_in_abspath("test", case_sensitive=True):
            assert "test" in p.abspath

        for p in path.select_by_pattern_in_abspath("TEST", case_sensitive=False):
            assert "test" in p.abspath.lower()

    def test_select_by_time(self):
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project

        for p in path.select_by_atime(min_time=0):
            p.atime >= 0

        for p in path.select_by_ctime(min_time=0):
            p.ctime >= 0

        for p in path.select_by_mtime(min_time=0):
            p.mtime >= 0

    def test_select_by_size(self):
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project

        for p in path.select_by_size(max_size=1000):
            assert p.size <= 1000

    def test_select_image(self):
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project

        for p in path.select_image():
            assert p.ext in [".jpg", ".png", ".gif", ".svg"]

    def test_sort_by(self):
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project

        p_list = Path.sort_by_size(path.select_file())
        assert is_increasing([p.size for p in p_list])

        p_list = Path.sort_by_size(path.select_file(), reverse=True)
        assert is_decreasing([p.size for p in p_list])

    def test_dirsize(self):
        p = Path(__file__).parent
        assert p.parent.dirsize >= 32768


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
