# -*- coding: utf-8 -*-

"""
pathlib_mate provide extensive methods, attributes for pathlib.
"""

from __future__ import print_function

from ._version import __version__

__short_description__ = "An extended and more powerful pathlib."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__maintainer__ = "Sanhe Hu"
__maintainer_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

import os

try:
    # from .pathlib2 import Path, WindowsPath, PosixPath
    from .python37_pathlib import Path, WindowsPath, PosixPath

    PathCls = WindowsPath if os.name == "nt" else PosixPath
except ImportError as e:  # pragma: no cover
    pass
except Exception as e:  # pragma: no cover
    print(e)
