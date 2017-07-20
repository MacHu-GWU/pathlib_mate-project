#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import pytest
from datetime import datetime
from pathlib_mate import Path
from pathlib_mate.pathlib import _preprocess


def setup_module(module):
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
    reserved = ["app", "test_all.py", "test_pathlib_mate.py"]
    for p in Path(__file__).parent.iterdir():
        if p.basename not in reserved:
            if p.is_dir():
                shutil.rmtree(p.abspath)
            else:
                os.remove(p.abspath)


def test_preprocess():
    assert _preprocess("a") == ["a", ]
    assert _preprocess(Path(__file__)) == [str(Path(__file__)), ]

    assert _preprocess(["a", ]) == ["a", ]
    assert _preprocess([Path(__file__), ]) == [str(Path(__file__)), ]


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


def test_attribute():
    p = Path(__file__).absolute()
    assert isinstance(p.abspath, str)
    assert isinstance(p.dirpath, str)
    assert p.abspath == __file__
    assert p.dirpath == os.path.dirname(__file__)
    assert p.dirname == os.path.basename(os.path.dirname(__file__))
    assert p.basename == os.path.basename(__file__)
    assert p.fname == os.path.splitext(os.path.basename(__file__))[0]
    assert p.ext == os.path.splitext(__file__)[1]
    assert len(p.md5) == 32
    assert len(p.get_partial_md5(1)) == 32
    assert p.size >= 1024
    assert p.parent.dirsize >= 32768
    assert p.ctime >= 1451624400.0
    assert p.mtime >= 1451624400.0
    assert p.atime >= 1451624400.0
    assert p.modify_datetime >= datetime(2016, 1, 1)
    assert p.access_datetime >= datetime(2016, 1, 1)
    assert p.create_datetime >= datetime(2016, 1, 1)
    assert "KB" in p.size_in_text


def test_drop_parts():
    p = Path(__file__)
    p1 = p.drop_parts(1)
    assert len(p.parts) == len(p1.parts) + 1
    p1 = p.drop_parts(2)
    assert len(p.parts) == len(p1.parts) + 2


def test_append_parts():
    p = Path(__file__).parent
    p1 = p.append_parts("a")
    assert len(p.parts) == len(p1.parts) - 1
    p1 = p.append_parts("a", "b")
    assert len(p.parts) == len(p1.parts) - 2


def test_change():
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

    # because __file__ is OS dependent, so don't test this.
#     p1 = p.change(new_dirpath=r"C:\User")
#     assert p1.ext == p.ext
#     assert p1.fname == p.fname
#     assert p1.dirname == "User"
#     assert p1.dirpath == r"C:\User"


def test_moveto():
    # move file
    p_file = Path(__file__).change(new_basename="file_to_move.txt")
    p_file_new = p_file.moveto(new_ext=".rst")  # change extension
    assert p_file.exists() is False
    assert p_file_new.exists() is True
    p_file = p_file_new.moveto(new_ext=".txt")  # move back

    # move file into not existing folder
    with pytest.raises(EnvironmentError):
        p_file.moveto(new_dirname="NOT EXIST FOLDER")

    # move file into not existsing folder, and create the folder
    p_file_new = p_file.moveto(
        new_abspath=Path(__file__).parent.
        append_parts("NOT EXIST FOLDER", "file_to_move.txt"),
        makedirs=True,
    )
    p_file = p_file_new.moveto(new_abspath=p_file.abspath)

    # move directory
    p_dir = Path(__file__).change(new_basename="wow")
    n_files = p_dir.n_file
    p_dir_new = p_dir.moveto(new_basename="wow1")
    assert n_files == p_dir_new.n_file
    p_dir = p_dir_new.moveto(new_basename="wow")


def test_copyto():
    # copy file
    p_file = Path(__file__).change(new_basename="file_to_copy.txt")
    p_file_new = p_file.copyto(new_ext=".rst")  # change extension
    assert p_file.exists() is True
    assert p_file_new.exists() is True

    # copy file into not existing folder
    with pytest.raises(EnvironmentError):
        p_file.copyto(new_dirname="NOT EXIST FOLDER")

    # copy file into not existsing folder, and create the folder
    p_file_new = p_file.copyto(
        new_abspath=Path(__file__).parent.
        append_parts("NOT EXIST FOLDER", "file_to_copy.txt"),
        makedirs=True,
    )

    # copy directory
    p_dir = Path(__file__).change(new_basename="wow")
    n_files = p_dir.n_file
    p_dir_new = p_dir.moveto(new_basename="wow1")
    assert n_files == p_dir_new.n_file


# Default test dir, the project dir: 'pathlib_mate-project'
path = Path(".").absolute().parent


def test_select():
    def filters(p):
        if p.fname.startswith("f"):
            return True
        else:
            return False

    for p in path.select(filters):
        assert p.fname.startswith("f")


def test_select_file():
    for p in path.select_file():
        assert p.is_file()


def test_select_dir():
    for p in path.select_dir():
        assert p.is_dir()


def test_select_by_ext():
    for p in path.select_by_ext(".Bat"):
        assert p.ext.lower() == ".bat"


def test_select_by_pattern_in_fname():
    for p in path.select_by_pattern_in_fname("test"):
        assert "test" in p.fname


def test_select_by_size():
    for p in path.select_by_size(max_size=1000):
        assert p.size <= 1000


def test_select_image():
    for p in path.select_image():
        assert p.ext in [".jpg", ".png", ".gif"]


def test_sort_by():
    p_list = Path.sort_by_size(path.select_file())
    assert is_increasing([p.size for p in p_list])

    p_list = Path.sort_by_size(path.select_file(), reverse=True)
    assert is_decreasing([p.size for p in p_list])


def test_is_empty():
    assert Path(__file__).is_empty() is False
    assert Path(__file__).parent.is_empty() is False


def test_print_big_dir():
    """Not need in travis.
    """
#     path.print_big_dir()


def test_print_big_file():
    """Not need in travis.
    """
#     path.print_big_file()


def test_print_big_dir_and_big_file():
    """Not need in travis.
    """
#     path.print_big_dir_and_big_file()


def test_file_stat():
    """Not need in travis.
    """
    p = Path(__file__).parent
    stat = p.file_stat()

    assert stat["file"] >= 6
    assert stat["dir"] >= 2
    assert stat["size"] >= 11000

    all_stat = p.file_stat_for_all()
    assert all_stat[p.abspath] == stat


def test_mirror_to():
    """Not need in travis.
    """
    path = Path("app")
#     path.mirror_to("mirror")


def test_backup():
    """Not need in travis.
    """
    p = Path(__file__).parent
#     p.backup(ignore_size_larger_than=1000, case_sensitive=False)


def test_autopep8():
    """Not need in travis.
    """
    p = Path(__file__).change(new_basename="app")
#     p.autopep8()


def test_trail_space():
    """Not need in travis.
    """
    p = Path(__file__).change(new_basename="app")
#     p.trail_space()


if __name__ == "__main__":
    import os
    pytest.main(["--tb=native", "-s", os.path.basename(__file__)])
