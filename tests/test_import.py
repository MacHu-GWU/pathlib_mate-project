#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


def test():
    import pathlib_mate

    pathlib_mate.Path
    pathlib_mate.WindowsPath
    pathlib_mate.PosixPath
    pathlib_mate.PathCls


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
