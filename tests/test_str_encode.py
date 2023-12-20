# -*- coding: utf-8 -*-

from pathlib_mate import str_encode


def test():
    assert __file__ == str_encode.decode_hexstr(
        str_encode.encode_hexstr(__file__))


if __name__ == "__main__":
    from pathlib_mate.tests import run_cov_test

    run_cov_test(__file__, "pathlib_mate.str_encode", preview=False)
