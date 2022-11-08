Release and Version History
===========================

x.x.x (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


1.1.1 (2022-11-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Minor Improvements**

- more coverage test for ``Path.make_zip_archive`` method

**Miscellaneous**

- Python2.7 and 3.6 are still supported, but not fully tested.
- now ``autopep8`` is an optional feature, not a required dependency.


1.0.3 (2022-03-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``dir_here`` method.
- add ``parse_data_size`` function.

**Minor Improvements**

- add lots of API document.

**Bugfixes**

**Miscellaneous**

- refact code base, apply type hint almost everywhere, and change code style to black.


1.0.2 (2021-12-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``remove_if_exists`` and ``mkdir_if_not_exists`` syntax sugar method.


1.0.1 (2020-12-04) Feature Improvement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``atomic_write_bytes`` and ``atomic_write_text`` method. Preventing overwriting existing file with incomplete data.
- now ``write_text`` use "utf-8" encoding by default

**Minor Improvements**

**Bugfixes**

**Miscellaneous**

- Move CI to github Action


1.0.0 (2020-03-14) First Production Ready Version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- type hint support for all method.

**Minor Improvements**

- since Python2.7 is no longer supported. but pathlib_mate still supports Python2.7, it bump ``pathlib2`` version to the latest 2.3.5

**Bugfixes**

**Miscellaneous**


0.0.11 (2017-08-31) MileStone
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A stable, rich features, fully tested version.


0.0.1 (2016-09-07)
~~~~~~~~~~~~~~~~~~
- First release