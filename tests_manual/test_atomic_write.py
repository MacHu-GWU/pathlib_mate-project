# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest

from pathlib_mate import Path

HERE = Path(__file__).parent
DATA_FILE = Path(HERE, "test.dat")

TEXT = "hello world! "


def clear_data_file():
    if DATA_FILE.exists():
        DATA_FILE.remove()


def setup_module(module):
    clear_data_file()


# def teardown_module(module):
#     clear_data_file()


def test_atomic_write():
    DATA_FILE.atomic_write_text(TEXT, overwrite=True)
    assert DATA_FILE.read_text() == TEXT

    # run this and manually shut down the program, it should not corrupt the file.
    # DATA_FILE.atomic_write_text(TEXT * 100000000, overwrite=True)  # around 1.3GB

    # run this and manually shut down the program, it should not corrupt the file.
    with DATA_FILE.atomic_open("w") as f:
        for _ in range(100000000): # around 1.3GB
            f.write(TEXT)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
