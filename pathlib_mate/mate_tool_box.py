# -*- coding: utf-8 -*-

"""
File system utility tool box. mimic linux ``md5``, ``zip``, etc...
"""

try:  # pragma: no cover
    from typing import TYPE_CHECKING, Callable, List, Union

    if TYPE_CHECKING:
        from .pathlib2 import Path

except ImportError:  # pragma: no cover
    pass

import os
import six
import hashlib
import autopep8

from .mate_path_filters import all_true
from .helper import repr_data_size
from .mate_tool_box_zip import ToolBoxZip


class ToolBox(ToolBoxZip):
    def get_dir_fingerprint(self, hash_meth):
        """
        Return md5 fingerprint of a directory. Calculation is based on
        iterate recursively through all files, ordered by absolute path,
        and stream in md5 for each file.

        :type self: Path
        :type hash_meth: Callable

        :rtype: str
        """
        m = hash_meth()
        for p in self.sort_by_abspath(self.select_file(recursive=True)):
            m.update(str(p).encode("utf-8"))
            m.update(p.md5.encode("utf-8"))
        return m.hexdigest()

    @property
    def dir_md5(self):
        """
        Return md5 fingerprint of a directory.

        See :meth:`ToolBox.get_dir_fingerprint` for details

        :type self: Path

        :rtype: str
        """
        return self.get_dir_fingerprint(hashlib.md5)

    @property
    def dir_sha256(self):
        """
        Return sha256 fingerprint of a directory.

        See :meth:`ToolBox.get_dir_fingerprint` for details

        :type self: Path

        :rtype: str
        """
        return self.get_dir_fingerprint(hashlib.sha256)

    @property
    def dir_sha512(self):
        """
        Return sha512 fingerprint of a directory.

        See :meth:`ToolBox.get_dir_fingerprint` for details

        :type self: Path

        :rtype: str
        """
        return self.get_dir_fingerprint(hashlib.sha512)

    def is_empty(self, strict=True):
        """
        If it's a file, check if it is a empty file. (0 bytes content)

        If it's a directory, check if there's no file and dir in it.
            But if ``strict = False``, then only check if there's no file in it.

        :type self: Path

        :type strict: bool
        :param strict: only useful when it is a directory. if True, only
            return True if this dir has no dir and file. if False, return True
            if it doesn't have any file.

        :rtype: bool
        """
        if self.exists():
            if self.is_file():
                return self.size == 0
            elif self.is_dir():
                if strict:
                    return len(list(self.select(recursive=True))) == 0
                else:  # pragma: no cover
                    return len(list(self.select_file(recursive=True))) == 0
            else:  # pragma: no cover
                msg = "'%s' is not either file or directory! (maybe simlink)" % self
                raise EnvironmentError(msg)
        else:
            raise EnvironmentError("'%s' not exists!" % self)

    def auto_complete_choices(self, case_sensitive=False):
        """
        A command line auto complete similar behavior. Find all item with same
        prefix of this one.

        :type self: Path

        :type case_sensitive: bool
        :param case_sensitive: toggle if it is case sensitive.

        :rtype: List[Path]
        :return: list of :class:`pathlib_mate.pathlib2.Path`.
        """
        self_basename = self.basename
        self_basename_lower = self.basename.lower()
        if case_sensitive:  # pragma: no cover
            def match(basename):
                return basename.startswith(self_basename)
        else:
            def match(basename):
                return basename.lower().startswith(self_basename_lower)

        choices = list()
        if self.is_dir():
            choices.append(self)
            for p in self.sort_by_abspath(self.select(recursive=False)):
                choices.append(p)
        else:
            p_parent = self.parent
            if p_parent.is_dir():
                for p in self.sort_by_abspath(p_parent.select(recursive=False)):
                    if match(p.basename):
                        choices.append(p)
            else:  # pragma: no cover
                raise ValueError("'%s' directory does not exist!" % p_parent)
        return choices

    # --- Directory Exclusive Method ---
    def print_big_dir(self, top_n=5):
        """
        Print ``top_n`` big dir in this dir.

        :type self: Path
        :type top_n: int
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
        """
        Print ``top_n`` big file in this dir.

        :type self: Path
        :type top_n: int
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
        """
        Print ``top_n`` big dir and ``top_n`` big file in each dir.

        :type self: Path
        :type top_n: int
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

    def file_stat_for_all(self, filters=all_true):  # pragma: no cover
        """
        Find out how many files, directories and total size (Include file in
        it's sub-folder) it has for each folder and sub-folder.

        :type self: Path
        :type filters: Callable

        :rtype: dict
        :returns: stat, a dict like ``{"directory path": {
          "file": number of files, "dir": number of directories,
          "size": total size in bytes}}``

        **中文文档**

        返回一个目录中的每个子目录的, 文件, 文件夹, 大小的统计数据。
        """
        self.assert_is_dir_and_exists()

        from collections import OrderedDict

        stat = OrderedDict()
        stat[self.abspath] = {"file": 0, "dir": 0, "size": 0}

        for p in self.select(filters=filters, recursive=True):
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

        :type self: Path
        :type filters: Callable

        :rtype: dict
        :returns: stat, a dict like ``{"file": number of files,
          "dir": number of directorys, "size": total size in bytes}``

        **中文文档**

        返回一个目录中的文件, 文件夹, 大小的统计数据。
        """
        self.assert_is_dir_and_exists()

        stat = {"file": 0, "dir": 0, "size": 0}

        for p in self.select(filters=filters, recursive=True):
            if p.is_file():
                stat["file"] += 1
                stat["size"] += p.size
            elif p.is_dir():
                stat["dir"] += 1

        return stat

    def mirror_to(self, dst):  # pragma: no cover
        """
        Create a new folder having exactly same structure with this directory.
        However, all files are just empty file with same file name.

        :type self: Path

        :type dst: str
        :param dst: destination directory. The directory can't exists before
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

    def execute_pyfile(self, py_exe=None):  # pragma: no cover
        """
        Execute every ``.py`` file as main script.

        :type self: Path

        :type py_exe: str
        :param py_exe: python command or python executable path.

        **中文文档**

        将目录下的所有 Python 文件作为主脚本用当前解释器运行。
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

    def trail_space(self, filters=lambda p: p.ext == ".py"):  # pragma: no cover
        """
        Trail white space at end of each line for every ``.py`` file.

        :type self: Path
        :type filters: Callable

        **中文文档**

        将目录下的所有被选择的文件中行末的空格删除.
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

    def autopep8(self, **kwargs):  # pragma: no cover
        """
        Auto convert your python code in a directory to pep8 styled code.

        :type self: Path
        :param kwargs: arguments for ``autopep8.fix_code`` method.

        **中文文档**

        将目录下的所有 Python 文件用 pep8 风格格式化. 增加其可读性和规范性.
        """
        self.assert_is_dir_and_exists()

        for p in self.select_by_ext(".py"):
            with open(p.abspath, "rb") as f:
                code = f.read().decode("utf-8")

            formatted_code = autopep8.fix_code(code, **kwargs)

            with open(p.abspath, "wb") as f:
                f.write(formatted_code.encode("utf-8"))
