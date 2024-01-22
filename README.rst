.. image:: https://readthedocs.org/projects/pathlib_mate/badge/?version=latest
    :target: https://pathlib-mate.readthedocs.io/?badge=latest
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/pathlib_mate-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/pathlib_mate-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/pathlib_mate-project/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/MacHu-GWU/pathlib_mate-project

.. image:: https://img.shields.io/pypi/v/pathlib_mate.svg
    :target: https://pypi.python.org/pypi/pathlib_mate

.. image:: https://img.shields.io/pypi/l/pathlib_mate.svg
    :target: https://pypi.python.org/pypi/pathlib_mate

.. image:: https://img.shields.io/pypi/pyversions/pathlib_mate.svg
    :target: https://pypi.python.org/pypi/pathlib_mate

.. image:: https://img.shields.io/pypi/dm/pathlib_mate.svg
    :target: https://github.com/MacHu-GWU/pathlib_mate-project

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pathlib_mate-project/blob/master/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pathlib_mate-project


------


.. image:: https://img.shields.io/badge/Link-Document-blue.svg
      :target: https://pathlib-mate.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
      :target: https://pathlib-mate.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
      :target: https://pathlib-mate.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
      :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/pathlib_mate-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
      :target: https://github.com/MacHu-GWU/pathlib_mate-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
      :target: https://github.com/MacHu-GWU/pathlib_mate-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.org/pypi/pathlib_mate#files


Welcome to ``pathlib_mate`` Documentation
==============================================================================

`pathlib <https://docs.python.org/3/library/pathlib.html>`_ is an awesome library handling path in different OS. And it's been added into standard library since Python3.4. ``pathlib_mate`` gives extensive methods and attributes, makes ``pathlib`` more powerful and user-friendly.

Features:

**Convenient Attribute Accessor**:

.. code-block:: python

    >>> p = Path("/Users/username/test.py").

    >>> p.abspath
    /Users/username/test.py

    >>> p.basename
    test.py

    >>> p.fname
    test

    >>> p.ext
    .py

    >>> p.dirname
    username

    >>> p.dirpath
    /Users/username

    >>> p.size
    1500

    >>> p.size_in_text
    1.46 KB

    >>> p.create_datetime
    datetime(2018, 1, 15, 8, 30, 15)

    >>> p.md5
    415f12f07a7e01486cc82856621e05bf

    >>> p.sha256
    d51512cb0ac71484c01c475409a73225d0149165024d7aac6d8e655eedf2c025

    >>> p.sha512
    7882fc375840cafa364eaf29dc424645b72fcdbe61fc3326c5afd98e70f696e4f390e0e3f159eac2cb60cedc0992ef7b5f8744a4481911e914a7c5b979e6de68

**Powerful Path Search**:

.. code-block:: python

    >>> p = Path("/Users/username/Documents")

    >>> for path in p.select_file(recursive=True)
    ...

    >>> for path in p.select_file(recursive=False)
    ...

    >>> for path in p.select_dir(recursive=True)
    ...

    >>> for image_file in p.select_by_ext([".jpg", ".png"])
    ...

    >>> for big_file in p.select_by_size(min_size=1000000)
    ...

    >>> for video_file in p.select_video():
    ...

    # You can customize the filter anyway you want
    >>> def py_filter(p): return ".py" == p.ext.lower()
    >>> for py_file in p.select_file(py_filter):
    ...


**Eazy to use File / Dir Operation**:

.. code-block:: python

    >>> p = Path("/Users/username/Documents/Readme.txt")

    # mutate
    >>> p.change(new_ext=".md")
    /Users/username/Documents/Readme.md

    >>> p.change(new_fname="Tutorial")
    /Users/username/Documents/Tutorial.txt

    >>> p.change(new_basename="README.rst")
    /Users/username/Documents/README.rst

    >>> p.change(new_dirname="Downloads")
    /Users/username/Downloads/Readme.txt

    >>> p.change(new_dirpath="/User/username/Downloads)
    /Users/username/Downloads/Readme.txt

    >>> p.change(new_abspath="/Users/username/Downloads/Readme.txt")
    /Users/username/Downloads/Readme.txt

    # copy
    >>> p.moveto(new_ext=".md", makedirs=True)

    # cut
    >>> p.copyto(new_ext=".md", makedirs=True)

    # delete
    >>> p.remove()

    # delete file or directory recursively, ignore if not exists
    >>> p.remove_if_exists()

    # make dir and required parents recursively, if not exists
    >>> p.mkdir_if_not_exists()


**Atomic Write Support**:

If anything wrong happens during writing big chunk of data into a file. It may leave you an incomplete file. Atomic write can guarantee either 100% done or nothing happens.

Thanks for `boltons <https://boltons.readthedocs.io/en/latest/>`_ project. Now ``pathlib_mate`` supports atomic write API:

.. code-block:: python

    >>> p = Path("test.dat")
    >>> s = "Hello World"
    >>> b = s.encode("utf-8)
    >>> p.atomic_write_bytes(b, overwrite=True)
    >>> p.atomic_write_text(s, overwrite=True)
    >>> with p.atomic_open("wb") as f:
    ...     f.write(b) # write large binary data


**Powerful Production Tools**:

.. code-block:: python

    >>> p = Path("/Users/username/Documents/Github/pathlib_mate-project")

    >>> p.print_big_dir_and_big_file()
    ...

    >>> p.file_stat()
    {"file": 122, "dir": 41, "size": 619682}

    # file statistics, include sub folder
    >>> p.file_stat_for_all()

    # make an zip archive for the directory, auto naming
    >>> p.make_zip_archive()

    # make an zip archive for the directory, auto naming
    >>> p.backup()


.. _install:

Install
------------------------------------------------------------------------------

``pathlib_mate`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install pathlib_mate

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pathlib_mate
