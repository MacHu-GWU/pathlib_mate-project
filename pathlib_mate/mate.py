#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import hashlib
import binascii
from datetime import datetime

from .pkg import six, autopep8


def _preprocess(path_or_path_list):
    """
    Preprocess input argument, whether if it is:

    1. abspath
    2. Path instance
    3. string
    4. list or set of any of them

    It returns list of path.

    :return path_or_path_list: always return list of path in string

    **中文文档**

    预处理输入参数。
    """
    if isinstance(path_or_path_list, (list, set)):
        path_or_path_list = [str(path) for path in path_or_path_list]
        return path_or_path_list
    else:
        path_or_path_list = [path_or_path_list, ]
        return _preprocess(path_or_path_list)


def repr_data_size(size_in_bytes, precision=2):
    """
    Return human readable string represent of a file size. Doesn"t support
    size greater than 1EB.

    For example:

    - 100 bytes => 100 B
    - 100,000 bytes => 97.66 KB
    - 100,000,000 bytes => 95.37 MB
    - 100,000,000,000 bytes => 93.13 GB
    - 100,000,000,000,000 bytes => 90.95 TB
    - 100,000,000,000,000,000 bytes => 88.82 PB
    ...

    Magnitude of data::

        1000         kB    kilobyte
        1000 ** 2    MB    megabyte
        1000 ** 3    GB    gigabyte
        1000 ** 4    TB    terabyte
        1000 ** 5    PB    petabyte
        1000 ** 6    EB    exabyte
        1000 ** 7    ZB    zettabyte
        1000 ** 8    YB    yottabyte
    """
    if size_in_bytes < 1024:
        return "%s B" % size_in_bytes

    magnitude_of_data = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    index = 0
    while 1:
        index += 1
        size_in_bytes, mod = divmod(size_in_bytes, 1024)
        if size_in_bytes < 1024:
            break
    template = "{0:.%sf} {1}" % precision
    s = template.format(size_in_bytes + mod / 1024.0, magnitude_of_data[index])
    return s


def md5file(abspath, nbytes=0):
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
    m = hashlib.md5()
    with open(abspath, "rb") as f:
        if nbytes:
            data = f.read(nbytes)
            if data:
                m.update(data)
        else:
            while True:
                data = f.read(4 * 1 << 16)  # only use first 4GB data
                if not data:
                    break
                m.update(data)
    return m.hexdigest()


def sha256file(abspath, nbytes=0):
    """
    Return sha256 hash value of a piece of a file

    Estimate processing time on:

    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0 or None,
      hash all file
    """
    m = hashlib.sha256()
    with open(abspath, "rb") as f:
        if nbytes:
            data = f.read(nbytes)
            if data:
                m.update(data)
        else:
            while True:
                data = f.read(4 * 1 << 16)  # only use first 4GB data
                if not data:
                    break
                m.update(data)
    return m.hexdigest()


def sha512file(abspath, nbytes=0):
    """
    Return sha512 hash value of a piece of a file

    Estimate processing time on:

    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0 or None,
      hash all file
    """
    m = hashlib.sha512()
    with open(abspath, "rb") as f:
        if nbytes:
            data = f.read(nbytes)
            if data:
                m.update(data)
        else:
            while True:
                data = f.read(4 * 1 << 16)  # only use first 4GB data
                if not data:
                    break
                m.update(data)
    return m.hexdigest()


def encode_hexstr(text):
    """
    Convert any utf-8 string to hex string.

    **中文文档**

    将任意utf-8字符串编码为16进制字符串。
    """
    return binascii.b2a_hex(text.encode("utf-8")).decode("utf-8")


def decode_hexstr(text):
    """
    Reverse operation of :func:`encode_hexstr`.

    **中文文档**

    将16进制字符串解码为原字符串。
    """
    return binascii.a2b_hex(text.encode("utf-8")).decode("utf-8")


