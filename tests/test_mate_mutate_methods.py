# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from pytest import raises
import shutil
import platform
from pathlib_mate.pathlib2 import Path


def setup_module(module):
    """
    Create temp file and dir for test.

    - create a new folder ``/wow``
    - create two file `/`wow/file_to_move.txt``, ``wow/file_to_copy.txt``
    """

    p = Path(__file__).change(new_basename="app")
    try:
        shutil.copytree(p.abspath, p.change(new_basename="wow").abspath)
    except Exception as e:
        pass

    p = Path(__file__).change(new_basename="file_to_move.txt")
    with open(p.abspath, "wb") as f:
        f.write("test file".encode("utf-8"))

    p = Path(__file__).change(new_basename="file_to_copy.txt")
    with open(p.abspath, "wb") as f:
        f.write("test file".encode("utf-8"))


def teardown_module(module):
    """
    Remove temp file and dir for test.
    """
    p_this = Path(__file__)
    to_remove_list = [
        p_this.change(new_basename="file_to_copy.txt"),
        p_this.change(new_basename="file_to_copy.rst"),
        p_this.change(new_basename="file_to_move.txt"),
        p_this.change(new_basename="NOT-EXIST-FOLDER-MOVETO"),
        p_this.change(new_basename="NOT-EXIST-FOLDER-COPYTO"),
        p_this.change(new_basename="wow"),
        p_this.change(new_basename="wow1"),
    ]
    for p in to_remove_list:
        if p.is_file():
            p.remove()
        elif p.is_dir():
            shutil.rmtree(p.abspath)


class TestMutateMethods(object):
    def test_drop_parts(self):
        p = Path(__file__)
        p1 = p.drop_parts(1)
        assert len(p.parts) == len(p1.parts) + 1
        p1 = p.drop_parts(2)
        assert len(p.parts) == len(p1.parts) + 2

    def test_append_parts(self):
        p = Path(__file__).parent
        p1 = p.append_parts("a")
        assert len(p.parts) == len(p1.parts) - 1
        p1 = p.append_parts("a", "b")
        assert len(p.parts) == len(p1.parts) - 2

    def test_change(self):
        p = Path(__file__)

        p1 = p.change(new_ext=".txt")
        assert p1.ext == ".txt"
        assert p1.fname == p.fname
        assert p1.dirname == p.dirname
        assert p1.dirpath == p.dirpath

        p1 = p.change(new_fname="hello")
        assert p1.ext == p.ext
        assert p1.fname == "hello"
        assert p1.dirname == p.dirname
        assert p1.dirpath == p.dirpath

        p1 = p.change(new_basename="hello.txt")
        assert p1.ext == ".txt"
        assert p1.fname == "hello"
        assert p1.dirname == p.dirname
        assert p1.dirpath == p.dirpath

        p1 = p.change(new_dirname="folder")
        assert p1.ext == p.ext
        assert p1.fname == p.fname
        assert p1.dirname == "folder"
        assert p1.dirpath.endswith("folder")

        with raises(ValueError):
            p.change(new_dirpath="new_dirpath", new_dirname="folder")
        with raises(ValueError):
            p.change(new_basename="hello.txt", new_fname="hello")
        with raises(ValueError):
            p.change(new_basename="hello.txt", new_ext="hello")

        # because __file__ is OS dependent, so don't test this.
        system_name = platform.system()
        if system_name == "Windows":
            p1 = p.change(new_dirpath="C:\\User")
            assert p1.ext == p.ext
            assert p1.fname == p.fname
            assert p1.dirname == "User"
            assert p1.dirpath == "C:\\User"

        elif system_name in ["Darwin", "Linux"]:
            p1 = p.change(new_dirpath="/Users")
            assert p1.ext == p.ext
            assert p1.fname == p.fname
            assert p1.dirname == "Users"
            assert p1.dirpath == "/Users"

    def test_moveto(self):
        # move file
        p_file = Path(__file__).change(new_basename="file_to_move.txt")
        p_file_new = p_file.moveto(new_ext=".rst")  # change extension
        assert p_file.exists() is False
        assert p_file_new.exists() is True
        p_file = p_file_new.moveto(new_ext=".txt")  # move back

        # move file into not existing folder
        with pytest.raises(EnvironmentError):
            p_file.moveto(new_dirname="NOT-EXIST-FOLDER-MOVETO")

        # move file into not existsing folder, and create the folder
        p_file_new = p_file.moveto(
            new_abspath=Path(__file__).parent.
                append_parts("NOT-EXIST-FOLDER-MOVETO", "file_to_move.txt"),
            makedirs=True,
        )
        p_file = p_file_new.moveto(new_abspath=p_file.abspath)

        # move directory
        p_dir = Path(__file__).change(new_basename="wow")
        n_files = p_dir.n_file
        n_dir = p_dir.n_dir

        p_dir_new = p_dir.moveto(new_basename="wow1")
        assert n_files == p_dir_new.n_file
        assert n_dir == p_dir_new.n_dir

        p_dir = p_dir_new.moveto(new_basename="wow")

    def test_copyto(self):
        # copy file
        p_file = Path(__file__).change(new_basename="file_to_copy.txt")
        p_file_new = p_file.change(new_ext=".rst")
        assert p_file_new.exists() is False

        p_file_new = p_file.copyto(new_ext=".rst")
        assert p_file.exists() is True
        assert p_file_new.exists() is True

        # copy file into not existing folder
        with pytest.raises(Exception):
            p_file.copyto(new_dirname="NOT-EXIST-FOLDER-COPYTO")

        # copy file into not existing folder, and create the folder
        p_file_new = p_file.change(
            new_abspath=Path(__file__).parent.append_parts(
                "NOT-EXIST-FOLDER-COPYTO", "file_to_copy.txt"),
        )
        assert p_file_new.exists() is False
        assert p_file_new.parent.exists() is False

        p_file_new = p_file.copyto(
            new_abspath=Path(__file__).parent.append_parts(
                "NOT-EXIST-FOLDER-COPYTO", "file_to_copy.txt"),
            makedirs=True,
        )
        assert p_file_new.exists() is True

        # copy directory
        p_dir = Path(__file__).change(new_basename="wow")
        n_files = p_dir.n_file
        p_dir_new = p_dir.moveto(new_basename="wow1")
        assert n_files == p_dir_new.n_file


class TestRemoveFileOrDir(object):
    dir_here = Path(__file__).parent
    path_to_move_file = Path(dir_here, "to_move_file.txt")
    path_to_move_dir = Path(dir_here, "to_move_dir")
    path_to_move_dir_file = Path(dir_here, "to_move_dir", "to_move_file.txt")

    def setup_method(self, method):
        self.path_to_move_file.write_text("test")
        self.path_to_move_dir.mkdir_if_not_exists()
        self.path_to_move_dir_file.write_text("test")

    # def teardown_method(self, method):
    def test_remove(self):
        self.path_to_move_file.remove()
        assert self.path_to_move_file.exists() is False

        with pytest.raises(Exception):
            self.path_to_move_file.remove()

    def test_remove_if_exists(self):
        # remove a file
        self.path_to_move_file.remove_if_exists()
        assert self.path_to_move_file.exists() is False
        self.path_to_move_file.remove_if_exists()

        # remove a dir
        self.path_to_move_dir.remove_if_exists()
        assert self.path_to_move_dir.exists() is False
        self.path_to_move_dir.remove_if_exists()

    def test_dir_here(self):
        dir_here = Path.dir_here(__file__)
        assert dir_here.basename == "tests"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
