# -*- coding: utf-8 -*-

"""
Public API of this package.
"""

import os

try:
    from .pathlib2 import Path, WindowsPath, PosixPath

    PathCls = WindowsPath if os.name == "nt" else PosixPath
except ImportError as e:  # pragma: no cover
    pass
except Exception as e:  # pragma: no cover
    print(e)
