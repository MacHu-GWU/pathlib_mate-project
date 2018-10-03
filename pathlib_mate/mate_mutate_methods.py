# -*- coding: utf-8 -*-

"""
Provide methods to mutate the Path instance.
"""

import os
import shutil


class MutateMethods(object):
    """
    Provide methods to mutate the Path instance.
    """
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
               new_dirpath=None,
               new_dirname=None,
               new_basename=None,
               new_fname=None,
               new_ext=None):
        """
        Return a new :class:`pathlib_mate.pathlib2.Path` object with updated information.
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
        else:  # pragma: no cover
            return True

    def moveto(self,
               new_abspath=None,
               new_dirpath=None,
               new_dirname=None,
               new_basename=None,
               new_fname=None,
               new_ext=None,
               overwrite=False,
               makedirs=False):
        """
        An advanced :meth:`pathlib_mate.pathlib2.Path.rename` method provide ability to rename by
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
               new_dirpath=None,
               new_dirname=None,
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
                try:
                    shutil.copy(self.abspath, p.abspath)
                except IOError as e:
                    if makedirs:
                        os.makedirs(p.parent.abspath)
                        shutil.copy(self.abspath, p.abspath)
                    else:
                        raise e
        return p

    def remove(self, *args, **kwargs):
        """
        Remove it.
        """
        self.unlink(*args, **kwargs)
