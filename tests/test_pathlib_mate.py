#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
from datetime import datetime
from pathlib_mate import Path
 
 
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
    assert p.dirname == os.path.basename(os.path.dirname(__file__))
    assert p.basename == os.path.basename(__file__)
    assert p.fname == os.path.splitext(os.path.basename(__file__))[0]
    assert p.ext == os.path.splitext(__file__)[1]
    assert len(p.md5()) == 32
    assert p.size >= 1024
    assert p.ctime >= 1451624400.0
    assert p.mtime >= 1451624400.0
    assert p.atime >= 1451624400.0
    assert p.modify_datetime >= datetime(2016, 1, 1)
    assert p.access_datetime >= datetime(2016, 1, 1)
    assert p.create_datetime >= datetime(2016, 1, 1)
    assert "KB" in p.size_in_text
    
 
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

 
def test_sort_by():
    p_list = Path.sort_by_size(path.select_file())
    assert is_increasing([p.size for p in p_list])
      
    p_list = Path.sort_by_size(path.select_file(), reverse=True)
    assert is_decreasing([p.size for p in p_list])
    
    
if __name__ == "__main__":
    import os
    pytest.main(["--tb=native", "-s", os.path.basename(__file__)])