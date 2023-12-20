# -*- coding: utf-8 -*-

from .vendor import six


def ensure_str(value):
    """
    Ensure value is string.
    """
    if isinstance(value, six.string_types):
        return value
    else:
        return six.text_type(value)


def ensure_list(path_or_path_list):
    """
    Pre-process input argument, whether if it is:

    1. abspath
    2. Path instance
    3. string
    4. list or set of any of them

    It returns list of path.

    :return path_or_path_list: always return list of path in string

    **中文文档**

    预处理输入参数。
    """
    if isinstance(path_or_path_list, (tuple, list, set)):
        return [ensure_str(path) for path in path_or_path_list]
    else:
        return [ensure_str(path_or_path_list), ]


MAGNITUDE_OF_DATA = {
    i: v
    for i, v in enumerate(["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"])
}


def repr_data_size(
    size_in_bytes,
    precision=2,
):
    """
    Return human readable string represent of a file size. Doesn't support
    size greater than 1YB.

    For example:
    - 100 bytes => 100 B
    - 100,000 bytes => 97.66 KB
    - 100,000,000 bytes => 95.37 MB
    - 100,000,000,000 bytes => 93.13 GB
    - 100,000,000,000,000 bytes => 90.95 TB
    - 100,000,000,000,000,000 bytes => 88.82 PB
    - and more ...

    Magnitude of data::

        1000         kB    kilobyte
        1000 ** 2    MB    megabyte
        1000 ** 3    GB    gigabyte
        1000 ** 4    TB    terabyte
        1000 ** 5    PB    petabyte
        1000 ** 6    EB    exabyte
        1000 ** 7    ZB    zettabyte
        1000 ** 8    YB    yottabyte

    :type size_in_bytes: int
    :type precision: int
    :rtype: str
    """
    if size_in_bytes < 1024:
        return "%s B" % size_in_bytes

    index = 0
    while 1:
        index += 1
        size_in_bytes, mod = divmod(size_in_bytes, 1024)
        if size_in_bytes < 1024:
            break
    template = "{0:.%sf} {1}" % precision
    s = template.format(size_in_bytes + mod / 1024.0, MAGNITUDE_OF_DATA[index])
    return s


def parse_data_size(s):
    """
    Parse human readable string representing a file size. Doesn't support
    size greater than 1YB.

    Examples::

        >>> parse_data_size("3.43 MB")
        3596615
        >>> parse_data_size("2_512.4 MB")
        2634442342
        >>> parse_data_size("2,512.4 MB")
        2634442342

    :type s: str
    :rtype: int
    """
    s = s.strip()

    # split digits and
    digits = set("01234567890_,.")
    digit_parts = list()
    ind = 0
    for ind, c in enumerate(s):
        if c in digits:
            digit_parts.append(c)
        else:
            break
    digit = "".join(digit_parts)
    digit = digit.replace("_", "").replace(",", "")
    digit = float(digit)

    unit_part = s[ind:].strip()

    unit_ind = None
    for ind, unit in MAGNITUDE_OF_DATA.items():
        if unit_part.upper() == unit:
            unit_ind = ind
            break

    if unit_ind is None:
        raise ValueError

    unit = 1024 ** unit_ind
    return int(digit * unit)
