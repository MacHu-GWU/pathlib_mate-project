.. include:: ../../README.rst

.. _document:

Documentation
==============================================================================

For all ``pathlib_mate`` exclusive features, see :class:`~pathlib_mate.mate_attr_accessor.AttrAccessor`.


Attribute
------------------------------------------------------------------------------

First, let's use a simple file for demonstration ``C:\Users\admin\readme.txt``:

.. code-block:: python

	>>> from pathlib_mate import Path
	>>> p = Path(r"C:\Users\admin\readme.txt")

``pathlib_mate`` provides a set of very straightforward attribute name:

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.abspath`

.. code-block:: python

	>>> p.abspath # Absolute path.
	'C:\Users\admin\readme.txt'

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.dirpath`

.. code-block:: python

	>>> p.dirpath # Parent dir full absolute path.
	'C:\Users\admin'

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.dirname`

.. code-block:: python

	>>> p.dirname # Parent dir name.
	'admin'

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.basename`

.. code-block:: python

	>>> p.basename # File name with extension, path is not included.
	'readme.txt'

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.fname`

.. code-block:: python

	>>> p.fname # File name without extension.
	'readme'

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.ext`

.. code-block:: python

	>>> p.ext # File extension. If it's a dir, then return empty str.
	'.txt'

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.md5`

.. code-block:: python

	>>> p.md5 # md5 check sum of this file (if file exists)

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.size`

.. code-block:: python

	>>> p.size # size in bytes
	1873

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.size_in_text`

.. code-block:: python

	>>> p.size_in_text # human readable string of the file size
	'1.83 KB'

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.mtime`

.. code-block:: python

	>>> p.mtime # Most recent modify time in timestamp. (atime, ctime is similar)
	1451624400

:meth:`~pathlib_mate.mate_attr_accessor.AttrAccessor.modify_datetime`

.. code-block:: python

	>>> p.modify_datetime # Most recent modify time in datetime.
	datetime.datetime(2016, 1, 1, 5, 0) # (access_datetime, create_datetime is similar)


.. code-block:: python

	>>> p = Path(r"C:\Users\admin")
	C:\Users\admin\

:meth:`~pathlib_mate.mate_path_filters.PathFilters.n_file`

.. code-block:: python

	>>> p.n_file # count how many file under this directory
	1000

:meth:`~pathlib_mate.mate_path_filters.PathFilters.n_dir`

.. code-block:: python

	>>> p.n_dir # count how many folders under this directory
	10


Method
------------------------------------------------------------------------------

**Rename / Cut a file**: :meth:`~pathlib_mate.mate_mutate_methods.MutateMethods.moveto()`

The default :meth:`~pathlib_mate.mate_mutate_methods.MutateMethods.rename` method is not good enough. ``pathlib_mate`` provide a new utility method ``Path.moveto(new_abspath=None, new_dirpath=None, new_dirname=None, new_basename=None, new_fname=None, new_ext=None, makedirs=False)`` making rename way more easier.

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


**Copy a file**: :meth:`~pathlib_mate.mate_mutate_methods.MutateMethods.copyto()`

In addition, ``Path.copyto(new_abspath=None, new_dirpath=None, new_dirname=None, new_fname=None, new_basename=None, new_ext=None, overwrite=False, makedirs=False)`` works same as ``Path.moveto()``, but it's a **copy operation**. By default, **it doesn't allow overwrite**.


**Remove a file**: :meth:`~pathlib_mate.mate_mutate_methods.MutateMethods.remove()`

And, you can use Path.remove() to remove the file form your disk, if it is a file.

.. code-block:: python

	>>> p.remove()


**Selecting specific files from a directory, sorting the result set, are very common needs. But the** :meth:`~pathlib_mate.pathlib2.Path.glob()` and :meth:`~pathlib_mate.pathlib2.Path.iterdir()` **is not convenient enough**. Let's see how easy it's done with ``pathlib_mate``, and it's super powerful.

**Select file and dir**: :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_file()`, :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_dir()`

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

**Filtering**:

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
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_image()`: Select image file.
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_audio()`: Select audio file.
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_video()`: Select video file.
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_word()`: Select compressed archive file.
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_excel()`: Select Microsoft Excel file.
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.select_archive()`: Select compressed archive file.


**Sort result set**

Sort set of path is super easy in ``pathlib_mate``:

.. code-block:: python

    result = path.select_file()
    # sort file by its size, from largest to smallest
    >>> for p in Path.sort_by_size(result, reverse=True):
    ...

In addition, you have these options for sorting.

- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_abspath()`
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_fname()`
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_ext()`
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_size()`
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_mtime()`
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_atime()`
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_ctime()`
- :meth:`~pathlib_mate.mate_path_filters.PathFilters.sort_by_md5()`


Utility Tools
------------------------------------------------------------------------------

- :meth:`~pathlib_mate.mate_tool_box.ToolBox.file_stat()`: return how many file, directory and totalsize of a direcoty.
- :meth:`~pathlib_mate.mate_tool_box.ToolBox.file_stat_for_all()`: return stat for this directory and all subfolders.
- :meth:`~pathlib_mate.mate_tool_box.ToolBox.print_big_dir()`: Display top-n big directory in a directory.
- :meth:`~pathlib_mate.mate_tool_box.ToolBox.print_big_file()`: Display top-n big file in a directory.
- :meth:`~pathlib_mate.mate_tool_box.ToolBox.print_big_dir_and_big_file()`: Display top-n big dir and big file in a directory.
- :meth:`~pathlib_mate.mate_tool_box_zip.ToolBoxZip.make_zip_archive` ``(dst=None)``: Use .gitignore file format to select files except those user defined, and make a zip archive for that directory.
- :meth:`~pathlib_mate.mate_tool_box_zip.ToolBoxZip.backup` ``(dst=None, ignore=None, ignore_ext=None, ignore_pattern=None, ignore_size_smaller_than=None, ignore_size_larger_than=None, case_sensitive=False)``: Use .gitignore file format to select files except those user defined, and make a zip archive for that directory.
- :meth:`~pathlib_mate.mate_tool_box.ToolBox.execute_pyfile()`: execute all python file as main script. usually for testing.
- :meth:`~pathlib_mate.mate_tool_box.ToolBox.trail_space()` ``(filters=lambda p: p.ext == ".py")``: trail all tailing empty space for each line for selected files.
- :meth:`~pathlib_mate.mate_tool_box.ToolBox.autopep8()`: auto reformat all python script in pep8 style.


.. include:: author.rst


API Document
------------------------------------------------------------------------------

* :ref:`by Name <genindex>`
* :ref:`by Structure <modindex>`