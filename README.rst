.. image:: https://travis-ci.org/MacHu-GWU/pathlib_mate-project.svg?branch=master

.. image:: https://img.shields.io/pypi/v/pathlib_mate.svg

.. image:: https://img.shields.io/pypi/l/pathlib_mate.svg

.. image:: https://img.shields.io/pypi/pyversions/pathlib_mate.svg

.. image:: https://img.shields.io/badge/downloads-1.5k/month-brightgreen.svg


Welcome to pathlib_mate Documentation
===============================================================================
`pathlib <https://docs.python.org/3/library/pathlib.html>`_ is an awesome library handling path in different OS. And it's been added into standard library since Python3.4. ``pathlib_mate`` gives extensive methods and attributes, makes ``pathlib`` more powerful and user-friendly.


**Quick Links**
-------------------------------------------------------------------------------
- `GitHub Homepage <https://github.com/MacHu-GWU/pathlib_mate-project>`_
- `Online Documentation <document_>`_
- `PyPI download <https://pypi.python.org/pypi/pathlib_mate>`_
- `Install <install_>`_
- `Issue submit and feature request <https://github.com/MacHu-GWU/pathlib_mate-project/issues>`_
- `API reference and source code <http://pythonhosted.org/pathlib_mate/py-modindex.html>`_


.. _install:

Install
-------------------------------------------------------------------------------

``pathlib_mate`` is released on PyPI, so all you need is:

.. code-block:: console

	$ pip install pathlib_mate

To upgrade to latest version:

.. code-block:: console

	$ pip install --upgrade pathlib_mate


.. _document:


**Documentation**
-------------------------------------------------------------------------------


Extended Attributes
~~~~~~~~~~~~~~~~~~~
First, let's use a simple file for demonstration ``C:\Users\admin\readme.txt``:

.. code-block:: python

	>>> from pathlib_mate import Path
	>>> p = Path(r"C:\Users\admin\readme.txt")

``pathlib_mate`` provides a set of very straightforward attribute name:

.. code-block:: python

	>>> p.abspath # Absolute path.
	'C:\Users\admin\readme.txt'

	>>> p.dirpath # Parent dir full absolute path.
	'C:\Users\admin'

	>>> p.dirname # Parent dir name.
	'admin'

	>>> p.basename # File name with extension, path is not included.
	'readme.txt'

	>>> p.fname # File name without extension.
	'readme'

	>>> p.txt # File extension. If it's a dir, then return empty str.
	'.txt'

	>>> p.md5 # md5 check sum of this file (if exists)

	>>> p.size # size in bytes
	1873

	>>> p.size_in_text # human readable string of the file size
	'1.83 KB'

	>>> p.mtime # Most recent modify time in timestamp. (atime, ctime is similar)
	1451624400

	>>> p.modify_datetime # Most recent modify time in datetime.
	datetime.datetime(2016, 1, 1, 5, 0) # (access_datetime, create_datetime is similar)


Extended Method
~~~~~~~~~~~~~~~

**Path.moveto**:

The default ``Path.rename(target)`` method is not good enough. ``pathlib_mate`` provide a new utility method ``Path.moveto(new_abspath=None, new_dirpath=None, new_dirname=None, new_fname=None, new_ext=None)`` making rename way more easier.

.. code-block:: python
	
	# You can easily update any parts of the path
	# Plus a new Path instance will return
	>>> p_new = p.moveto(new_dirpath=r"C:\User\guest")
	>>> p_new
	'C:\User\guest\readme.txt'

	>>> p_new = p.moveto(new_fname=r"introduction")
	>>> p_new
	'C:\User\guest\introduction.txt'

	# This will silently overwrite 'C:\User\guest\introduction.txt'
	>>> p_new = p.moveto(new_fname=r"introduction", overwrite=True)


**Path.copyto**:

In addition, ``Path.copyto(new_abspath=None, new_dirpath=None, new_dirname=None, new_fname=None, new_ext=None)`` works same as ``Path.moveto()``, but it's a **copy operation**. By default, **it doesn't allow overwrite**.


**Path.remove**:

And, you can use Path.remove() to remove the file form your disk, if it is a file.

.. code-block:: python

	>>> p.remove()


**Selecting specific files from a directory, and sorting the result set, is very frequently used. But the** ``Path.glob()`` and ``Path.iterdir()`` **is not good enough**. Let's see how easy it's done with ``pathlib_mate``, and it's super powerful.

.. code-block:: python

	>>> path = Path(r"C:\User\admin")

	# This select files recursively in a directory
	>>> for p in path.select_file():
	...

	# This select directories recursively in a directory
	>>> for p in path.select_dir():
	...

If you don't want to include the subfolders (non-recursively), set ``recursive=False``.

.. code-block:: python

	>>> for p in path.select_file(recursive=False):
	...

You can easily customize the rules you use for filtering. You only need to define a filter function like this:

.. code-block:: python

	def filter_image_file(p):
	    """This filter returns True only if it is a .jpg and .png file.
	    """
	    return p.ext.lower() in [".jpg", ".png"]

	# Filter image file
	>>> for p in path.select_file(filter_image_file):
	...

Plus, ``pathlib_mate`` provides a set of utility methods for selection (They all support the ``recursive`` keyword):

- ``Path.select_by_ext(ext=[".jpg", ".png"])``: Select file path by extension.
- ``Path.select_by_pattern_in_fname(pattern="001")``: Select file path by text pattern in file name.
- ``Path.select_by_pattern_in_abspath(pattern="admin")``: Select file path by text pattern in absolute path.
- ``Path.select_by_size(min_size=0, max_size=999999999)``: Select file path by size.
- ``Path.select_by_mtime(min_time=0, max_time=999999999)``: Select file path by modify time.
- ``Path.select_by_atime(min_time=0, max_time=999999999)``: Select file path by access time.
- ``Path.select_by_ctime(min_time=0, max_time=999999999)``: Select file path by create time.
- ``Path.select_image()``: Select image file.
- ``Path.select_audio()``: Select audio file.
- ``Path.select_video()``: Select video file.
- ``Path.select_word()``: Select compressed archive file.
- ``Path.select_excel()``: Select Microsoft Excel file.
- ``Path.select_archive()``: Select compressed archive file.

**Sort result set**

Sort set of path is super easy in ``pathlib_mate``:

.. code-block:: python

	result = path.select_file()
	# sort file by its size, from largest to smallest
	>>> for p in Path.sort_by_size(result, reverse=True):
	... 

In addition, you have these options for sorting.

- ``Path.sort_by_abspath``
- ``Path.sort_by_fname``
- ``Path.sort_by_ext``
- ``Path.sort_by_size``
- ``Path.sort_by_mtime``
- ``Path.sort_by_atime``
- ``Path.sort_by_ctime``
- ``Path.sort_by_md5``