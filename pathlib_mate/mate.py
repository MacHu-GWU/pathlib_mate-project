#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pathlib_mate provide extensive method, attributes for pathlib.
"""

import os
import hashlib
from collections import OrderedDict
from datetime import datetime

try:
    from .pathlib import Path
except:
    from pathlib_mate.pathlib import Path


def _preprocess(path_or_path_list):
    """Preprocess input argument, whether if it is:

    1. abspath
    2. WinFile instance
    3. WinDir instance
    4. list or set of any of them

    It returns list of path.

    :return path_or_path_list: always return list of path

    **中文文档**

    预处理输入参数。
    """
    if not isinstance(path_or_path_list, (list, set)):
        path_or_path_list = [path_or_path_list, ]
    else:
        od = OrderedDict()
        for path in path_or_path_list:
            od[str(path)] = 0
        path_or_path_list = list(od)

    return path_or_path_list


def repr_data_size(size_in_bytes, precision=2):
    """Return human readable string represent of a file size. Doesn"t support 
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
    s = template.format(size_in_bytes + mod/1024.0, magnitude_of_data[index])
    return s


def md5file(abspath, nbytes=0):
    """Return md5 hash value of a piece of a file

    Estimate processing time on:

    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0, hash all file

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


@property
def abspath(self):
    """Absolute path.
    """
    return self.__str__()

Path.abspath = abspath


@property
def dirpath(self):
    """Parent dir full absolute path.
    """
    return self.parent.abspath

Path.dirpath = dirpath


@property
def dirname(self):
    """Parent dir name.
    """
    return self.parent.name

Path.dirname = dirname


@property
def basename(self):
    """File name with extension, path is not included.
    """
    return self.name

Path.basename = basename


@property
def fname(self):
    """File name without extension.
    """
    return self.stem

Path.fname = fname


@property
def ext(self):
    """File extension. If it's a dir, then return empty str.
    """
    return self.suffix

Path.ext = ext


def get_partial_md5(self, nbytes=0):
    """Md5 check sum.
    """
    return md5file(self.abspath, nbytes)

Path.get_partial_md5 = get_partial_md5


@property
def md5(self):
    return md5file(self.abspath)

Path.md5 = md5


@property
def size(self):
    """File size in bytes.
    """
    try:
        return self._stat.st_size
    except:
        self._stat = self.stat()
        return self.size


Path.size = size


@property
def size_in_text(self):
    """File size as human readable string.
    """
    return repr_data_size(self.size, precision=2)


Path.size_in_text = size_in_text


@property
def mtime(self):
    """Get most recent modify timestamp.
    """
    try:
        return self._stat.st_mtime
    except:
        self._stat = self.stat()
        return self.mtime


Path.mtime = mtime


@property
def atime(self):
    """Get most recent access timestamp.
    """
    try:
        return self._stat.st_atime
    except:
        self._stat = self.stat()
        return self.atime


Path.atime = atime


@property
def ctime(self):
    """Get most recent create timestamp.
    """
    try:
        return self._stat.st_ctime
    except:
        self._stat = self.stat()
        return self.ctime


Path.ctime = ctime


@property
def modify_datetime(self):
    """Get most recent modify datetime.
    """
    return datetime.fromtimestamp(self.mtime)


Path.modify_datetime = modify_datetime


@property
def access_datetime(self):
    """Get most recent access datetime.
    """
    return datetime.fromtimestamp(self.atime)


Path.access_datetime = access_datetime


@property
def create_datetime(self):
    """Get most recent create datetime.
    """
    return datetime.fromtimestamp(self.ctime)


Path.create_datetime = create_datetime


def moveto(self, new_dirpath=None, new_dirname=None, new_fname=None, new_ext=None):
    """An advanced ``Path.rename`` method provide ability to rename by parts of 
    a path. A new ``Path`` instance will returns.
    
    **中文文档**
    
    高级重命名函数, 允许用于根据路径的各个组成部分进行重命名。
    """
    flag = False

    if (new_dirpath is None) and (new_dirname is not None):
        new_dirpath = os.path.join(self.parent.dirpath, new_dirname)
        flag = True
        
    elif (new_dirpath is not None) and (new_dirname is None):
        new_dirpath = new_dirpath
        flag = True
        
    elif (new_dirpath is None) and (new_dirname is None):
        new_dirpath = self.dirpath
        flag = True
        
    elif (new_dirpath is not None) and (new_dirname is not None):
        raise ValueError("Cannot having both new_dirpath and new_dirname!")

    if new_fname is None:
        new_fname = self.fname
    else:
        flag = True

    if new_ext is None:
        new_ext = self.ext
    else:
        flag = True

    if flag:
        p = Path(new_dirpath, new_fname + new_ext)
        self.rename(p)
        return p
        

Path.moveto = moveto

Path.remove = Path.unlink


#--- select ---
all_true = lambda x: True


def select(self, filters=all_true, recursive=True):
    """Select path by criterion.

    :param filters: a lambda function that take a `pathlib.Path` as input, 
      boolean as a output.
    :param recursive: include files in subfolder or not.

    **中文文档**

    根据filters中定义的条件选择路径。
    """
    if not self.is_dir():
        raise TypeError("%s is not a directory!" % self)

    if recursive:
        for p in self.glob("**/*"):
            if filters(p):
                yield p
    else:
        for p in self.iterdir():
            if filters(p):
                yield p

Path.select = select


def select_file(self, filters=all_true, recursive=True):
    """Select file path by criterion.

    **中文文档**

    根据filters中定义的条件选择文件。
    """
    for p in self.select(filters, recursive):
        if p.is_file():
            yield p


Path.select_file = select_file


def select_dir(self, filters=all_true, recursive=True):
    """Select dir path by criterion.

    **中文文档**

    根据filters中定义的条件选择文件夹。
    """
    for p in self.select(filters, recursive):
        if p.is_dir():
            yield p


Path.select_dir = select_dir


#--- Select by built-in criterion ---
def select_by_ext(self, ext, recursive=True):
    """Select file path by extension.

    :param ext:

    **中文文档**

    选择与预定义的若干个扩展名匹配的文件。
    """
    ext = [ext.strip().lower() for ext in _preprocess(ext)]
    filters = lambda p: p.suffix.lower() in ext
    return self.select_file(filters, recursive)


Path.select_by_ext = select_by_ext


def select_by_pattern_in_fname(self, pattern, recursive=True, case_sensitive=False):
    """Select file path by text pattern in file name.
    """
    if case_sensitive:
        pattern = pattern.lower()
        filters = lambda p: pattern in p.fname.lower()
    else:
        filters = lambda p: pattern in p.fname

    return self.select_file(filters, recursive)


Path.select_by_pattern_in_fname = select_by_pattern_in_fname


def select_by_pattern_in_abspath(self, pattern, recursive=True, case_sensitive=False):
    """Select file path by text pattern in absolute path.
    """
    if case_sensitive:
        pattern = pattern.lower()
        filters = lambda p: pattern in p.abspath.lower()
    else:
        filters = lambda p: pattern in p.abspath

    return self.select_file(filters, recursive)


Path.select_by_pattern_in_abspath = select_by_pattern_in_abspath


def select_by_size(self, min_size=0, max_size=1 << 40, recursive=True):
    """Select file path by size.

    **中文文档**

    选择所有文件大小在一定范围内的文件。
    """
    filters = lambda p: min_size <= p.size <= max_size
    return self.select_file(filters, recursive)


Path.select_by_size = select_by_size


def select_by_mtime(self, min_time=0, max_time=4102462800.0, recursive=True):
    """Select file path by modify time.

    :param min_time: lower bound timestamp
    :param max_time: upper bound timestamp

    **中文文档**

    选择所有mtime在一定范围内的文件。
    """
    filters = lambda p: min_time <= p.mtime <= max_time
    return self.select_file(filters, recursive)


Path.select_by_mtime = select_by_mtime


def select_by_atime(self, min_time=0, max_time=4102462800.0, recursive=True):
    """Select file path by access time.

    :param min_time: lower bound timestamp
    :param max_time: upper bound timestamp

    **中文文档**

    选择所有atime在一定范围内的文件。
    """
    filters = lambda p: min_time <= p.atime <= max_time
    return self.select_file(filters, recursive)


Path.select_by_atime = select_by_atime


def select_by_ctime(self, min_time=0, max_time=4102462800.0, recursive=True):
    """Select file path by create time.

    :param min_time: lower bound timestamp
    :param max_time: upper bound timestamp

    **中文文档**

    选择所有ctime在一定范围内的文件。
    """
    filters = lambda p: min_time <= p.ctime <= max_time
    return self.select_file(filters, recursive)


Path.select_by_ctime = select_by_ctime


#--- Select Special File Type ---
def select_image(self, recursive=True):
    """Select image file.
    """
    ext = [".jpg", ".jpeg", ".png", ".gif", ".tiff",
           ".bmp", ".ppm", ".pgm", ".pbm", ".pnm", ".svg"]
    return select_by_ext(ext, recursive)


Path.select_image = select_image


def select_audio(self, recursive=True):
    """Select audio file.
    """
    ext = [".mp3", ".mp4", ".aac", ".m4a", ".wma",
           ".wav", ".ape", ".tak", ".tta",
           ".3gp", ".webm", ".ogg", ]
    return select_by_ext(ext, recursive)


Path.select_audio = select_audio


def select_video(self, recursive=True):
    """Select video file.
    """
    ext = [".avi", ".wmv", ".mkv", ".mp4", ".flv",
           ".vob", ".mov", ".rm", ".rmvb", "3gp", ".3g2", ".nsv", ".webm",
           ".mpg", ".mpeg", ".m4v", ".iso", ]
    return select_by_ext(ext, recursive)


Path.select_video = select_video


def select_word(self, recursive=True):
    """Select Microsoft Word file.
    """
    ext = [".doc", ".docx", ".docm", ".dotx", ".dotm", ".docb"]
    return select_by_ext(ext, recursive)


Path.select_word = select_word


def select_excel(self, recursive=True):
    """Select Microsoft Excel file.
    """
    ext = [".xls", ".xlsx", ".xlsm", ".xltx", ".xltm"]
    return select_by_ext(ext, recursive)


Path.select_excel = select_excel


def select_archive(self, recursive=True):
    """Select compressed archive file.
    """
    ext = [".zip", ".rar", ".gz", ".tar.gz", ".tgz", ".7z"]
    return select_by_ext(ext, recursive)


Path.select_archive = select_archive


def _sort_by(key):
    """High order function for sort methods.
    """
    @staticmethod
    def sort_by(iterable, reverse=False):
        return sorted(iterable, key=lambda p: getattr(p, key), reverse=reverse)
    return sort_by


Path.sort_by_abspath = _sort_by("abspath")
Path.sort_by_fname = _sort_by("fname")
Path.sort_by_ext = _sort_by("ext")
Path.sort_by_size = _sort_by("size")
Path.sort_by_mtime = _sort_by("mtime")
Path.sort_by_atime = _sort_by("atime")
Path.sort_by_ctime = _sort_by("ctime")
Path.sort_by_md5 = _sort_by("md5")
