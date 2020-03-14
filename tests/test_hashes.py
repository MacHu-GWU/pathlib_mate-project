# -*- coding: utf-8 -*-

import pytest
from pytest import raises
import hashlib
from pathlib_mate import hashes


def test_exception():
    with raises(ValueError):
        hashes.get_file_fingerprint(__file__, hashlib.md5, nbytes=-1)
    with raises(ValueError):
        hashes.get_file_fingerprint(__file__, hashlib.md5, chunk_size=-1)


def test_get_fingerprint():
    md5_1 = hashes.get_file_fingerprint(__file__, hashlib.md5)
    md5_2 = hashes.get_file_fingerprint(
        __file__, hashlib.md5, chunk_size=1 << 9)
    assert md5_1 == md5_2

    md5_1 = hashes.get_file_fingerprint(
        __file__, hashlib.md5, nbytes=500, chunk_size=128)
    md5_2 = hashes.get_file_fingerprint(
        __file__, hashlib.md5, nbytes=500, chunk_size=1024)
    assert md5_1 == md5_2


def test_all_algo():
    md5 = hashes.md5file(__file__)
    sha256 = hashes.sha256file(__file__)
    sha512 = hashes.sha512file(__file__)
    assert len(set([md5, sha256, sha512])) == 3


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
