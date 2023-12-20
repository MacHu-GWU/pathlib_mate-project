# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


def test():
    import pathlib_mate

    _ = pathlib_mate.Path
    _ = pathlib_mate.WindowsPath
    _ = pathlib_mate.PosixPath
    _ = pathlib_mate.PathCls


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
