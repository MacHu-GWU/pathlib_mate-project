#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import shutil
from pathlib_mate.pathlib2 import Path


def teardown_module(module):
    """
    Remove temp file and dir for test.
    """
    p_this = Path(__file__)
    to_remove_list = [
        p_this.change(new_basename="mirror"),
    ]
    for p in p_this.parent.select_by_ext(".zip"):
        to_remove_list.append(p)

    for p in to_remove_list:
        if p.is_file():
            p.remove()
        elif p.is_dir():
            shutil.rmtree(p.abspath)


class TestToolBoxStateful(object):
    def test_make_zip_archive(self):
        p = Path(__file__).change(new_basename="app")
        p.make_zip_archive()

    def test_mirror_to(self):
        """
        Not need in travis.
        """
        p = Path(__file__).change(new_basename="app")
        dst = Path(__file__).change(new_basename="mirror")
        p.mirror_to(dst.abspath)

    def test_backup(self):
        """
        Not need in travis.
        """
        import random
        p = Path(__file__).change(new_basename="app")

        dst = Path(__file__) \
            .change(new_basename="app-backup-%s.zip" % random.randint(1, 9999))
        assert dst.exists() is False
        p.backup(dst.abspath, ignore_size_larger_than=1000,
                 case_sensitive=False)
        assert dst.exists() is True

    def test_autopep8(self):
        """
        Not need in travis.
        """
        p = Path(__file__).change(new_basename="app")
        p.autopep8()

    def test_trail_space(self):
        """
        Not need in travis.
        """
        p = Path(__file__).change(new_basename="app")
        p.trail_space()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
