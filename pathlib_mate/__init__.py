#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pathlib_mate provide extensive methods, attributes for pathlib.
"""

__version__ = "0.0.15"
__short_description__ = "An extended and more powerful pathlib."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__maintainer__ = "Sanhe Hu"
__maintainer_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

import os

try:
    from .pathlib2 import Path, WindowsPath, PosixPath

    PathCls = WindowsPath if os.name == "nt" else PosixPath
except Exception as e:  # pragma: no cover
    print(e)
    pass
