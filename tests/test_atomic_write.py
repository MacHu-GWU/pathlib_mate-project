# -*- coding: utf-8 -*-

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

    with DATA_FILE.atomic_open("wb") as f:
        f.write(BINARY)
    with DATA_FILE.atomic_open("rb") as f:
        assert f.read() == BINARY

    with DATA_FILE.atomic_open("w") as f:
        f.write(TEXT)
    with DATA_FILE.atomic_open("r") as f:
        assert f.read() == TEXT


if __name__ == "__main__":
    from pathlib_mate.tests import run_cov_test

    run_cov_test(__file__, "pathlib_mate.mate_tool_box", preview=False)
