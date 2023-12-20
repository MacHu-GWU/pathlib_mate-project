# -*- coding: utf-8 -*-

"""
An extended and more powerful pathlib in Python.
"""

from ._version import __version__

__short_description__ = "An extended and more powerful pathlib."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__maintainer__ = "Sanhe Hu"
__maintainer_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from .api import (
        Path,
        WindowsPath,
        PosixPath,
        PathCls,
        T_PATH_ARG,
    )
except ImportError as e:  # pragma: no cover
    pass
except Exception as e:  # pragma: no cover
    print(e)
