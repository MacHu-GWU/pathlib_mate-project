# -*- coding: utf-8 -*-

import hashlib

DEFAULT_CHUNK_SIZE = 1 << 6


def get_text_fingerprint(text, hash_meth, encoding="utf-8"):  # pragma: no cover
    """
    Use default hash method to return hash value of a piece of string
    default setting use 'utf-8' encoding.
    """
    m = hash_meth()
    m.update(text.encode(encoding))
    return m.hexdigest()


def get_file_fingerprint(abspath, hash_meth, nbytes=0, chunk_size=DEFAULT_CHUNK_SIZE):
    if nbytes < 0:
        raise ValueError("chunk_size cannot smaller than 0")
    if chunk_size < 1:
        raise ValueError("chunk_size cannot smaller than 1")
    if (nbytes > 0) and (nbytes < chunk_size):
        chunk_size = nbytes

    m = hash_meth()
    with open(abspath, "rb") as f:
        if nbytes:  # use first n bytes
            have_reads = 0
            while True:
                have_reads += chunk_size
                if have_reads > nbytes:
                    n = nbytes - (have_reads - chunk_size)
                    if n:
                        data = f.read(n)
                        m.update(data)
                    break
                else:
                    data = f.read(chunk_size)
                    m.update(data)
        else:  # use entire content
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                m.update(data)

    return m.hexdigest()


def md5file(abspath, nbytes=0, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Return md5 hash value of a piece of a file

    Estimate processing time on:

    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0 or None,
      hash all file

    CPU = i7-4600U 2.10GHz - 2.70GHz, RAM = 8.00 GB
    1 second can process 0.25GB data

    - 0.59G - 2.43 sec
    - 1.3G - 5.68 sec
    - 1.9G - 7.72 sec
    - 2.5G - 10.32 sec
    - 3.9G - 16.0 sec
    """
    return get_file_fingerprint(abspath, hashlib.md5, nbytes=nbytes, chunk_size=chunk_size)


def sha256file(abspath, nbytes=0, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Return sha256 hash value of a piece of a file

    Estimate processing time on:

    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0 or None,
      hash all file
    """
    return get_file_fingerprint(abspath, hashlib.sha256, nbytes=nbytes, chunk_size=chunk_size)


def sha512file(abspath, nbytes=0, chunk_size=DEFAULT_CHUNK_SIZE):
    """
    Return sha512 hash value of a piece of a file

    Estimate processing time on:

    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0 or None,
      hash all file
    """
    return get_file_fingerprint(abspath, hashlib.sha512, nbytes=nbytes, chunk_size=chunk_size)