class PathlibMatePath(object):
    """
    Pathlib mate customized methods, properties.
    """

    def assert_is_file_and_exists(self):
        """
        Assert it is a directory and exists in file system.
        """
        if not self.is_file():
            msg = "'%s' is not a file or doesn't exists!" % self
            raise EnvironmentError(msg)

    def assert_is_dir_and_exists(self):
        """
        Assert it is a directory and exists in file system.
        """
        if not self.is_dir():
            msg = "'%s' is not a file or doesn't exists!" % self
            raise EnvironmentError(msg)

    def assert_exists(self):
        """
        Assert it exists.
        """
        if not self.exists():
            msg = "'%s' doesn't exists!" % self
            raise EnvironmentError(msg)

    # --- property methods that returns a value ---
    @property
    def abspath(self):
        r"""
        Absolute path.

        Example: ``C:\User\admin\readme.txt``
        """
        return self.absolute().__str__()

    @property
    def abspath_hexstr(self):
        """
        Return absolute path in hex string.
        """
        return encode_hexstr(self.abspath)

    @property
    def dirpath(self):
        r"""
        Parent dir full absolute path.

        Example: ``C:\User\admin``
        """
        return self.parent.abspath

    @property
    def dirpath_hexstr(self):
        """
        Return dir full absolute path in hex string.
        """
        return encode_hexstr(self.dirpath)

    @property
    def dirname(self):
        """
        Parent dir name.

        Example: ``admin``
        """
        return self.parent.name

    @property
    def dirname_hexstr(self):
        """
        Parent dir name in hex string.
        """
        return encode_hexstr(self.dirname)

    @property
    def basename(self):
        """
        File name with extension, path is not included.

        Example: ``readme.txt``
        """
        return self.name

    @property
    def basename_hexstr(self):
        """
        File name with extension in hex string.
        """
        return encode_hexstr(self.basename)

    @property
    def fname(self):
        """
        File name without extension.

        Example: ``readme``
        """
        return self.stem

    @property
    def fname_hexstr(self):
        """
        File name in hex string.
        """
        return encode_hexstr(self.fname)

    @property
    def ext(self):
        """
        File extension. If it's a dir, then return empty str.

        Example: ``.txt``
        """
        return self.suffix

    def get_partial_md5(self, nbytes):
        """
        Return md5 check sum of first n bytes of this file.
        """
        if nbytes in [0, None]:
            raise ValueError("'nbytes' has to be positive integer.")
        return md5file(self.abspath, nbytes)

    @property
    def md5(self):
        """
        Return md5 check sum of this file.
        """
        return md5file(self.abspath)

    def get_partial_sha256(self, nbytes):
        """
        Return sha256 check sum of first n bytes of this file.
        """
        if nbytes in [0, None]:
            raise ValueError("'nbytes' has to be positive integer.")
        return sha256file(self.abspath, nbytes)

    @property
    def sha256(self):
        """
        Return sha256 check sum of this file.
        """
        return sha256file(self.abspath)

    def get_partial_sha512(self, nbytes):
        """
        Return sha512 check sum of first n bytes of this file.
        """
        if nbytes in [0, None]:
            raise ValueError("'nbytes' has to be positive integer.")
        return sha512file(self.abspath, nbytes)

    @property
    def sha512(self):
        """
        Return md5 check sum of this file.
        """
        return sha512file(self.abspath)

    @property
    def size(self):
        """
        File size in bytes.
        """
        try:
            return self._stat.st_size
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.size

    @property
    def dirsize(self):
        """
        Return total file size (include sub folder).
        """
        total = 0
        for p in self.select_file(recursive=True):
            try:
                total += p.size
            except:
                print("Unable to get file size of: %s" % p)
        return total

    @property
    def size_in_text(self):
        """
        File size as human readable string.
        """
        return repr_data_size(self.size, precision=2)

    @property
    def mtime(self):
        """
        Get most recent modify time in timestamp.
        """
        try:
            return self._stat.st_mtime
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.mtime

    @property
    def atime(self):
        """
        Get most recent access time in timestamp.
        """
        try:
            return self._stat.st_atime
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.atime

    @property
    def ctime(self):
        """
        Get most recent create time in timestamp.
        """
        try:
            return self._stat.st_ctime
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.ctime

    @property
    def modify_datetime(self):
        """
        Get most recent modify time in datetime.
        """
        return datetime.fromtimestamp(self.mtime)

    @property
    def access_datetime(self):
        """
        Get most recent access time in datetime.
        """
        return datetime.fromtimestamp(self.atime)

    @property
    def create_datetime(self):
        """
        Get most recent create time in datetime.
        """
        return datetime.fromtimestamp(self.ctime)

    # --- methods return another Path ---
    def drop_parts(self, n=1):
        """
        Drop parts from the ends.

        :param n: integer, number of parts you wants to drop from ends.
          n has to greater equal than 0.

        :returns: a new Path object.

        Example::

            >>> self.__class__("/usr/bin/python").drop_parts(1)
            "/user/bin"

            >>> self.__class__("/usr/bin/python").drop_parts(2)
            "/user"
        """
        return self.__class__(*self.parts[:-n])

    def append_parts(self, *parts):
        """
        Append some parts to the end of this path.

        :returns: a new Path object.

        Example::

            >>> self.__class__("/usr/bin/python").append_parts("lib")
            "/user/bin/python/lib"

            >>> self.__class__("/usr/bin/python").append_parts("lib", "core.py")
            "/user/bin/python/lib/core.py"
        """
        return self.__class__(self, *parts)

    def change(self,
               new_abspath=None,
               new_dirpath=None, new_dirname=None,
               new_basename=None,
               new_fname=None,
               new_ext=None):
        """Return a new :class:`Path` object with updated information.
        """
        if new_abspath is not None:
            p = self.__class__(new_abspath)
            return p

        if (new_dirpath is None) and (new_dirname is not None):
            new_dirpath = os.path.join(self.parent.dirpath, new_dirname)

        elif (new_dirpath is not None) and (new_dirname is None):
            new_dirpath = new_dirpath

        elif (new_dirpath is None) and (new_dirname is None):
            new_dirpath = self.dirpath

        elif (new_dirpath is not None) and (new_dirname is not None):
            raise ValueError("Cannot having both new_dirpath and new_dirname!")

        if new_basename is None:
            if new_fname is None:
                new_fname = self.fname
            if new_ext is None:
                new_ext = self.ext
            new_basename = new_fname + new_ext
        else:
            if new_fname is not None or new_ext is not None:
                raise ValueError("Cannot having both new_basename, "
                                 "new_fname, new_ext!")

        return self.__class__(new_dirpath, new_basename)

    def is_not_exist_or_allow_overwrite(self, overwrite=False):
        """
        Test whether a file target is not exists or it exists but allow
        overwrite.
        """
        if self.exists() and overwrite is False:
            return False
        else:
            return True

    def moveto(self,
               new_abspath=None,
               new_dirpath=None, new_dirname=None,
               new_basename=None,
               new_fname=None,
               new_ext=None,
               overwrite=False,
               makedirs=False):
        """
        An advanced ``Path.rename`` method provide ability to rename by
        each components of a path. A new ``Path`` instance will returns.

        **中文文档**

        高级重命名函数, 允许用于根据路径的各个组成部分进行重命名。但和os.rename
        方法一样, 需要保证母文件夹存在。
        """
        self.assert_exists()

        p = self.change(
            new_abspath=new_abspath,
            new_dirpath=new_dirpath,
            new_dirname=new_dirname,
            new_basename=new_basename,
            new_fname=new_fname,
            new_ext=new_ext,
        )

        if p.is_not_exist_or_allow_overwrite(overwrite=overwrite):
            # 如果两个路径不同, 才进行move
            if self.abspath != p.abspath:
                if makedirs:
                    parent = p.parent
                    if not parent.exists():
                        os.makedirs(parent.abspath)
                self.rename(p)
        return p

    def copyto(self,
               new_abspath=None,
               new_dirpath=None, new_dirname=None,
               new_basename=None,
               new_fname=None,
               new_ext=None,
               overwrite=False,
               makedirs=False):
        """
        Copy this file to other place.
        """
        self.assert_exists()

        p = self.change(
            new_abspath=new_abspath,
            new_dirpath=new_dirpath,
            new_dirname=new_dirname,
            new_basename=new_basename,
            new_fname=new_fname,
            new_ext=new_ext,
        )

        if p.is_not_exist_or_allow_overwrite(overwrite=overwrite):
            # 如果两个路径不同, 才进行copy
            if self.abspath != p.abspath:
                if makedirs:
                    parent = p.parent
                    if not parent.exists():
                        os.makedirs(parent.abspath)
                shutil.copy(self.abspath, p.abspath)

        return p

    def remove(self, *args, **kwargs):
        """Remove it.
        """
        self.unlink(*args, **kwargs)

    # --- select ---
    def all_true(x):
        return True

    def select(self, filters=all_true, recursive=True):
        """Select path by criterion.

        :param filters: a lambda function that take a `pathlib.Path` as input,
          boolean as a output.
        :param recursive: include files in subfolder or not.

        **中文文档**

        根据filters中定义的条件选择路径。
        """
        self.assert_is_dir_and_exists()

        if recursive:
            for p in self.glob("**/*"):
                if filters(p):
                    yield p
        else:
            for p in self.iterdir():
                if filters(p):
                    yield p

    def select_file(self, filters=all_true, recursive=True):
        """Select file path by criterion.

        **中文文档**

        根据filters中定义的条件选择文件。
        """
        for p in self.select(filters, recursive):
            if p.is_file():
                yield p

    def select_dir(self, filters=all_true, recursive=True):
        """Select dir path by criterion.

        **中文文档**

        根据filters中定义的条件选择文件夹。
        """
        for p in self.select(filters, recursive):
            if p.is_dir():
                yield p

    @property
    def n_file(self):
        """Count how many files in this directory.
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_file(recursive=True):
            n += 1
        return n

    @property
    def n_dir(self):
        """Count how many folders in this directory.
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_dir(recursive=True):
            n += 1
        return n

    @property
    def n_subfile(self):
        """Count how many files in this directory (doesn't include files in
        sub folders).
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_file(recursive=False):
            n += 1
        return n

    @property
    def n_subdir(self):
        """Count how many folders in this directory (doesn't include folder in
        sub folders).
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_dir(recursive=False):
            n += 1
        return n

    # --- Select by built-in criterion ---
    def select_by_ext(self, ext, recursive=True):
        """Select file path by extension.

        :param ext:

        **中文文档**

        选择与预定义的若干个扩展名匹配的文件。
        """
        ext = [ext.strip().lower() for ext in _preprocess(ext)]

        def filters(p): return p.suffix.lower() in ext

        return self.select_file(filters, recursive)

    def select_by_pattern_in_fname(self,
                                   pattern,
                                   recursive=True,
                                   case_sensitive=False):
        """Select file path by text pattern in file name.


        **中文文档**

        选择文件名中包含指定子字符串的文件。
        """
        if case_sensitive:
            def filters(p):
                return pattern in p.fname
        else:
            pattern = pattern.lower()

            def filters(p):
                return pattern in p.fname.lower()

        return self.select_file(filters, recursive)

    def select_by_pattern_in_abspath(self,
                                     pattern,
                                     recursive=True,
                                     case_sensitive=False):
        """
        Select file path by text pattern in absolute path.

        **中文文档**

        选择绝对路径中包含指定子字符串的文件。
        """
        if case_sensitive:
            def filters(p):
                return pattern in p.abspath
        else:
            pattern = pattern.lower()

            def filters(p):
                return pattern in p.abspath.lower()

        return self.select_file(filters, recursive)

    def select_by_size(self, min_size=0, max_size=1 << 40, recursive=True):
        """Select file path by size.

        **中文文档**

        选择所有文件大小在一定范围内的文件。
        """

        def filters(p): return min_size <= p.size <= max_size

        return self.select_file(filters, recursive)

    def select_by_mtime(self, min_time=0, max_time=4102462800.0,
                        recursive=True):
        """Select file path by modify time.

        :param min_time: lower bound timestamp
        :param max_time: upper bound timestamp

        **中文文档**

        选择所有mtime在一定范围内的文件。
        """

        def filters(p): return min_time <= p.mtime <= max_time

        return self.select_file(filters, recursive)

    def select_by_atime(self, min_time=0, max_time=4102462800.0,
                        recursive=True):
        """Select file path by access time.

        :param min_time: lower bound timestamp
        :param max_time: upper bound timestamp

        **中文文档**

        选择所有atime在一定范围内的文件。
        """

        def filters(p): return min_time <= p.atime <= max_time

        return self.select_file(filters, recursive)

    def select_by_ctime(self, min_time=0, max_time=4102462800.0,
                        recursive=True):
        """Select file path by create time.

        :param min_time: lower bound timestamp
        :param max_time: upper bound timestamp

        **中文文档**

        选择所有ctime在一定范围内的文件。
        """

        def filters(p): return min_time <= p.ctime <= max_time

        return self.select_file(filters, recursive)

    # --- Select Special File Type ---
    _image_ext = [
        ".jpg", ".jpeg", ".png", ".gif", ".tiff",
        ".bmp", ".ppm", ".pgm", ".pbm", ".pnm", ".svg",
    ]

    def select_image(self, recursive=True):
        """Select image file.
        """
        return self.select_by_ext(self._image_ext, recursive)

    _audio_ext = [
        ".mp3", ".mp4", ".aac", ".m4a", ".wma",
        ".wav", ".ape", ".tak", ".tta",
        ".3gp", ".webm", ".ogg",
    ]

    def select_audio(self, recursive=True):  # pragma: no cover
        """Select audio file.
        """
        return self.select_by_ext(self._audio_ext, recursive)

    _video_ext = [
        ".avi", ".wmv", ".mkv", ".mp4", ".flv",
        ".vob", ".mov", ".rm", ".rmvb", "3gp", ".3g2", ".nsv", ".webm",
        ".mpg", ".mpeg", ".m4v", ".iso",
    ]

    def select_video(self, recursive=True):  # pragma: no cover
        """Select video file.
        """
        return self.select_by_ext(self._video_ext, recursive)

    def select_word(self, recursive=True):  # pragma: no cover
        """Select Microsoft Word file.
        """
        ext = [".doc", ".docx", ".docm", ".dotx", ".dotm", ".docb"]
        return self.select_by_ext(ext, recursive)

    def select_excel(self, recursive=True):  # pragma: no cover
        """Select Microsoft Excel file.
        """
        ext = [".xls", ".xlsx", ".xlsm", ".xltx", ".xltm"]
        return self.select_by_ext(ext, recursive)

    _archive_ext = [".zip", ".rar", ".gz", ".tar.gz", ".tgz", ".7z"]

    def select_archive(self, recursive=True):  # pragma: no cover
        """Select compressed archive file.
        """
        return self.select_by_ext(self._archive_ext, recursive)

    def _sort_by(key):
        """High order function for sort methods.
        """

        @staticmethod
        def sort_by(p_list, reverse=False):
            return sorted(p_list, key=lambda p: getattr(p, key),
                          reverse=reverse)

        return sort_by

    sort_by_abspath = _sort_by("abspath")
    """Sort list of :class:`Path` by absolute path.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_fname = _sort_by("fname")
    """Sort list of :class:`Path` by file name.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_ext = _sort_by("ext")
    """Sort list of :class:`Path` by extension.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_size = _sort_by("size")
    """Sort list of :class:`Path` by file size.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_mtime = _sort_by("mtime")
    """Sort list of :class:`Path` by modify time.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_atime = _sort_by("atime")
    """Sort list of :class:`Path` by access time.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_ctime = _sort_by("ctime")
    """Sort list of :class:`Path` by create time.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_md5 = _sort_by("md5")
    """Sort list of :class:`Path` by md5.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    def is_empty(self, strict=True):
        """Test:

        - If it's a file, check if it is a empty file. (0 bytes)
        - If it's a directory, check if there's no file and dir in it. But if
          ``strict = False``, then only check if there's no file in it.
        """
        if self.exists():
            if self.is_file():
                return self.size == 0
            elif self.is_dir():
                if strict:
                    return len(list(self.select(recursive=True))) == 0
                else:
                    return len(list(self.select_file(recursive=True))) == 0
            else:
                raise EnvironmentError(
                    "'%s' is not either file or directory!" % self)
        else:
            raise EnvironmentError("'%s' not exists!" % self)

    # --- Directory Exclusive Method ---
    def print_big_dir(self, top_n=5):
        """Print ``top_n`` big dir in this dir.
        """
        self.assert_is_dir_and_exists()

        size_table = sorted(
            [(p, p.dirsize) for p in self.select_dir(recursive=False)],
            key=lambda x: x[1],
            reverse=True,
        )
        for p, size in size_table[:top_n]:
            print("{:<9}    {:<9}".format(repr_data_size(size), p.abspath))

    def print_big_file(self, top_n=5):
        """Print ``top_n`` big file in this dir.
        """
        self.assert_is_dir_and_exists()

        size_table = sorted(
            [(p, p.size) for p in self.select_file(recursive=True)],
            key=lambda x: x[1],
            reverse=True,
        )
        for p, size in size_table[:top_n]:
            print("{:<9}    {:<9}".format(repr_data_size(size), p.abspath))

    def print_big_dir_and_big_file(self, top_n=5):
        """Print ``top_n`` big dir and ``top_n`` big file in each dir.
        """
        self.assert_is_dir_and_exists()

        size_table1 = sorted(
            [(p, p.dirsize) for p in self.select_dir(recursive=False)],
            key=lambda x: x[1],
            reverse=True,
        )
        for p1, size1 in size_table1[:top_n]:
            print("{:<9}    {:<9}".format(repr_data_size(size1), p1.abspath))
            size_table2 = sorted(
                [(p, p.size) for p in p1.select_file(recursive=True)],
                key=lambda x: x[1],
                reverse=True,
            )
            for p2, size2 in size_table2[:top_n]:
                print("    {:<9}    {:<9}".format(
                    repr_data_size(size2), p2.abspath))

    def file_stat_for_all(self, filters=all_true):
        """Find out how many files, directorys and total size (Include file in
        it's sub-folder) it has for each folder and sub-folder.

        :returns: stat, a dict like ``{"directory path": {
          "file": number of files, "dir": number of directorys,
          "size": total size in bytes}}``

        **中文文档**

        返回一个目录中的每个子目录的, 文件, 文件夹, 大小的统计数据。
        """
        self.assert_is_dir_and_exists()

        from collections import OrderedDict

        stat = OrderedDict()
        stat[self.abspath] = {"file": 0, "dir": 0, "size": 0}

        for p in self.select(recursive=True):
            if p.is_file():
                size = p.size
                while 1:
                    parent = p.parent

                    stat[parent.abspath]["file"] += 1
                    stat[parent.abspath]["size"] += size

                    if parent.abspath == self.abspath:
                        break

                    p = parent

            elif p.is_dir():
                stat[p.abspath] = {"file": 0, "dir": 0, "size": 0}

                while 1:
                    parent = p.parent
                    stat[parent.abspath]["dir"] += 1

                    if parent.abspath == self.abspath:
                        break

                    p = parent

        return stat

    def file_stat(self, filters=all_true):
        """Find out how many files, directorys and total size (Include file in
        it's sub-folder).

        :returns: stat, a dict like ``{"file": number of files,
          "dir": number of directorys, "size": total size in bytes}``

        **中文文档**

        返回一个目录中的文件, 文件夹, 大小的统计数据。
        """
        self.assert_is_dir_and_exists()

        stat = {"file": 0, "dir": 0, "size": 0}

        for p in self.select(recursive=True):
            if p.is_file():
                stat["file"] += 1
                stat["size"] += p.size
            elif p.is_dir():
                stat["dir"] += 1

        return stat

    def mirror_to(self, dst):
        """Create a folder that has exactly same structure with this directory.
        Except, all files are empty file.

        :param dst: distination directory. The directory can't exists before
        you execute this.

        **中文文档**

        创建一个目录的镜像拷贝, 与拷贝操作不同的是, 文件的副本只是在文件名上
        与原件一致, 但是是空文件, 完全没有内容, 文件大小为0。
        """
        self.assert_is_dir_and_exists()

        src = self.abspath
        dst = os.path.abspath(dst)
        if os.path.exists(dst):  # pragma: no cover
            raise Exception("distination already exist!")

        folder_to_create = list()
        file_to_create = list()

        for current_folder, _, file_list in os.walk(self.abspath):
            current_folder = current_folder.replace(src, dst)
            try:
                os.mkdir(current_folder)
            except:  # pragma: no cover
                pass
            for basename in file_list:
                abspath = os.path.join(current_folder, basename)
                with open(abspath, "wb") as _:
                    pass

    def backup(self, dst=None,
               ignore=None,
               ignore_ext=None,
               ignore_pattern=None,
               ignore_size_smaller_than=None,
               ignore_size_larger_than=None,
               case_sensitive=False):
        """The backup utility method. Basically it just add files that need to be
        backupped to zip archives.

        :param filename: the output file name, DO NOT NEED FILE EXTENSION.
        :param root_dir: the directory you want to backup.
        :param ignore: file or directory defined in this list will be ignored.
        :param ignore_ext: file with extensions defined in this list will be ignored.
        :param ignore_pattern: any file or directory that contains this pattern
          will be ignored.

        **中文文档**

        为一个目录创建一个备份压缩包。可以通过过滤器选择你要备份的文件。
        """
        from zipfile import ZipFile

        def preprocess_arg(arg):  # pragma: no cover
            if arg is None:
                return []

            if isinstance(arg, (tuple, list)):
                return list(arg)
            else:
                return [arg, ]

        self.assert_is_dir_and_exists()

        tab = "    "

        # Step 0, preprocess input argument
        surfix = " %s.zip" % datetime.now().strftime("%Y-%m-%d %Hh-%Mm-%Ss")
        if dst is None:
            dst = self.__class__(os.getcwd(), self.basename + surfix).abspath
        else:
            dst = str(dst)
            if dst.endswith(".zip") or dst.endswith(".ZIP"):
                dst = dst[:-4]
            dst = self.__class__(self.__class__(dst).abspath + surfix).abspath
        print("Backup '%s' to '%s'..." % (self.abspath, dst))

        # Step 1, calculate files to backup
        print(tab + "1. Calculate files...")

        ignore = preprocess_arg(ignore)
        for i in ignore:
            if i.startswith("/") or i.startswith("\\"):
                raise ValueError

        ignore_ext = preprocess_arg(ignore_ext)
        for ext in ignore_ext:
            if not ext.startswith("."):
                raise ValueError

        ignore_pattern = preprocess_arg(ignore_pattern)

        if case_sensitive:
            pass
        else:
            ignore = [i.lower() for i in ignore]
            ignore_ext = [i.lower() for i in ignore_ext]
            ignore_pattern = [i.lower() for i in ignore_pattern]

        def filters(p):
            relpath = p.relative_to(self).abspath
            if not case_sensitive:
                relpath = relpath.lower()

            # ignore
            for i in ignore:
                if relpath.startswith(i):
                    return False

            # ignore_ext
            if case_sensitive:
                ext = p.ext
            else:
                ext = p.ext.lower()

            if ext in ignore_ext:
                return False

            # ignore_pattern
            for pattern in ignore_pattern:
                if pattern in relpath:
                    return False

            # ignore_size_smaller_than
            if ignore_size_smaller_than:
                if p.size < ignore_size_smaller_than:
                    return False

            # ignore_size_larger_than
            if ignore_size_larger_than:
                if p.size > ignore_size_larger_than:
                    return False

            return True

        total_size = 0
        selected = list()
        for p in self.glob("**/*"):
            if filters(p):
                selected.append(p)
                total_size += p.size

        print(tab * 2 + "Done, got %s files, total size is %s." % (
            len(selected), repr_data_size(total_size)))

        # Step 2, write files to zip archive
        print(tab + "2. Backup files...")
        current_dir = os.getcwd()

        with ZipFile(dst, "w") as f:
            os.chdir(self.abspath)
            for p in selected:
                relpath = p.relative_to(self).__str__()
                f.write(relpath)

        os.chdir(current_dir)

        print(tab * 2 + "Complete!")

    def execute_pyfile(self, py_exe=None):  # pragma: no cover
        """
        Execute every ``.py`` file as main script.

        :param py_exe: str, python command or python executable path.

        **中文文档**

        将目录下的所有Python文件作为主脚本用当前解释器运行。
        """
        import subprocess

        self.assert_is_dir_and_exists()

        if py_exe is None:
            if six.PY2:
                py_exe = "python2"
            elif six.PY3:
                py_exe = "python3"

        for p in self.select_by_ext(".py"):
            subprocess.Popen('%s "%s"' % (py_exe, p.abspath))

    def trail_space(self, filters=lambda p: p.ext == ".py"):
        """
        Trail white space at end of each line for every ``.py`` file.

        **中文文档**

        将目录下的所有被选择的文件中行末的空格删除。
        """
        self.assert_is_dir_and_exists()

        for p in self.select_file(filters):
            try:
                with open(p.abspath, "rb") as f:
                    lines = list()
                    for line in f:
                        lines.append(line.decode("utf-8").rstrip())

                with open(p.abspath, "wb") as f:
                    f.write("\n".join(lines).encode("utf-8"))

            except Exception as e:  # pragma: no cover
                raise e

    def autopep8(self, **kwargs):
        """
        Auto convert your python code in a directory to pep8 styled code.

        :param kwargs: arguments for ``autopep8.fix_code`` method.

        **中文文档**

        将目录下的所有Python文件用pep8风格格式化。增加其可读性和规范性。
        """
        self.assert_is_dir_and_exists()

        for p in self.select_by_ext(".py"):
            with open(p.abspath, "rb") as f:
                code = f.read().decode("utf-8")

            formatted_code = autopep8.fix_code(code, **kwargs)

            with open(p.abspath, "wb") as f:
                f.write(formatted_code.encode("utf-8"))
