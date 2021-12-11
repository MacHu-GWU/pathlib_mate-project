# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest

from pathlib_mate import PathCls as Path

HERE = Path(__file__).parent
DATA_FILE = Path(HERE, "test.dat")

TEXT = "hello world! "
BINARY = TEXT.encode("utf-8")


def clear_data_file():
    if DATA_FILE.exists():
        DATA_FILE.remove()


def setup_module(module):
    clear_data_file()


def teardown_module(module):
    clear_data_file()


def test_atomic_write():
    DATA_FILE.write_bytes(BINARY)
    assert DATA_FILE.read_bytes() == BINARY

    DATA_FILE.write_text(TEXT)
    assert DATA_FILE.read_text() == TEXT

    DATA_FILE.atomic_write_bytes(BINARY, overwrite=True)
    assert DATA_FILE.read_bytes() == BINARY

    DATA_FILE.atomic_write_text(TEXT, overwrite=True)
    assert DATA_FILE.read_text() == TEXT


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
