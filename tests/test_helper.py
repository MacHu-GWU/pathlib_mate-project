# -*- coding: utf-8 -*-

import pytest
from pathlib_mate.helper import ensure_list, repr_data_size


class Path(object):
    def __init__(self, p):
        self.p = p

    def __str__(self):
        return self.p


def test_ensure_list():
    assert ensure_list("a") == ["a", ]
    assert ensure_list(Path(__file__)) == [str(Path(__file__)), ]

    assert ensure_list(["a", ]) == ["a", ]
    assert ensure_list([Path(__file__), ]) == [str(Path(__file__)), ]


def test_repr_data_size():
    assert repr_data_size(1) == "1 B"
    assert repr_data_size(1024) == "1.00 KB"
    assert repr_data_size(1024 ** 2) == "1.00 MB"
    assert repr_data_size(1024 ** 3) == "1.00 GB"
    assert repr_data_size(1024 ** 4) == "1.00 TB"
    assert repr_data_size(1024 ** 5) == "1.00 PB"
    assert repr_data_size(1024 ** 6) == "1.00 EB"
    assert repr_data_size(1024 ** 7) == "1.00 ZB"
    assert repr_data_size(1024 ** 8) == "1.00 YB"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
