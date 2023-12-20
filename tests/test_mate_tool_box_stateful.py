# -*- coding: utf-8 -*-

import shutil
from pathlib_mate import Path


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

        dst = Path(__file__).change(
            new_basename="app-backup-%s.zip" % random.randint(1, 9999)
        )
        assert dst.exists() is False
        p.backup(dst.abspath, ignore_size_larger_than=1000, case_sensitive=False)
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

    def test_temp_cwd(self):
        p = Path(__file__).parent.parent.parent
        assert Path.cwd() != p
        with p.temp_cwd():
            assert Path.cwd() == p
        assert Path.cwd() != p


if __name__ == "__main__":
    from pathlib_mate.tests import run_cov_test

    run_cov_test(__file__, "pathlib_mate.mate_tool_box", preview=False)
