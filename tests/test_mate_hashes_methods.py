# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path


class TestHashesMethods(object):
    def test(self):
        p = Path(__file__)
        assert len({
            p.md5, p.get_partial_md5(nbytes=1 << 20),
            p.sha256, p.get_partial_sha256(nbytes=1 << 20),
            p.sha512, p.get_partial_sha512(nbytes=1 << 20),
        }) == 3


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
