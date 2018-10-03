# -*- coding: utf-8 -*-

"""
Provides additional attribute accessor.
"""

import six
from datetime import datetime

from .str_encode import encode_hexstr
from .helper import repr_data_size


class AttrAccessor(object):
    """
    Provides additional attribute accessor.
    """

    # --- property methods that returns a value ---
    @property
    def abspath(self):
        r"""
        Absolute path.

        Example: ``C:\User\admin\readme.txt`` for ``C:\User\admin\readme.txt``
        """
        return self.absolute().__str__()

    @property
    def abspath_hexstr(self):
        """
        Return absolute path encoded in hex string.
        """
        return encode_hexstr(self.abspath)

    @property
    def dirpath(self):
        r"""
        Parent dir full absolute path.

        Example: ``C:\User\admin`` for ``C:\User\admin\readme.txt``
        """
        return self.parent.abspath

    @property
    def dirpath_hexstr(self):
        """
        Return dir full absolute path encoded in hex string.
        """
        return encode_hexstr(self.dirpath)

    @property
    def dirname(self):
        r"""
        Parent dir name.

        Example: ``admin`` for ``C:\User\admin\readme.txt``
        """
        return self.parent.name

    @property
    def dirname_hexstr(self):
        """
        Parent dir name in hex string.
        """
        return encode_hexstr(self.dirname)

    @property
    def basename(self):
        r"""
        File name with extension, path is not included.

        Example: ``readme.txt`` for ``C:\User\admin\readme.txt``
        """
        return self.name

    @property
    def basename_hexstr(self):
        """
        File name with extension encoded in hex string.
        """
        return encode_hexstr(self.basename)

    @property
    def fname(self):
        r"""
        File name without extension.

        Example: ``readme`` for ``C:\User\admin\readme.txt``
        """
        return self.stem

    @property
    def fname_hexstr(self):
        """
        File name encoded in hex string.
        """
        return encode_hexstr(self.fname)

    @property
    def ext(self):
        r"""
        File extension. If it's a dir, then return empty str.

        Example: ``.txt`` for ``C:\User\admin\readme.txt``
        """
        return self.suffix

    @property
    def size(self):
        """
        File size in bytes.
        """
        try:
            return self._stat.st_size
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.size

    @property
    def size_in_text(self):
        """
        File size as human readable string.
        """
        return repr_data_size(self.size, precision=2)

    @property
    def mtime(self):
        """
        Get most recent modify time in timestamp.
        """
        try:
            return self._stat.st_mtime
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.mtime

    @property
    def atime(self):
        """
        Get most recent access time in timestamp.
        """
        try:
            return self._stat.st_atime
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.atime

    @property
    def ctime(self):
        """
        Get most recent create time in timestamp.
        """
        try:
            return self._stat.st_ctime
        except:  # pragma: no cover
            self._stat = self.stat()
            return self.ctime

    @property
    def modify_datetime(self):
        """
        Get most recent modify time in datetime.
        """
        return datetime.fromtimestamp(self.mtime)

    @property
    def access_datetime(self):
        """
        Get most recent access time in datetime.
        """
        return datetime.fromtimestamp(self.atime)

    @property
    def create_datetime(self):
        """
        Get most recent create time in datetime.
        """
        return datetime.fromtimestamp(self.ctime)

    def __contains__(self, item):
        if isinstance(item, six.string_types):
            return self.abspath in item
        else:
            return self.abspath in item.abspath

    def __iter__(self):
        current_self = self.__class__(self)
        while 1:
            parent = current_self.parent
            if parent == current_self:
                yield current_self
                break
            else:
                yield current_self
                current_self = parent
