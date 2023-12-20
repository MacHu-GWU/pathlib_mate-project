# -*- coding: utf-8 -*-

"""
Provide zip related functions.
"""

from typing import TYPE_CHECKING, Optional, List, Union
import os
import random
import string
from datetime import datetime
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED

from .mate_path_filters import all_true
from .helper import repr_data_size

if TYPE_CHECKING:  # pragma: no cover
    from .pathlib2 import Path

alpha_digits = string.ascii_letters + string.digits


def rand_str(length):
    """
    :type length: int

    :rtype: str
    """
    return "".join([random.choice(alpha_digits) for _ in range(length)])


class ToolBoxZip(object):
    """
    Provide zip related functions.
    """

    def _default_zip_dst(self):
        """
        automatically create destination zip file ``Path`` object.

        :type self: Path

        :rtype: Path
        """
        new_basename = "{}-{}-{}.zip".format(
            self.basename,
            datetime.now().strftime("%Y-%m-%d-%Hh-%Mm-%Ss"),
            rand_str(4),
        )
        return self.change(new_basename=new_basename)

    def make_zip_archive(
        self,
        dst=None,
        filters=all_true,
        compress=True,
        overwrite=False,
        makedirs=False,
        include_dir=True,
        verbose=False,
    ):
        """
        Make a zip archive of a directory or a file.

        :type self: Path

        :type dst: Optional[Union[Path, str]]
        :param dst: output file path. if not given, will be automatically assigned.

        :type filters: typing.Callable
        :param filters: custom path filter. By default it allows any file.

        :type compress: bool
        :param compress: compress or not.

        :type verbose: bool
        :param overwrite: overwrite exists or not.

        :type makedirs: bool
        :param makedirs: if True, automatically create the parent dir if not
            exists

        :type include_dir: bool
        :param include_dir: if True, then you will see the source dir when you
            unzip it. It only apply when zipping a directory

        :type verbose: bool
        :param verbose: display log or not.
        """
        self.assert_exists()

        if dst is None:
            dst = self._default_zip_dst()
        else:
            dst = self.change(new_abspath=dst)

        if not dst.basename.lower().endswith(".zip"):
            raise ValueError("zip archive name has to be endswith '.zip'!")

        if dst.exists():
            if not overwrite:
                raise IOError("'%s' already exists!" % dst)

        if compress:
            compression = ZIP_DEFLATED
        else:
            compression = ZIP_STORED

        if not dst.parent.exists():
            if makedirs:  # pragma: no cover
                os.makedirs(dst.parent.abspath)

        if verbose:
            msg = "Making zip archive for '%s' ..." % self
            print(msg)

        if self.is_dir():
            total_size = 0
            selected = list()
            for p in self.glob("**/*"):
                if filters(p):
                    selected.append(p)
                    total_size += p.size

            if verbose:
                msg = "Got {} files, total size is {}, compressing ...".format(
                    len(selected),
                    repr_data_size(total_size),
                )
                print(msg)

            with ZipFile(dst.abspath, "w", compression) as f:
                if include_dir:
                    relpath_root = self.parent
                else:
                    relpath_root = self
                for p in selected:
                    relpath = p.relative_to(relpath_root).__str__()
                    f.write(p.abspath, relpath)

        elif self.is_file():
            with ZipFile(dst.abspath, "w", compression) as f:
                f.write(self.abspath, self.basename)

        if verbose:
            msg = "Complete! Archive size is {}.".format(dst.size_in_text)
            print(msg)

    def backup(
        self,
        dst=None,
        ignore=None,
        ignore_ext=None,
        ignore_pattern=None,
        ignore_size_smaller_than=None,
        ignore_size_larger_than=None,
        case_sensitive=False,
        include_dir=True,
        verbose=True,
    ):  # pragma: no cover
        """
        Create a compressed zip archive backup for a directory.

        :type self: Path

        :type dst: Optional[Union[Path, str]]
        :param dst: the output file path.

        :type ignore: Optional[List[str]]
        :param ignore: file or directory defined in this list will be ignored.

        :type ignore_ext: Optional[List[str]]
        :param ignore_ext: file with extensions defined in this list will be ignored.

        :type ignore_pattern: Optional[List[str]]
        :param ignore_pattern: any file or directory that contains this pattern
            will be ignored.

        :type ignore_size_smaller_than: int
        :param ignore_size_smaller_than: any file size smaller than this
            will be ignored.

        :type ignore_size_larger_than: int
        :param ignore_size_larger_than: any file size larger than this
            will be ignored.

        :type case_sensitive: bool
        :param case_sensitive: if True, the ignore rules are case sensitive

        :type include_dir: bool
        :param include_dir: if True, then you will see the source dir when you
            unzip it. It only apply when zipping a directory

        :type verbose: bool
        :param verbose: display log or not.

        **中文文档**

        为一个目录创建一个备份压缩包。可以通过过滤器选择你要备份的文件。
        """

        def preprocess_arg(arg):  # pragma: no cover
            if arg is None:
                return []

            if isinstance(arg, (tuple, list)):
                return list(arg)
            else:
                return [
                    arg,
                ]

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

        self.make_zip_archive(
            dst=dst,
            filters=filters,
            compress=True,
            overwrite=False,
            include_dir=include_dir,
            verbose=verbose,
        )
