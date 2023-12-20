# -*- coding: utf-8 -*-

from pathlib_mate import Path
from pathlib import Path as PathlibPath


def test_convert():
    p = PathlibPath(Path(__file__))
    assert str(p) == __file__
    assert isinstance(p, PathlibPath)

    p = Path(PathlibPath(__file__))
    assert str(p) == __file__
    assert isinstance(p, Path)


if __name__ == "__main__":
    from pathlib_mate.tests import run_cov_test

    run_cov_test(__file__, "pathlib_mate.mate_tool_box", preview=False)
