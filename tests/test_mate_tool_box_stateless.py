# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from pathlib_mate import Path


class TestToolBoxStateless(object):
    def test_dir_fingerprint(self):
        p = Path(Path(__file__).dirpath)
        assert p.dir_md5 == p.dir_md5
        assert p.dir_sha256 == p.dir_sha256
        assert p.dir_sha512 == p.dir_sha512

    def test_is_empty(self):
        assert Path(__file__).is_empty() is False
        assert Path(__file__).parent.is_empty() is False
        with raises(Exception):
            assert Path("THIS-FILE-NOT-EXISTS.txt").is_empty()

    def test_auto_complete_choices(self):
        p = Path(__file__).change(new_basename="te")
        for p in p.auto_complete_choices():
            assert p.basename.lower().startswith("te")

        p = Path(__file__).parent
        for p1 in p.auto_complete_choices():
            assert p1 in p

    def test_print_big_file(self):
        """
        Not need in travis.
        """
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project
        path.print_big_file()
        path.print_big_dir()

    def test_print_big_dir_and_big_file(self):
        """
        Not need in travis.
        """
        path = Path(__file__).absolute().parent.parent  # pathlibm_mate-project
        path.print_big_dir_and_big_file()

    def test_dir_stat_attribute(self):
        p = Path(__file__).change(new_basename="app")
        assert p.n_file >= 4
        assert p.n_subfile >= 3
        assert p.n_dir == 1
        assert p.n_subdir == 1

    def test_file_stat(self):
        """
        Not need in travis.
        """
        p = Path(__file__).parent
        stat = p.file_stat()
        assert stat["file"] >= 14
        assert stat["dir"] >= 2
        assert stat["size"] >= 32000

        all_stat = p.file_stat_for_all()
        assert all_stat[p.abspath] == stat


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
