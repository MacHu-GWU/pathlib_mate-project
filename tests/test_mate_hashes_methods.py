# -*- coding: utf-8 -*-

from pathlib_mate import Path


class TestHashesMethods(object):
    def test(self):
        p = Path(__file__)
        assert (
            len(
                {
                    p.md5,
                    p.get_partial_md5(nbytes=1 << 20),
                    p.sha256,
                    p.get_partial_sha256(nbytes=1 << 20),
                    p.sha512,
                    p.get_partial_sha512(nbytes=1 << 20),
                }
            )
            == 3
        )


if __name__ == "__main__":
    from pathlib_mate.tests import run_cov_test

    run_cov_test(__file__, "pathlib_mate.mate_hashes_methods", preview=False)
