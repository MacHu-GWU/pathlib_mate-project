# -*- coding: utf-8 -*-

"""
Provide methods to mutate the Path instance.
"""

import os
import shutil

# for type hint only
try:  # pragma: no cover
    from typing import TYPE_CHECKING, Union

    if TYPE_CHECKING:
        from .pathlib2 import Path

except ImportError:  # pragma: no cover
    pass


class MutateMethods(object):
    """
    Provide methods to mutate the Path instance.
    """

    # --- methods return another Path ---
    def drop_parts(self, n=1):
        """
        Drop number of parts from the ends. By default, it is equal to
        ``self.parent``.

        Example::

            >>> Path("/usr/bin/python").drop_parts(1)
            "/user/bin"

            >>> Path("/usr/bin/python").drop_parts(2)
            "/user"

        :type self: Path

        :type n: int
        :param n: integer, number of parts you wants to drop from ends.
          n has to greater equal than 0.

        :rtype: Path
        :returns: a new Path object.
        """
        return self.__class__(*self.parts[:-n])

    def append_parts(self, *parts):
        """
        Append some parts to the end of this path.

        Example::

            >>> Path("/usr/bin/python").append_parts("lib")
            "/user/bin/python/lib"

            >>> Path("/usr/bin/python").append_parts("lib", "core.py")
            "/user/bin/python/lib/core.py"

        :type self: Path

        :rtype: Path
        :returns: a new Path object.
        """
        return self.__class__(self, *parts)

    def change(
        self,
        new_abspath=None,
        new_dirpath=None,
        new_dirname=None,
        new_basename=None,
        new_fname=None,
        new_ext=None,
    ):
        """
        Return a new :class:`pathlib_mate.pathlib2.Path` object with updated path.

        Example::

            >>> Path("/Users/alice/test.py").change(new_fname="test1")
            /Users/alice/test1.py

            >>> Path("/Users/alice/test.py").change(new_ext=".txt")
            /Users/alice/test.txt

            >>> Path("/Users/alice/test.py").change(new_dirname="bob")
            /Users/bob/test.py

            >>> Path("/Users/alice/test.py").change(new_dirpath="/tmp")
            /tmp/test.py

        :type self: Path
        :type new_abspath: Union[str, Path]
        :type new_dirpath: str
        :type new_dirname: str
        :type new_basename: str
        :type new_fname: str
        :type new_ext: str

        :rtype: Path

        **中文文档**

        高级重命名函数, 允许用于根据路径的各个组成部分进行重命名. 但和 os.rename
        方法一样, 需要保证母文件夹存在.
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

    def is_not_exist_or_allow_overwrite(self, overwrite=False):  # pragma: no cover
        """
        Test whether a file target is not exists or it exists but allow
        overwrite.

        :type self: Path
        :param overwrite: bool

        :rtype: bool
        """
        if (not self.exists()) or (overwrite is True):
            return True
        else:
            return False

    def moveto(
        self,
        new_abspath=None,
        new_dirpath=None,
        new_dirname=None,
        new_basename=None,
        new_fname=None,
        new_ext=None,
        overwrite=False,
        makedirs=False,
    ):
        """
        Similar to :meth:`~pathlib_mate.mate_mutate_methods.MutateMethods.change`
        method. However, it move the original path to new location.

        :type self: Path
        :type new_abspath: Union[str, Path]
        :type new_dirpath: str
        :type new_dirname: str
        :type new_basename: str
        :type new_fname: str
        :type new_ext: str
        :type overwrite: bool
        :type makedirs: bool
        :rtype: Path

        **中文文档**

        高级 文件 / 文件夹 移动函数, 允许用于根据路径的各个组成部分进行重命名, 然后移动.
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

    def copyto(
        self,
        new_abspath=None,
        new_dirpath=None,
        new_dirname=None,
        new_basename=None,
        new_fname=None,
        new_ext=None,
        overwrite=False,
        makedirs=False,
    ):
        """
        Similar to :meth:`~pathlib_mate.mate_mutate_methods.MutateMethods.change`
        method. However, it copy the original path to new location.

        :type self: Path
        :type new_abspath: Union[str, Path]
        :type new_dirpath: str
        :type new_dirname: str
        :type new_basename: str
        :type new_fname: str
        :type new_ext: str
        :type overwrite: bool
        :type makedirs: bool
        :rtype: Path

        **中文文档**

        高级 文件 / 文件夹 拷贝函数, 允许用于根据路径的各个组成部分进行重命名, 然后拷贝.
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
                try:
                    shutil.copy(self.abspath, p.abspath)
                except IOError as e:
                    if makedirs:
                        os.makedirs(p.parent.abspath)
                        shutil.copy(self.abspath, p.abspath)
                    else:
                        raise e
        return p

    def remove(self):
        """
        Remove this file. Won't work if it is a directory.

        :type self: Path
        """
        self.unlink()

    def remove_if_exists(self):
        """
        Remove a file or entire directory recursively.

        :type self: Path
        """
        if self.exists():
            if self.is_dir():
                shutil.rmtree(self.abspath)
            else:
                self.remove()

    def mkdir_if_not_exists(self):
        """
        Make a directory if not exists yet.

        :type self: Path
        """
        self.mkdir(parents=True, exist_ok=True)

    @classmethod
    def dir_here(cls, file_var):
        """
        Return the directory of the python script that where this method
        is called.

        Suppose you have a file structure like this::

            /Users/myname/test.py

        And it is the content of ``test.py``::

            from pathlib_mate import Path

            dir_here = Path.dir_here(__file__)

            print(dir_here) # /Users/myname

        :type file_var: str
        :param file_var: the __file__ variable

        :rtype: Path
        """
        return cls(file_var).absolute().parent
