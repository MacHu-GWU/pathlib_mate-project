# -*- coding: utf-8 -*-

"""
Provide friendly path filter API.
"""

# for type hint only
try:  # pragma: no cover
    from typing import TYPE_CHECKING, Callable, Iterable

    if TYPE_CHECKING:
        from .pathlib2 import Path

except ImportError:  # pragma: no cover
    pass

from datetime import datetime

from .helper import ensure_list

ts_2100 = (datetime(2100, 1, 1) - datetime(1970, 1, 1)).total_seconds()


def all_true(anything):
    return True


def _sort_by(key):
    """
    High order function for sort methods.
    """

    @staticmethod
    def sort_by(p_list, reverse=False):
        """
        :rtype: typing.Iterable[Path]
        """
        return sorted(
            p_list,
            key=lambda p: getattr(p, key),
            reverse=reverse,
        )

    return sort_by


class PathFilters(object):
    """
    Provide friendly path filter API.
    """

    # --- assert something ---

    def assert_is_file_and_exists(self):
        """
        Assert it is a directory and exists in file system.

        :type self: Path
        """
        if not self.is_file():
            msg = "'%s' is not a file or doesn't exists!" % self
            raise EnvironmentError(msg)

    def assert_is_dir_and_exists(self):
        """
        Assert it is a directory and exists in file system.

        :type self: Path
        """
        if not self.is_dir():
            msg = "'%s' is not a file or doesn't exists!" % self
            raise EnvironmentError(msg)

    def assert_exists(self):
        """
        Assert it exists.

        :type self: Path
        """
        if not self.exists():
            msg = "'%s' doesn't exists!" % self
            raise EnvironmentError(msg)

    # --- select ---
    def select(self, filters=all_true, recursive=True):
        """Select path by criterion.

        :type self: Path

        :type filters: Callable
        :param filters: a lambda function that take
            a :class:`~pathlib_mate.pathlib2.Path` as input,
            return boolean as a output.

        :type recursive: bool
        :param recursive: include files in sub-folder or not.

        :rtype: Iterable[Path]

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

        :type self: Path
        :type filters: Callable
        :type recursive: bool

        :rtype: typing.Iterable[Path]

        **中文文档**

        根据 ``filters`` 中定义的条件选择文件.
        """
        for p in self.select(filters, recursive):
            if p.is_file():
                yield p

    def select_dir(self, filters=all_true, recursive=True):
        """Select dir path by criterion.

        :type self: Path
        :type filters: Callable
        :type recursive: bool

        :rtype: typing.Iterable[Path]

        **中文文档**

        根据 ``filters`` 中定义的条件选择文件夹.
        """
        for p in self.select(filters, recursive):
            if p.is_dir():
                yield p

    @property
    def n_file(self):
        """
        Count how many files in this directory. Including file in sub folder.

        :type self: Path

        :rtype: int
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_file(recursive=True):
            n += 1
        return n

    @property
    def n_dir(self):
        """
        Count how many folders in this directory. Including folder in sub folder.

        :type self: Path

        :rtype: int
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_dir(recursive=True):
            n += 1
        return n

    @property
    def n_subfile(self):
        """
        Count how many files in this directory (doesn't include files in
        sub folders).

        :type self: Path

        :rtype: int
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_file(recursive=False):
            n += 1
        return n

    @property
    def n_subdir(self):
        """
        Count how many folders in this directory (doesn't include folder in
        sub folders).

        :type self: Path

        :rtype: int
        """
        self.assert_is_dir_and_exists()
        n = 0
        for _ in self.select_dir(recursive=False):
            n += 1
        return n

    # --- Select by built-in criterion ---
    def select_by_ext(self, ext, recursive=True):
        """
        Select file path by extension.

        :type self: Path
        :type ext: str
        :type recursive: bool
        :rtype: typing.Iterable[Path]

        **中文文档**

        选择与预定义的若干个扩展名匹配的文件。
        """
        ext = [ext.strip().lower() for ext in ensure_list(ext)]

        def filters(p): return p.suffix.lower() in ext

        return self.select_file(filters, recursive)

    def select_by_pattern_in_fname(
        self,
        pattern,
        recursive=True,
        case_sensitive=False,
    ):
        """
        Select file path by text pattern in file name.

        :type self: Path
        :type pattern: str
        :type recursive: bool
        :rtype: typing.Iterable[Path]

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

    def select_by_pattern_in_abspath(
        self,
        pattern,
        recursive=True,
        case_sensitive=False,
    ):
        """
        Select file path by text pattern in absolute path.

        :type self: Path
        :type pattern: str
        :type recursive: bool
        :rtype: typing.Iterable[Path]

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

    def select_by_size(
        self,
        min_size=0,
        max_size=1 << 40,
        recursive=True,
    ):
        """
        Select file path by size.

        :type self: Path
        :type min_size: int
        :type max_size: int
        :type recursive: bool
        :rtype: typing.Iterable[Path]

        **中文文档**

        选择所有文件大小在一定范围内的文件。
        """

        def filters(p): return min_size <= p.size <= max_size

        return self.select_file(filters, recursive)

    def select_by_mtime(
        self,
        min_time=0,
        max_time=ts_2100,
        recursive=True,
    ):
        """
        Select file path by modify time.

        :type self: Path

        :type min_time: Union[int, float]
        :param min_time: lower bound timestamp

        :type max_time: Union[int, float]
        :param max_time: upper bound timestamp

        :type recursive: bool

        :rtype: typing.Iterable[Path]

        **中文文档**

        选择所有 :attr:`pathlib_mate.pathlib2.Path.mtime` 在一定范围内的文件。
        """

        def filters(p): return min_time <= p.mtime <= max_time

        return self.select_file(filters, recursive)

    def select_by_atime(
        self,
        min_time=0,
        max_time=ts_2100,
        recursive=True
    ):
        """
        Select file path by access time.

        :type self: Path

        :type min_time: Union[int, float]
        :param min_time: lower bound timestamp

        :type max_time: Union[int, float]
        :param max_time: upper bound timestamp

        :type recursive: bool
        :rtype: typing.Iterable[Path]

        **中文文档**

        选择所有 :attr:`pathlib_mate.pathlib2.Path.atime` 在一定范围内的文件。
        """

        def filters(p): return min_time <= p.atime <= max_time

        return self.select_file(filters, recursive)

    def select_by_ctime(
        self,
        min_time=0,
        max_time=ts_2100,
        recursive=True,
    ):
        """
        Select file path by create time.

        :type self: Path

        :type min_time: Union[int, float]
        :param min_time: lower bound timestamp

        :type max_time: Union[int, float]
        :param max_time: upper bound timestamp

        :type recursive: bool
        :rtype: typing.Iterable[Path]

        **中文文档**

        选择所有 :attr:`pathlib_mate.pathlib2.Path.ctime` 在一定范围内的文件。
        """

        def filters(p): return min_time <= p.ctime <= max_time

        return self.select_file(filters, recursive)

    # --- Select Special File Type ---
    _image_ext = [
        ".jpg", ".jpeg", ".png", ".gif", ".tiff",
        ".bmp", ".ppm", ".pgm", ".pbm", ".pnm", ".svg",
    ]

    def select_image(self, recursive=True):
        """
        Select image file.

        :type self: Path
        :type recursive: bool
        :rtype: typing.Iterable[Path]
        """
        return self.select_by_ext(self._image_ext, recursive)

    _audio_ext = [
        ".mp3", ".mp4", ".aac", ".m4a", ".wma",
        ".wav", ".ape", ".tak", ".tta",
        ".3gp", ".webm", ".ogg",
    ]

    def select_audio(self, recursive=True):  # pragma: no cover
        """
        Select audio file.

        :type self: Path
        :type recursive: bool
        :rtype: typing.Iterable[Path]
        """
        return self.select_by_ext(self._audio_ext, recursive)

    _video_ext = [
        ".avi", ".wmv", ".mkv", ".mp4", ".flv",
        ".vob", ".mov", ".rm", ".rmvb", "3gp", ".3g2", ".nsv", ".webm",
        ".mpg", ".mpeg", ".m4v", ".iso",
    ]

    def select_video(self, recursive=True):  # pragma: no cover
        """
        Select video file.

        :type self: Path
        :type recursive: bool
        :rtype: typing.Iterable[Path]
        """
        return self.select_by_ext(self._video_ext, recursive)

    _ms_word_ext = [".doc", ".docx", ".docm", ".dotx", ".dotm", ".docb"]

    def select_word(self, recursive=True):  # pragma: no cover
        """
        Select Microsoft Word file.

        :type self: Path
        :type recursive: bool
        :rtype: typing.Iterable[Path]
        """
        return self.select_by_ext(self._ms_word_ext, recursive)

    _ms_excel_ext = [".xls", ".xlsx", ".xlsm", ".xltx", ".xltm"]

    def select_excel(self, recursive=True):  # pragma: no cover
        """
        Select Microsoft Excel file.

        :type self: Path
        :type recursive: bool
        :rtype: typing.Iterable[Path]
        """
        return self.select_by_ext(self._ms_excel_ext, recursive)

    _archive_ext = [".zip", ".rar", ".gz", ".tar.gz", ".tgz", ".7z"]

    def select_archive(self, recursive=True):  # pragma: no cover
        """
        Select compressed archive file.

        :type self: Path
        :type recursive: bool
        :rtype: typing.Iterable[Path]
        """
        return self.select_by_ext(self._archive_ext, recursive)

    sort_by_abspath = _sort_by("abspath")
    """
    Sort list of :class:`Path` by absolute path.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_fname = _sort_by("fname")
    """
    Sort list of :class:`Path` by file name.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_ext = _sort_by("ext")
    """
    Sort list of :class:`Path` by extension.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_size = _sort_by("size")
    """
    Sort list of :class:`Path` by file size.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_mtime = _sort_by("mtime")
    """
    Sort list of :class:`Path` by modify time.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_atime = _sort_by("atime")
    """
    Sort list of :class:`Path` by access time.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_ctime = _sort_by("ctime")
    """
    Sort list of :class:`Path` by create time.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    sort_by_md5 = _sort_by("md5")
    """
    Sort list of :class:`Path` by md5.

    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """

    @property
    def dirsize(self):
        """
        Return total file size (include sub folder). Symlink doesn't count.
        """
        total = 0
        for p in self.select_file(recursive=True):
            try:
                total += p.size
            except:  # pragma: no cover
                print("Unable to get file size of: %s" % p)
        return total
