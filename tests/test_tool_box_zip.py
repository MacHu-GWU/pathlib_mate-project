#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path


def teardown_module(module):
    """
    Remove temp file and dir for test.
    """
    p_this = Path(__file__)
    to_remove_list = list(p_this.parent.select_by_ext(".zip"))
    for p in to_remove_list:
        if p.exists():
            p.remove()


class TestToolBoxZip(object):
    def test_make_zip_archive(self):
        p = Path(__file__).parent.change(new_basename="pathlib_mate")
        dst = Path(__file__).change(new_basename="pathlib_mate.zip").abspath
        p.make_zip_archive(dst=dst, verbose=False)

        p = Path(__file__).parent.change(new_basename="setup.py")
        dst = Path(__file__).change(new_basename="setup.py.zip").abspath
        p.make_zip_archive(dst=dst, verbose=False)

    def test_backup(self):
        p = Path(__file__).change(new_basename="app")
        p.backup()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
