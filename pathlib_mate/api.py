# -*- coding: utf-8 -*-

"""
Public API of this package.
"""

import os

from .pathlib2 import Path
from .pathlib2 import WindowsPath
from .pathlib2 import PosixPath
PathCls = WindowsPath if os.name == "nt" else PosixPath
