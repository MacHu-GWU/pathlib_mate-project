# -*- coding: utf-8 -*-

"""
Provide file hash functions.
"""

try:  # pragma: no cover
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from .pathlib2 import Path

except ImportError:  # pragma: no cover
    pass

from .hashes import md5file, sha256file, sha512file


class HashesMethods(object):
    """
    Provide hash functions.
    """

    # --- file check sum ---

    def get_partial_md5(self, nbytes):
        """
        Return md5 check sum of first n bytes of this file.

        :type self: Path
        :type nbytes: int

        :rtype: str
        """
        return md5file(abspath=self.abspath, nbytes=nbytes)

    @property
    def md5(self):
        """
        Return md5 check sum of this file.

        :type self: Path

        :rtype: str
        """
        return md5file(self.abspath)

    def get_partial_sha256(self, nbytes):
        """
        Return sha256 check sum of first n bytes of this file.

        :type self: Path
        :type nbytes: int

        :rtype: str
        """
        return sha256file(abspath=self.abspath, nbytes=nbytes)

    @property
    def sha256(self):
        """
        Return sha256 check sum of this file.

        :type self: Path

        :rtype: str
        """
        return sha256file(self.abspath)

    def get_partial_sha512(self, nbytes):
        """
        Return sha512 check sum of first n bytes of this file.

        :type self: Path
        :type nbytes: int

        :rtype: str
        """
        return sha512file(abspath=self.abspath, nbytes=nbytes)

    @property
    def sha512(self):
        """
        Return md5 check sum of this file.

        :type self: Path

        :rtype: str
        """
        return sha512file(self.abspath)
