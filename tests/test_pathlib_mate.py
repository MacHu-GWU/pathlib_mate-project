#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
from datetime import datetime
from pathlib_mate import Path
from pathlib_mate.pathlib import _preprocess


def test_preprocess():
    assert _preprocess("a") == ["a", ]
    assert _preprocess(Path(__file__)) == [str(Path(__file__)), ]
    
    assert _preprocess(["a", ]) == ["a", ]
    assert _preprocess([Path(__file__),]) == [str(Path(__file__)), ]
    
    
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
    

def test_moveto():
    p = Path(Path(__file__).dirpath, "testdir", "test.txt")
    p1 = Path(Path(__file__).dirpath, "testdir", "test1.txt")
    p2 = Path(Path(__file__).dirpath, "testdir", "test1.cfg")
    p3 = Path(Path(__file__).dirpath, "test1.cfg")

    assert p1.exists() is False
      
    p.moveto(new_fname="test1")
    assert p.exists() is False
    assert p1.exists() is True
          
    p1.moveto(new_ext=".cfg")
    assert p1.exists() is False
    assert p2.exists() is True
      
    p2.moveto(new_dirpath=p2.parent.dirpath)
    assert p2.exists() is False
    assert p3.exists() is True
      
    p3.rename(p)
    assert p3.exists() is False
    assert p.exists() is True
    
    p = p.moveto(new_fname="test1")
    assert p.exists() is True
    
    p = p.moveto(new_ext=".cfg")
    assert p.exists() is True
     
    p = p.moveto(new_dirpath=p2.parent.dirpath)
    assert p.exists() is True
    
    p = p.moveto(new_dirname="pathlib_mate")
    assert p.exists() is True 
    
    p = p.moveto(
        new_dirpath=Path(Path(__file__).dirpath, "testdir"),
        new_fname="test",
        new_ext=".txt",
    )
    assert p.exists() is True
    
    p = p.moveto(new_abspath=p.abspath)
    assert p.exists() is True

    with pytest.raises(EnvironmentError):
        p.moveto(new_abspath=__file__)
        
        
def test_copyto():
    p_test = Path(Path(__file__).dirpath, "testdir", "test.txt")
    p_test2 = p_test.copyto(new_fname="test2")
    
    assert p_test.exists() is True
    assert p_test2.exists() is True
    
    p_test2.remove()
    assert p_test2.exists() is False
    
    with pytest.raises(EnvironmentError):
        p_test.copyto(new_abspath=__file__)


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
        assert p.ext == ".jpg"


def test_sort_by():
    p_list = Path.sort_by_size(path.select_file())
    assert is_increasing([p.size for p in p_list])
      
    p_list = Path.sort_by_size(path.select_file(), reverse=True)
    assert is_decreasing([p.size for p in p_list])


def test_print_big_dir():
    """Not needed.
    """
#     path.print_big_dir()


def test_print_big_file():
    """Not needed.
    """
#     path.print_big_file()
    

def test_print_big_dir_and_big_file():
    """Not needed.
    """
#     path.print_big_dir_and_big_file()
    

if __name__ == "__main__":
    import os
    pytest.main(["--tb=native", "-s", os.path.basename(__file__)])