# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path

dir_tests = Path.dir_here(__file__)
dir_project_root = dir_tests.parent
dir_pathlib_mate = Path(dir_project_root, "pathlib_mate")
dir_app = Path(dir_tests, "app")
p_this = Path(__file__).absolute()


def clear_all_zip_file_in_tests_dir():
    for p in dir_tests.select_by_ext(".zip"):
        p.remove_if_exists()


def setup_module(module):
    clear_all_zip_file_in_tests_dir()


def teardown_module(module):
    clear_all_zip_file_in_tests_dir()


class TestToolBoxZip(object):
    def test_auto_zip_archive_dst(self):
        p = dir_pathlib_mate._default_zip_dst()
        assert p.dirpath == dir_pathlib_mate.dirpath

        p = p_this._default_zip_dst()
        assert p.dirpath == p_this.dirpath

    def test_make_zip_archive(self):
        dst = dir_tests.append_parts("pathlib_mate_with_dir.zip").abspath
        dir_pathlib_mate.make_zip_archive(dst=dst, verbose=False)

        dst = dir_tests.append_parts("pathlib_mate_without_dir.zip").abspath
        dir_pathlib_mate.make_zip_archive(dst=dst, include_dir=False, compress=False, verbose=False)

        p_this.make_zip_archive(verbose=False)

        # error handling
        # already exists error
        with pytest.raises(OSError):
            dir_pathlib_mate.make_zip_archive(dst=dst, verbose=False)

        # file extension error
        with pytest.raises(ValueError):
            dst = dir_tests.append_parts("pathlib_mate_with_dir.tar").abspath
            dir_pathlib_mate.make_zip_archive(dst=dst, verbose=False)

    def test_backup(self):
        dir_app.backup(verbose=False)

        p_this.backup(verbose=False)


if __name__ == "__main__":
    from pathlib_mate.tests import run_cov_test

    run_cov_test(__file__, "pathlib_mate.mate_tool_box_zip", preview=False)
