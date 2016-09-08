#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import pytest

from filetool.files import WinFile, FileCollection
from pathlib_mate import Path


path = Path(".").absolute().parent


def test_performance_metadata():
    WinFile.use_regular_init()
     
    st = time.clock()
    for winfile in FileCollection.from_path(path.abspath).iterfiles():
        winfile.size_on_disk
    elapse1 = time.clock() - st
    
    st = time.clock()    
    for p in path.select():
        p.size
    elapse2 = time.clock() - st
    
    assert elapse1 > elapse2        
    

if __name__ == "__main__":
    import os
    pytest.main(["--tb=native", "-s", os.path.basename(__file__)])