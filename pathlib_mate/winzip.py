#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A file compress utility module. You can easily programmatically add files
and directorys to zip archives. And compress arbitrary binary content.

- :func:`zip_a_folder`: add folder to archive.
- :func:`zip_everything_in_a_folder`: add everything in a folder to archive.
- :func:`zip_many_files`: Add many files to a zip archive.
- :func:`write_gzip`: Write binary content to gzip file.
- :func:`read_gzip`: Read binary content from gzip file.

**中文文档**

提供了若干个文件和数据压缩的快捷函数。

- :func:`zip_a_folder`: 将目录添加到压缩包。
- :func:`zip_everything_in_a_folder`: 将目录内的所有文件添加到压缩包。
- :func:`zip_many_files`: 将多个文件添加到压缩包。
- :func:`write_gzip`: 将二进制数据写入文件, 例如python pickle, bytes string。
- :func:`read_gzip`: 读取解压后的二进制数据内容。

注: python中zipfile包自带的ZipFile方法的用法如下:

基本用法::

    with ZipFile("filename.zip", "w") as f:
        f.write(path)

其中path是文件路径。 如果path是文件夹, 并不会将文件夹内所有的文件添加到压缩包中。

相对路径压缩:

比如你有一个路径 ``C:\download\readme.txt``, 如果当前路径是 ``C:\``,
而此时你将 ``readme.txt`` 添加到压缩包时则是在压缩包内添加一个: ``download\readme.txt``,
如果当前路径是 ``C:\download\``, 则在压缩包内添加的路径则是: ``readme.txt``
"""

from __future__ import print_function

import os
from zipfile import ZipFile


def zip_a_folder(src, dst):
    """
    Add a folder and everything inside to zip archive.

    Example::

        |---paper
            |--- algorithm.pdf
            |--- images
                |--- 1.jpg

        zip_a_folder("paper", "paper.zip")

        paper.zip
            |---paper
                |--- algorithm.pdf
                |--- images
                    |--- 1.jpg

    **中文文档**

    将整个文件夹添加到压缩包, 包括根目录本身。
    """
    if os.path.exists(dst):
        print("destination '%s' already exist." % dst)
        return

    src, dst = os.path.abspath(src), os.path.abspath(dst)
    cwd = os.getcwd()
    todo = list()

    dirname, basename = os.path.split(src)
    os.chdir(dirname)
    for dirname, _, fnamelist in os.walk(basename):
        for fname in fnamelist:
            newname = os.path.join(dirname, fname)
            todo.append(newname)

    with ZipFile(dst, "w") as f:
        for newname in todo:
            f.write(newname)

    os.chdir(cwd)


def zip_everything_in_a_folder(src, dst):
    """
    Add everything in a folder except the root folder it self to zip archive.

    Example::

        |---paper
            |--- algorithm.pdf
            |--- images
                |--- 1.jpg

        zip_everything_in_folder("paper", "paper.zip")

        paper.zip
            |--- algorithm.pdf
            |--- images
                |--- 1.jpg

    **中文文档**

    将目录内部的所有文件添加到压缩包, 不包括根目录本身。
    """
    if os.path.exists(dst):
        print("destination '%s' already exist." % dst)
        return

    src, dst = os.path.abspath(src), os.path.abspath(dst)
    cwd = os.getcwd()
    todo = list()

    os.chdir(src)
    for dirname, _, fnamelist in os.walk(os.getcwd()):
        for fname in fnamelist:
            newname = os.path.relpath(os.path.join(dirname, fname), src)
            todo.append(newname)

    with ZipFile(dst, "w") as f:
        for newname in todo:
            f.write(newname)

    os.chdir(cwd)


def zip_many_files(list_of_abspath, dst):
    """
    Add many files to a zip archive.

    **中文文档**

    将一系列的文件压缩到一个压缩包中, 若有重复的文件名, 在zip中保留所有的副本。
    """
    if os.path.exists(dst):
        print("destination '%s' already exist." % dst)
        return

    base_dir = os.getcwd()

    with ZipFile(dst, "w") as f:
        for abspath in list_of_abspath:
            dirname, basename = os.path.split(abspath)
            os.chdir(dirname)
            f.write(basename)

    os.chdir(base_dir)
