#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a REVISED version of standard pathlib.
download from https://pypi.python.org/pypi/pathlib2/

line 734::

    class PurePath(object):
        __slots__ = (
            '_drv', '_root', '_parts',
            '_str', '_hash', '_pparts', '_cached_cparts',
            '_stat', # <--- PLEASE ADD THIS!
        )
"""
import ctypes
import fnmatch
import functools
import io
import ntpath
import os
import posixpath
import re
from . import six
import sys
from collections import Sequence
from contextlib import contextmanager
from errno import EINVAL, ENOENT, ENOTDIR, EEXIST
from operator import attrgetter
from stat import (
    S_ISDIR, S_ISLNK, S_ISREG, S_ISSOCK, S_ISBLK, S_ISCHR, S_ISFIFO)
try:
    from urllib import quote as urlquote_from_bytes
except ImportError:
    from urllib.parse import quote_from_bytes as urlquote_from_bytes


try:
    intern = intern
except NameError:
    intern = sys.intern
try:
    basestring = basestring
except NameError:
    basestring = str

supports_symlinks = True
try:
    import nt
except ImportError:
    nt = None
else:
    if sys.getwindowsversion()[:2] >= (6, 0) and sys.version_info >= (3, 2):
        from nt import _getfinalpathname
    else:
        supports_symlinks = False
        _getfinalpathname = None

__all__ = [
    "PurePath", "PurePosixPath", "PureWindowsPath",
    "Path", "PosixPath", "WindowsPath",
    ]

#
# Internals
#

# --- pathlib_mate ---
import shutil
import hashlib
from datetime import datetime


def _py2_fsencode(parts):
    # py2 => minimal unicode support
    assert six.PY2
    return [part.encode('ascii') if isinstance(part, six.text_type)
            else part for part in parts]


def _try_except_fileexistserror(try_func, except_func):
    if sys.version_info >= (3, 3):
        try:
            try_func()
        except FileExistsError as exc:
            except_func(exc)
    else:
        try:
            try_func()
        except EnvironmentError as exc:
            if exc.errno != EEXIST:
                raise
            else:
                except_func(exc)


def _win32_get_unique_path_id(path):
    # get file information, needed for samefile on older Python versions
    # see http://timgolden.me.uk/python/win32_how_do_i/
    # see_if_two_files_are_the_same_file.html
    from ctypes import POINTER, Structure, WinError
    from ctypes.wintypes import DWORD, HANDLE, BOOL

    class FILETIME(Structure):
        _fields_ = [("datetime_lo", DWORD),
                    ("datetime_hi", DWORD),
                    ]

    class BY_HANDLE_FILE_INFORMATION(Structure):
        _fields_ = [("attributes", DWORD),
                    ("created_at", FILETIME),
                    ("accessed_at", FILETIME),
                    ("written_at", FILETIME),
                    ("volume", DWORD),
                    ("file_hi", DWORD),
                    ("file_lo", DWORD),
                    ("n_links", DWORD),
                    ("index_hi", DWORD),
                    ("index_lo", DWORD),
                    ]

    CreateFile = ctypes.windll.kernel32.CreateFileW
    CreateFile.argtypes = [ctypes.c_wchar_p, DWORD, DWORD, ctypes.c_void_p,
                           DWORD, DWORD, HANDLE]
    CreateFile.restype = HANDLE
    GetFileInformationByHandle = (
        ctypes.windll.kernel32.GetFileInformationByHandle)
    GetFileInformationByHandle.argtypes = [
        HANDLE, POINTER(BY_HANDLE_FILE_INFORMATION)]
    GetFileInformationByHandle.restype = BOOL
    CloseHandle = ctypes.windll.kernel32.CloseHandle
    CloseHandle.argtypes = [HANDLE]
    CloseHandle.restype = BOOL
    GENERIC_READ = 0x80000000
    FILE_SHARE_READ = 0x00000001
    FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
    OPEN_EXISTING = 3
    if os.path.isdir(path):
        flags = FILE_FLAG_BACKUP_SEMANTICS
    else:
        flags = 0
    hfile = CreateFile(path, GENERIC_READ, FILE_SHARE_READ,
                       None, OPEN_EXISTING, flags, None)
    if hfile == 0xffffffff:
        if sys.version_info >= (3, 3):
            raise FileNotFoundError(path)
        else:
            exc = OSError("file not found: path")
            exc.errno = ENOENT
            raise exc
    info = BY_HANDLE_FILE_INFORMATION()
    success = GetFileInformationByHandle(hfile, info)
    CloseHandle(hfile)
    if success == 0:
        raise WinError()
    return info.volume, info.index_hi, info.index_lo


def _is_wildcard_pattern(pat):
    # Whether this pattern needs actual matching using fnmatch, or can
    # be looked up directly as a file.
    return "*" in pat or "?" in pat or "[" in pat


class _Flavour(object):

    """A flavour implements a particular (platform-specific) set of path
    semantics."""

    def __init__(self):
        self.join = self.sep.join

    def parse_parts(self, parts):
        if six.PY2:
            parts = _py2_fsencode(parts)
        parsed = []
        sep = self.sep
        altsep = self.altsep
        drv = root = ''
        it = reversed(parts)
        for part in it:
            if not part:
                continue
            if altsep:
                part = part.replace(altsep, sep)
            drv, root, rel = self.splitroot(part)
            if sep in rel:
                for x in reversed(rel.split(sep)):
                    if x and x != '.':
                        parsed.append(intern(x))
            else:
                if rel and rel != '.':
                    parsed.append(intern(rel))
            if drv or root:
                if not drv:
                    # If no drive is present, try to find one in the previous
                    # parts. This makes the result of parsing e.g.
                    # ("C:", "/", "a") reasonably intuitive.
                    for part in it:
                        if not part:
                            continue
                        if altsep:
                            part = part.replace(altsep, sep)
                        drv = self.splitroot(part)[0]
                        if drv:
                            break
                break
        if drv or root:
            parsed.append(drv + root)
        parsed.reverse()
        return drv, root, parsed

    def join_parsed_parts(self, drv, root, parts, drv2, root2, parts2):
        """
        Join the two paths represented by the respective
        (drive, root, parts) tuples.  Return a new (drive, root, parts) tuple.
        """
        if root2:
            if not drv2 and drv:
                return drv, root2, [drv + root2] + parts2[1:]
        elif drv2:
            if drv2 == drv or self.casefold(drv2) == self.casefold(drv):
                # Same drive => second path is relative to the first
                return drv, root, parts + parts2[1:]
        else:
            # Second path is non-anchored (common case)
            return drv, root, parts + parts2
        return drv2, root2, parts2


class _WindowsFlavour(_Flavour):
    # Reference for Windows paths can be found at
    # http://msdn.microsoft.com/en-us/library/aa365247%28v=vs.85%29.aspx

    sep = '\\'
    altsep = '/'
    has_drv = True
    pathmod = ntpath

    is_supported = (os.name == 'nt')

    drive_letters = (
        set(chr(x) for x in range(ord('a'), ord('z') + 1)) |
        set(chr(x) for x in range(ord('A'), ord('Z') + 1))
    )
    ext_namespace_prefix = '\\\\?\\'

    reserved_names = (
        set(['CON', 'PRN', 'AUX', 'NUL']) |
        set(['COM%d' % i for i in range(1, 10)]) |
        set(['LPT%d' % i for i in range(1, 10)])
        )

    # Interesting findings about extended paths:
    # - '\\?\c:\a', '//?/c:\a' and '//?/c:/a' are all supported
    #   but '\\?\c:/a' is not
    # - extended paths are always absolute; "relative" extended paths will
    #   fail.

    def splitroot(self, part, sep=sep):
        first = part[0:1]
        second = part[1:2]
        if (second == sep and first == sep):
            # XXX extended paths should also disable the collapsing of "."
            # components (according to MSDN docs).
            prefix, part = self._split_extended_path(part)
            first = part[0:1]
            second = part[1:2]
        else:
            prefix = ''
        third = part[2:3]
        if (second == sep and first == sep and third != sep):
            # is a UNC path:
            # vvvvvvvvvvvvvvvvvvvvv root
            # \\machine\mountpoint\directory\etc\...
            #            directory ^^^^^^^^^^^^^^
            index = part.find(sep, 2)
            if index != -1:
                index2 = part.find(sep, index + 1)
                # a UNC path can't have two slashes in a row
                # (after the initial two)
                if index2 != index + 1:
                    if index2 == -1:
                        index2 = len(part)
                    if prefix:
                        return prefix + part[1:index2], sep, part[index2 + 1:]
                    else:
                        return part[:index2], sep, part[index2 + 1:]
        drv = root = ''
        if second == ':' and first in self.drive_letters:
            drv = part[:2]
            part = part[2:]
            first = third
        if first == sep:
            root = first
            part = part.lstrip(sep)
        return prefix + drv, root, part

    def casefold(self, s):
        return s.lower()

    def casefold_parts(self, parts):
        return [p.lower() for p in parts]

    def resolve(self, path):
        s = str(path)
        if not s:
            return os.getcwd()
        if _getfinalpathname is not None:
            return self._ext_to_normal(_getfinalpathname(s))
        # Means fallback on absolute
        return None

    def _split_extended_path(self, s, ext_prefix=ext_namespace_prefix):
        prefix = ''
        if s.startswith(ext_prefix):
            prefix = s[:4]
            s = s[4:]
            if s.startswith('UNC\\'):
                prefix += s[:3]
                s = '\\' + s[3:]
        return prefix, s

    def _ext_to_normal(self, s):
        # Turn back an extended path into a normal DOS-like path
        return self._split_extended_path(s)[1]

    def is_reserved(self, parts):
        # NOTE: the rules for reserved names seem somewhat complicated
        # (e.g. r"..\NUL" is reserved but not r"foo\NUL").
        # We err on the side of caution and return True for paths which are
        # not considered reserved by Windows.
        if not parts:
            return False
        if parts[0].startswith('\\\\'):
            # UNC paths are never reserved
            return False
        return parts[-1].partition('.')[0].upper() in self.reserved_names

    def make_uri(self, path):
        # Under Windows, file URIs use the UTF-8 encoding.
        drive = path.drive
        if len(drive) == 2 and drive[1] == ':':
            # It's a path on a local drive => 'file:///c:/a/b'
            rest = path.as_posix()[2:].lstrip('/')
            return 'file:///%s/%s' % (
                drive, urlquote_from_bytes(rest.encode('utf-8')))
        else:
            # It's a path on a network drive => 'file://host/share/a/b'
            return 'file:' + urlquote_from_bytes(
                path.as_posix().encode('utf-8'))

    def gethomedir(self, username):
        if 'HOME' in os.environ:
            userhome = os.environ['HOME']
        elif 'USERPROFILE' in os.environ:
            userhome = os.environ['USERPROFILE']
        elif 'HOMEPATH' in os.environ:
            try:
                drv = os.environ['HOMEDRIVE']
            except KeyError:
                drv = ''
            userhome = drv + os.environ['HOMEPATH']
        else:
            raise RuntimeError("Can't determine home directory")

        if username:
            # Try to guess user home directory.  By default all users
            # directories are located in the same place and are named by
            # corresponding usernames.  If current user home directory points
            # to nonstandard place, this guess is likely wrong.
            if os.environ['USERNAME'] != username:
                drv, root, parts = self.parse_parts((userhome,))
                if parts[-1] != os.environ['USERNAME']:
                    raise RuntimeError("Can't determine home directory "
                                       "for %r" % username)
                parts[-1] = username
                if drv or root:
                    userhome = drv + root + self.join(parts[1:])
                else:
                    userhome = self.join(parts)
        return userhome


class _PosixFlavour(_Flavour):
    sep = '/'
    altsep = ''
    has_drv = False
    pathmod = posixpath

    is_supported = (os.name != 'nt')

    def splitroot(self, part, sep=sep):
        if part and part[0] == sep:
            stripped_part = part.lstrip(sep)
            # According to POSIX path resolution:
            # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/
            # xbd_chap04.html#tag_04_11
            # "A pathname that begins with two successive slashes may be
            # interpreted in an implementation-defined manner, although more
            # than two leading slashes shall be treated as a single slash".
            if len(part) - len(stripped_part) == 2:
                return '', sep * 2, stripped_part
            else:
                return '', sep, stripped_part
        else:
            return '', '', part

    def casefold(self, s):
        return s

    def casefold_parts(self, parts):
        return parts

    def resolve(self, path):
        sep = self.sep
        accessor = path._accessor
        seen = {}

        def _resolve(path, rest):
            if rest.startswith(sep):
                path = ''

            for name in rest.split(sep):
                if not name or name == '.':
                    # current dir
                    continue
                if name == '..':
                    # parent dir
                    path, _, _ = path.rpartition(sep)
                    continue
                newpath = path + sep + name
                if newpath in seen:
                    # Already seen this path
                    path = seen[newpath]
                    if path is not None:
                        # use cached value
                        continue
                    # The symlink is not resolved, so we must have a symlink
                    # loop.
                    raise RuntimeError("Symlink loop from %r" % newpath)
                # Resolve the symbolic link
                try:
                    target = accessor.readlink(newpath)
                except OSError as e:
                    if e.errno != EINVAL:
                        raise
                    # Not a symlink
                    path = newpath
                else:
                    seen[newpath] = None  # not resolved symlink
                    path = _resolve(path, target)
                    seen[newpath] = path  # resolved symlink

            return path
        # NOTE: according to POSIX, getcwd() cannot contain path components
        # which are symlinks.
        base = '' if path.is_absolute() else os.getcwd()
        return _resolve(base, str(path)) or sep

    def is_reserved(self, parts):
        return False

    def make_uri(self, path):
        # We represent the path using the local filesystem encoding,
        # for portability to other applications.
        bpath = bytes(path)
        return 'file://' + urlquote_from_bytes(bpath)

    def gethomedir(self, username):
        if not username:
            try:
                return os.environ['HOME']
            except KeyError:
                import pwd
                return pwd.getpwuid(os.getuid()).pw_dir
        else:
            import pwd
            try:
                return pwd.getpwnam(username).pw_dir
            except KeyError:
                raise RuntimeError("Can't determine home directory "
                                   "for %r" % username)

_windows_flavour = _WindowsFlavour()
_posix_flavour = _PosixFlavour()


class _Accessor:

    """An accessor implements a particular (system-specific or not) way of
    accessing paths on the filesystem."""


class _NormalAccessor(_Accessor):

    def _wrap_strfunc(strfunc):
        @functools.wraps(strfunc)
        def wrapped(pathobj, *args):
            return strfunc(str(pathobj), *args)
        return staticmethod(wrapped)

    def _wrap_binary_strfunc(strfunc):
        @functools.wraps(strfunc)
        def wrapped(pathobjA, pathobjB, *args):
            return strfunc(str(pathobjA), str(pathobjB), *args)
        return staticmethod(wrapped)

    stat = _wrap_strfunc(os.stat)

    lstat = _wrap_strfunc(os.lstat)

    open = _wrap_strfunc(os.open)

    listdir = _wrap_strfunc(os.listdir)

    chmod = _wrap_strfunc(os.chmod)

    if hasattr(os, "lchmod"):
        lchmod = _wrap_strfunc(os.lchmod)
    else:
        def lchmod(self, pathobj, mode):
            raise NotImplementedError("lchmod() not available on this system")

    mkdir = _wrap_strfunc(os.mkdir)

    unlink = _wrap_strfunc(os.unlink)

    rmdir = _wrap_strfunc(os.rmdir)

    rename = _wrap_binary_strfunc(os.rename)

    if sys.version_info >= (3, 3):
        replace = _wrap_binary_strfunc(os.replace)

    if nt:
        if supports_symlinks:
            symlink = _wrap_binary_strfunc(os.symlink)
        else:
            def symlink(a, b, target_is_directory):
                raise NotImplementedError(
                    "symlink() not available on this system")
    else:
        # Under POSIX, os.symlink() takes two args
        @staticmethod
        def symlink(a, b, target_is_directory):
            return os.symlink(str(a), str(b))

    utime = _wrap_strfunc(os.utime)

    # Helper for resolve()
    def readlink(self, path):
        return os.readlink(path)


_normal_accessor = _NormalAccessor()


#
# Globbing helpers
#

@contextmanager
def _cached(func):
    try:
        func.__cached__
        yield func
    except AttributeError:
        cache = {}

        def wrapper(*args):
            try:
                return cache[args]
            except KeyError:
                value = cache[args] = func(*args)
                return value
        wrapper.__cached__ = True
        try:
            yield wrapper
        finally:
            cache.clear()


def _make_selector(pattern_parts):
    pat = pattern_parts[0]
    child_parts = pattern_parts[1:]
    if pat == '**':
        cls = _RecursiveWildcardSelector
    elif '**' in pat:
        raise ValueError(
            "Invalid pattern: '**' can only be an entire path component")
    elif _is_wildcard_pattern(pat):
        cls = _WildcardSelector
    else:
        cls = _PreciseSelector
    return cls(pat, child_parts)

if hasattr(functools, "lru_cache"):
    _make_selector = functools.lru_cache()(_make_selector)


class _Selector:

    """A selector matches a specific glob pattern part against the children
    of a given path."""

    def __init__(self, child_parts):
        self.child_parts = child_parts
        if child_parts:
            self.successor = _make_selector(child_parts)
        else:
            self.successor = _TerminatingSelector()

    def select_from(self, parent_path):
        """Iterate over all child paths of `parent_path` matched by this
        selector.  This can contain parent_path itself."""
        path_cls = type(parent_path)
        is_dir = path_cls.is_dir
        exists = path_cls.exists
        listdir = parent_path._accessor.listdir
        return self._select_from(parent_path, is_dir, exists, listdir)


class _TerminatingSelector:

    def _select_from(self, parent_path, is_dir, exists, listdir):
        yield parent_path


class _PreciseSelector(_Selector):

    def __init__(self, name, child_parts):
        self.name = name
        _Selector.__init__(self, child_parts)

    def _select_from(self, parent_path, is_dir, exists, listdir):
        if not is_dir(parent_path):
            return
        path = parent_path._make_child_relpath(self.name)
        if exists(path):
            for p in self.successor._select_from(
                    path, is_dir, exists, listdir):
                yield p


class _WildcardSelector(_Selector):

    def __init__(self, pat, child_parts):
        self.pat = re.compile(fnmatch.translate(pat))
        _Selector.__init__(self, child_parts)

    def _select_from(self, parent_path, is_dir, exists, listdir):
        if not is_dir(parent_path):
            return
        cf = parent_path._flavour.casefold
        for name in listdir(parent_path):
            casefolded = cf(name)
            if self.pat.match(casefolded):
                path = parent_path._make_child_relpath(name)
                for p in self.successor._select_from(
                        path, is_dir, exists, listdir):
                    yield p


class _RecursiveWildcardSelector(_Selector):

    def __init__(self, pat, child_parts):
        _Selector.__init__(self, child_parts)

    def _iterate_directories(self, parent_path, is_dir, listdir):
        yield parent_path
        for name in listdir(parent_path):
            path = parent_path._make_child_relpath(name)
            if is_dir(path):
                for p in self._iterate_directories(path, is_dir, listdir):
                    yield p

    def _select_from(self, parent_path, is_dir, exists, listdir):
        if not is_dir(parent_path):
            return
        with _cached(listdir) as listdir:
            yielded = set()
            try:
                successor_select = self.successor._select_from
                for starting_point in self._iterate_directories(
                        parent_path, is_dir, listdir):
                    for p in successor_select(
                            starting_point, is_dir, exists, listdir):
                        if p not in yielded:
                            yield p
                            yielded.add(p)
            finally:
                yielded.clear()


#
# Public API
#

class _PathParents(Sequence):

    """This object provides sequence-like access to the logical ancestors
    of a path.  Don't try to construct it yourself."""
    __slots__ = ('_pathcls', '_drv', '_root', '_parts')

    def __init__(self, path):
        # We don't store the instance to avoid reference cycles
        self._pathcls = type(path)
        self._drv = path._drv
        self._root = path._root
        self._parts = path._parts

    def __len__(self):
        if self._drv or self._root:
            return len(self._parts) - 1
        else:
            return len(self._parts)

    def __getitem__(self, idx):
        if idx < 0 or idx >= len(self):
            raise IndexError(idx)
        return self._pathcls._from_parsed_parts(self._drv, self._root,
                                                self._parts[:-idx - 1])

    def __repr__(self):
        return "<{0}.parents>".format(self._pathcls.__name__)


class PurePath(object):

    """PurePath represents a filesystem path and offers operations which
    don't imply any actual filesystem I/O.  Depending on your system,
    instantiating a PurePath will return either a PurePosixPath or a
    PureWindowsPath object.  You can also instantiate either of these classes
    directly, regardless of your system.
    """
    __slots__ = (
        '_drv', '_root', '_parts',
        '_str', '_hash', '_pparts', '_cached_cparts',
        '_stat', # <--- PLEASE ADD THIS!
    )

    def __new__(cls, *args):
        """Construct a PurePath from one or several strings and or existing
        PurePath objects.  The strings and path objects are combined so as
        to yield a canonicalized path, which is incorporated into the
        new PurePath object.
        """
        if cls is PurePath:
            cls = PureWindowsPath if os.name == 'nt' else PurePosixPath
        return cls._from_parts(args)

    def __reduce__(self):
        # Using the parts tuple helps share interned path parts
        # when pickling related paths.
        return (self.__class__, tuple(self._parts))

    @classmethod
    def _parse_args(cls, args):
        # This is useful when you don't want to create an instance, just
        # canonicalize some constructor arguments.
        parts = []
        for a in args:
            if isinstance(a, PurePath):
                parts += a._parts
            elif isinstance(a, basestring):
                # Force-cast str subclasses to str (issue #21127)
                parts.append(str(a))
            else:
                raise TypeError(
                    "argument should be a path or str object, not %r"
                    % type(a))
        return cls._flavour.parse_parts(parts)

    @classmethod
    def _from_parts(cls, args, init=True):
        # We need to call _parse_args on the instance, so as to get the
        # right flavour.
        self = object.__new__(cls)
        drv, root, parts = self._parse_args(args)
        self._drv = drv
        self._root = root
        self._parts = parts
        if init:
            self._init()
        return self

    @classmethod
    def _from_parsed_parts(cls, drv, root, parts, init=True):
        self = object.__new__(cls)
        self._drv = drv
        self._root = root
        self._parts = parts
        if init:
            self._init()
        return self

    @classmethod
    def _format_parsed_parts(cls, drv, root, parts):
        if drv or root:
            return drv + root + cls._flavour.join(parts[1:])
        else:
            return cls._flavour.join(parts)

    def _init(self):
        # Overriden in concrete Path
        pass

    def _make_child(self, args):
        drv, root, parts = self._parse_args(args)
        drv, root, parts = self._flavour.join_parsed_parts(
            self._drv, self._root, self._parts, drv, root, parts)
        return self._from_parsed_parts(drv, root, parts)

    def __str__(self):
        """Return the string representation of the path, suitable for
        passing to system calls."""
        try:
            return self._str
        except AttributeError:
            self._str = self._format_parsed_parts(self._drv, self._root,
                                                  self._parts) or '.'
            return self._str

    def as_posix(self):
        """Return the string representation of the path with forward (/)
        slashes."""
        f = self._flavour
        return str(self).replace(f.sep, '/')

    def __bytes__(self):
        """Return the bytes representation of the path.  This is only
        recommended to use under Unix."""
        if sys.version_info < (3, 2):
            raise NotImplementedError("needs Python 3.2 or later")
        return os.fsencode(str(self))

    def __repr__(self):
        return "{0}({1!r})".format(self.__class__.__name__, self.as_posix())

    def as_uri(self):
        """Return the path as a 'file' URI."""
        if not self.is_absolute():
            raise ValueError("relative path can't be expressed as a file URI")
        return self._flavour.make_uri(self)

    @property
    def _cparts(self):
        # Cached casefolded parts, for hashing and comparison
        try:
            return self._cached_cparts
        except AttributeError:
            self._cached_cparts = self._flavour.casefold_parts(self._parts)
            return self._cached_cparts

    def __eq__(self, other):
        if not isinstance(other, PurePath):
            return NotImplemented
        return (
            self._cparts == other._cparts
            and self._flavour is other._flavour)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(tuple(self._cparts))
            return self._hash

    def __lt__(self, other):
        if (not isinstance(other, PurePath)
                or self._flavour is not other._flavour):
            return NotImplemented
        return self._cparts < other._cparts

    def __le__(self, other):
        if (not isinstance(other, PurePath)
                or self._flavour is not other._flavour):
            return NotImplemented
        return self._cparts <= other._cparts

    def __gt__(self, other):
        if (not isinstance(other, PurePath)
                or self._flavour is not other._flavour):
            return NotImplemented
        return self._cparts > other._cparts

    def __ge__(self, other):
        if (not isinstance(other, PurePath)
                or self._flavour is not other._flavour):
            return NotImplemented
        return self._cparts >= other._cparts

    drive = property(attrgetter('_drv'),
                     doc="""The drive prefix (letter or UNC path), if any.""")

    root = property(attrgetter('_root'),
                    doc="""The root of the path, if any.""")

    @property
    def anchor(self):
        """The concatenation of the drive and root, or ''."""
        anchor = self._drv + self._root
        return anchor

    @property
    def name(self):
        """The final path component, if any."""
        parts = self._parts
        if len(parts) == (1 if (self._drv or self._root) else 0):
            return ''
        return parts[-1]

    @property
    def suffix(self):
        """The final component's last suffix, if any."""
        name = self.name
        i = name.rfind('.')
        if 0 < i < len(name) - 1:
            return name[i:]
        else:
            return ''

    @property
    def suffixes(self):
        """A list of the final component's suffixes, if any."""
        name = self.name
        if name.endswith('.'):
            return []
        name = name.lstrip('.')
        return ['.' + suffix for suffix in name.split('.')[1:]]

    @property
    def stem(self):
        """The final path component, minus its last suffix."""
        name = self.name
        i = name.rfind('.')
        if 0 < i < len(name) - 1:
            return name[:i]
        else:
            return name

    def with_name(self, name):
        """Return a new path with the file name changed."""
        if not self.name:
            raise ValueError("%r has an empty name" % (self,))
        drv, root, parts = self._flavour.parse_parts((name,))
        if (not name or name[-1] in [self._flavour.sep, self._flavour.altsep]
                or drv or root or len(parts) != 1):
            raise ValueError("Invalid name %r" % (name))
        return self._from_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    def with_suffix(self, suffix):
        """Return a new path with the file suffix changed (or added, if
        none).
        """
        # XXX if suffix is None, should the current suffix be removed?
        f = self._flavour
        if f.sep in suffix or f.altsep and f.altsep in suffix:
            raise ValueError("Invalid suffix %r" % (suffix))
        if suffix and not suffix.startswith('.') or suffix == '.':
            raise ValueError("Invalid suffix %r" % (suffix))
        name = self.name
        if not name:
            raise ValueError("%r has an empty name" % (self,))
        old_suffix = self.suffix
        if not old_suffix:
            name = name + suffix
        else:
            name = name[:-len(old_suffix)] + suffix
        return self._from_parsed_parts(self._drv, self._root,
                                       self._parts[:-1] + [name])

    def relative_to(self, *other):
        """Return the relative path to another path identified by the passed
        arguments.  If the operation is not possible (because this is not
        a subpath of the other path), raise ValueError.
        """
        # For the purpose of this method, drive and root are considered
        # separate parts, i.e.:
        #   Path('c:/').relative_to('c:')  gives Path('/')
        #   Path('c:/').relative_to('/')   raise ValueError
        if not other:
            raise TypeError("need at least one argument")
        parts = self._parts
        drv = self._drv
        root = self._root
        if root:
            abs_parts = [drv, root] + parts[1:]
        else:
            abs_parts = parts
        to_drv, to_root, to_parts = self._parse_args(other)
        if to_root:
            to_abs_parts = [to_drv, to_root] + to_parts[1:]
        else:
            to_abs_parts = to_parts
        n = len(to_abs_parts)
        cf = self._flavour.casefold_parts
        if (root or drv) if n == 0 else cf(abs_parts[:n]) != cf(to_abs_parts):
            formatted = self._format_parsed_parts(to_drv, to_root, to_parts)
            raise ValueError("{!r} does not start with {!r}"
                             .format(str(self), str(formatted)))
        return self._from_parsed_parts('', root if n == 1 else '',
                                       abs_parts[n:])

    @property
    def parts(self):
        """An object providing sequence-like access to the
        components in the filesystem path."""
        # We cache the tuple to avoid building a new one each time .parts
        # is accessed.  XXX is this necessary?
        try:
            return self._pparts
        except AttributeError:
            self._pparts = tuple(self._parts)
            return self._pparts

    def joinpath(self, *args):
        """Combine this path with one or several arguments, and return a
        new path representing either a subpath (if all arguments are relative
        paths) or a totally different path (if one of the arguments is
        anchored).
        """
        return self._make_child(args)

    def __truediv__(self, key):
        return self._make_child((key,))

    def __rtruediv__(self, key):
        return self._from_parts([key] + self._parts)

    if six.PY2:
        __div__ = __truediv__
        __rdiv__ = __rtruediv__

    @property
    def parent(self):
        """The logical parent of the path."""
        drv = self._drv
        root = self._root
        parts = self._parts
        if len(parts) == 1 and (drv or root):
            return self
        return self._from_parsed_parts(drv, root, parts[:-1])

    @property
    def parents(self):
        """A sequence of this path's logical parents."""
        return _PathParents(self)

    def is_absolute(self):
        """True if the path is absolute (has both a root and, if applicable,
        a drive)."""
        if not self._root:
            return False
        return not self._flavour.has_drv or bool(self._drv)

    def is_reserved(self):
        """Return True if the path contains one of the special names reserved
        by the system, if any."""
        return self._flavour.is_reserved(self._parts)

    def match(self, path_pattern):
        """
        Return True if this path matches the given pattern.
        """
        cf = self._flavour.casefold
        path_pattern = cf(path_pattern)
        drv, root, pat_parts = self._flavour.parse_parts((path_pattern,))
        if not pat_parts:
            raise ValueError("empty pattern")
        if drv and drv != cf(self._drv):
            return False
        if root and root != cf(self._root):
            return False
        parts = self._cparts
        if drv or root:
            if len(pat_parts) != len(parts):
                return False
            pat_parts = pat_parts[1:]
        elif len(pat_parts) > len(parts):
            return False
        for part, pat in zip(reversed(parts), reversed(pat_parts)):
            if not fnmatch.fnmatchcase(part, pat):
                return False
        return True


class PurePosixPath(PurePath):
    _flavour = _posix_flavour
    __slots__ = ()


class PureWindowsPath(PurePath):
    _flavour = _windows_flavour
    __slots__ = ()


# Filesystem-accessing classes


class Path(PurePath):
    """Path represent a virtual/real path in your file system.
    """
    __slots__ = (
        '_accessor',
        '_closed',
    )

    def __new__(cls, *args, **kwargs):
        if cls is Path:
            cls = WindowsPath if os.name == 'nt' else PosixPath
        self = cls._from_parts(args, init=False)
        if not self._flavour.is_supported:
            raise NotImplementedError("cannot instantiate %r on your system"
                                      % (cls.__name__,))
        self._init()
        return self

    def _init(self,
              # Private non-constructor arguments
              template=None,
              ):
        self._closed = False
        if template is not None:
            self._accessor = template._accessor
        else:
            self._accessor = _normal_accessor

    def _make_child_relpath(self, part):
        # This is an optimization used for dir walking.  `part` must be
        # a single part relative to this path.
        parts = self._parts + [part]
        return self._from_parsed_parts(self._drv, self._root, parts)

    def __enter__(self):
        if self._closed:
            self._raise_closed()
        return self

    def __exit__(self, t, v, tb):
        self._closed = True

    def _raise_closed(self):
        raise ValueError("I/O operation on closed path")

    def _opener(self, name, flags, mode=0o666):
        # A stub for the opener argument to built-in open()
        return self._accessor.open(self, flags, mode)

    def _raw_open(self, flags, mode=0o777):
        """
        Open the file pointed by this path and return a file descriptor,
        as os.open() does.
        """
        if self._closed:
            self._raise_closed()
        return self._accessor.open(self, flags, mode)

    # Public API

    @classmethod
    def cwd(cls):
        """Return a new path pointing to the current working directory
        (as returned by os.getcwd()).
        """
        return cls(os.getcwd())

    @classmethod
    def home(cls):
        """Return a new path pointing to the user's home directory (as
        returned by os.path.expanduser('~')).
        """
        return cls(cls()._flavour.gethomedir(None))

    def samefile(self, other_path):
        """Return whether `other_file` is the same or not as this file.
        (as returned by os.path.samefile(file, other_file)).
        """
        if hasattr(os.path, "samestat"):
            st = self.stat()
            try:
                other_st = other_path.stat()
            except AttributeError:
                other_st = os.stat(other_path)
            return os.path.samestat(st, other_st)
        else:
            filename1 = six.text_type(self)
            filename2 = six.text_type(other_path)
            st1 = _win32_get_unique_path_id(filename1)
            st2 = _win32_get_unique_path_id(filename2)
            return st1 == st2

    def iterdir(self):
        """Iterate over the files in this directory.  Does not yield any
        result for the special paths '.' and '..'.
        """
        if self._closed:
            self._raise_closed()
        for name in self._accessor.listdir(self):
            if name in ('.', '..'):
                # Yielding a path object for these makes little sense
                continue
            yield self._make_child_relpath(name)
            if self._closed:
                self._raise_closed()

    def glob(self, pattern):
        """Iterate over this subtree and yield all existing files (of any
        kind, including directories) matching the given pattern.
        """
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        if drv or root:
            raise NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(tuple(pattern_parts))
        for p in selector.select_from(self):
            yield p

    def rglob(self, pattern):
        """Recursively yield all existing files (of any kind, including
        directories) matching the given pattern, anywhere in this subtree.
        """
        pattern = self._flavour.casefold(pattern)
        drv, root, pattern_parts = self._flavour.parse_parts((pattern,))
        if drv or root:
            raise NotImplementedError("Non-relative patterns are unsupported")
        selector = _make_selector(("**",) + tuple(pattern_parts))
        for p in selector.select_from(self):
            yield p

    def absolute(self):
        """Return an absolute version of this path.  This function works
        even if the path doesn't point to anything.

        No normalization is done, i.e. all '.' and '..' will be kept along.
        Use resolve() to get the canonical path to a file.
        """
        # XXX untested yet!
        if self._closed:
            self._raise_closed()
        if self.is_absolute():
            return self
        # FIXME this must defer to the specific flavour (and, under Windows,
        # use nt._getfullpathname())
        obj = self._from_parts([os.getcwd()] + self._parts, init=False)
        obj._init(template=self)
        return obj

    def resolve(self):
        """
        Make the path absolute, resolving all symlinks on the way and also
        normalizing it (for example turning slashes into backslashes under
        Windows).
        """
        if self._closed:
            self._raise_closed()
        s = self._flavour.resolve(self)
        if s is None:
            # No symlink resolution => for consistency, raise an error if
            # the path doesn't exist or is forbidden
            self.stat()
            s = str(self.absolute())
        # Now we have no symlinks in the path, it's safe to normalize it.
        normed = self._flavour.pathmod.normpath(s)
        obj = self._from_parts((normed,), init=False)
        obj._init(template=self)
        return obj

    def stat(self):
        """
        Return the result of the stat() system call on this path, like
        os.stat() does.
        """
        return self._accessor.stat(self)

    def owner(self):
        """
        Return the login name of the file owner.
        """
        import pwd
        return pwd.getpwuid(self.stat().st_uid).pw_name

    def group(self):
        """
        Return the group name of the file gid.
        """
        import grp
        return grp.getgrgid(self.stat().st_gid).gr_name

    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        if self._closed:
            self._raise_closed()
        if sys.version_info >= (3, 3):
            return io.open(
                str(self), mode, buffering, encoding, errors, newline,
                opener=self._opener)
        else:
            return io.open(str(self), mode, buffering,
                           encoding, errors, newline)

    def read_bytes(self):
        """
        Open the file in bytes mode, read it, and close the file.
        """
        with self.open(mode='rb') as f:
            return f.read()

    def read_text(self, encoding=None, errors=None):
        """
        Open the file in text mode, read it, and close the file.
        """
        with self.open(mode='r', encoding=encoding, errors=errors) as f:
            return f.read()

    def write_bytes(self, data):
        """
        Open the file in bytes mode, write to it, and close the file.
        """
        if not isinstance(data, six.binary_type):
            raise TypeError(
                'data must be %s, not %s' %
                (six.binary_type.__class__.__name__, data.__class__.__name__))
        with self.open(mode='wb') as f:
            return f.write(data)

    def write_text(self, data, encoding=None, errors=None):
        """
        Open the file in text mode, write to it, and close the file.
        """
        if not isinstance(data, six.text_type):
            raise TypeError(
                'data must be %s, not %s' %
                (six.text_type.__class__.__name__, data.__class__.__name__))
        with self.open(mode='w', encoding=encoding, errors=errors) as f:
            return f.write(data)

    def touch(self, mode=0o666, exist_ok=True):
        """
        Create this file with the given access mode, if it doesn't exist.
        """
        if self._closed:
            self._raise_closed()
        if exist_ok:
            # First try to bump modification time
            # Implementation note: GNU touch uses the UTIME_NOW option of
            # the utimensat() / futimens() functions.
            try:
                self._accessor.utime(self, None)
            except OSError:
                # Avoid exception chaining
                pass
            else:
                return
        flags = os.O_CREAT | os.O_WRONLY
        if not exist_ok:
            flags |= os.O_EXCL
        fd = self._raw_open(flags, mode)
        os.close(fd)

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):

        def helper(exc):
            if not exist_ok or not self.is_dir():
                raise exc

        if self._closed:
            self._raise_closed()
        if not parents:
            _try_except_fileexistserror(
                lambda: self._accessor.mkdir(self, mode),
                helper)
        else:
            try:
                _try_except_fileexistserror(
                    lambda: self._accessor.mkdir(self, mode),
                    helper)
            except OSError as e:
                if e.errno != ENOENT:
                    raise
                self.parent.mkdir(parents=True)
                self._accessor.mkdir(self, mode)

    def chmod(self, mode):
        """
        Change the permissions of the path, like os.chmod().
        """
        if self._closed:
            self._raise_closed()
        self._accessor.chmod(self, mode)

    def lchmod(self, mode):
        """
        Like chmod(), except if the path points to a symlink, the symlink's
        permissions are changed, rather than its target's.
        """
        if self._closed:
            self._raise_closed()
        self._accessor.lchmod(self, mode)

    def unlink(self):
        """
        Remove this file or link.
        If the path is a directory, use rmdir() instead.
        """
        if self._closed:
            self._raise_closed()
        self._accessor.unlink(self)

    def rmdir(self):
        """
        Remove this directory.  The directory must be empty.
        """
        if self._closed:
            self._raise_closed()
        self._accessor.rmdir(self)

    def lstat(self):
        """
        Like stat(), except if the path points to a symlink, the symlink's
        status information is returned, rather than its target's.
        """
        if self._closed:
            self._raise_closed()
        return self._accessor.lstat(self)

    def rename(self, target):
        """
        Rename this path to the given path.
        """
        if self._closed:
            self._raise_closed()
        self._accessor.rename(self, target)

    def replace(self, target):
        """
        Rename this path to the given path, clobbering the existing
        destination if it exists.
        """
        if sys.version_info < (3, 3):
            raise NotImplementedError("replace() is only available "
                                      "with Python 3.3 and later")
        if self._closed:
            self._raise_closed()
        self._accessor.replace(self, target)

    def symlink_to(self, target, target_is_directory=False):
        """
        Make this path a symlink pointing to the given path.
        Note the order of arguments (self, target) is the reverse of
        os.symlink's.
        """
        if self._closed:
            self._raise_closed()
        self._accessor.symlink(target, self, target_is_directory)

    # Convenience functions for querying the stat results

    def exists(self):
        """
        Whether this path exists.
        """
        try:
            self.stat()
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            return False
        return True

    def is_dir(self):
        """
        Whether this path is a directory.
        """
        try:
            return S_ISDIR(self.stat().st_mode)
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            return False

    def is_file(self):
        """
        Whether this path is a regular file (also True for symlinks pointing
        to regular files).
        """
        try:
            return S_ISREG(self.stat().st_mode)
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            return False

    def is_symlink(self):
        """
        Whether this path is a symbolic link.
        """
        try:
            return S_ISLNK(self.lstat().st_mode)
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            # Path doesn't exist
            return False

    def is_block_device(self):
        """
        Whether this path is a block device.
        """
        try:
            return S_ISBLK(self.stat().st_mode)
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            return False

    def is_char_device(self):
        """
        Whether this path is a character device.
        """
        try:
            return S_ISCHR(self.stat().st_mode)
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            return False

    def is_fifo(self):
        """
        Whether this path is a FIFO.
        """
        try:
            return S_ISFIFO(self.stat().st_mode)
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            return False

    def is_socket(self):
        """
        Whether this path is a socket.
        """
        try:
            return S_ISSOCK(self.stat().st_mode)
        except OSError as e:
            if e.errno not in (ENOENT, ENOTDIR):
                raise
            # Path doesn't exist or is a broken symlink
            # (see https://bitbucket.org/pitrou/pathlib/issue/12/)
            return False

    def expanduser(self):
        """ Return a new path with expanded ~ and ~user constructs
        (as returned by os.path.expanduser)
        """
        if (not (self._drv or self._root)
                and self._parts and self._parts[0][:1] == '~'):
            homedir = self._flavour.gethomedir(self._parts[0][1:])
            return self._from_parts([homedir] + self._parts[1:])

        return self

    #--- pathlib_mate ---
    @property
    def abspath(self):
        """Absolute path.
        """
        return self.absolute().__str__()

    @property
    def dirpath(self):
        """Parent dir full absolute path.
        """
        return self.parent.abspath

    @property
    def dirname(self):
        """Parent dir name.
        """
        return self.parent.name

    @property
    def basename(self):
        """File name with extension, path is not included.
        """
        return self.name

    @property
    def fname(self):
        """File name without extension.
        """
        return self.stem

    @property
    def ext(self):
        """File extension. If it's a dir, then return empty str.
        """
        return self.suffix

    def get_partial_md5(self, nbytes=0):
        """Return md5 check sum of first n bytes of this file.
        """
        return md5file(self.abspath, nbytes)

    @property
    def md5(self):
        """Return md5 check sum of this file.
        """
        return md5file(self.abspath)

    @property
    def size(self):
        """File size in bytes.
        """
        try:
            return self._stat.st_size
        except:
            self._stat = self.stat()
            return self.size

    @property
    def dirsize(self):
        """Return total file size (include sub folder).
        """
        total = 0
        for p in self.select_file(recursive=True):
            try:
                total += p.size
            except:
                print("Unable to get file size of: %s" % p)
        return total

    @property
    def size_in_text(self):
        """File size as human readable string.
        """
        return repr_data_size(self.size, precision=2)

    @property
    def mtime(self):
        """Get most recent modify time in timestamp.
        """
        try:
            return self._stat.st_mtime
        except:
            self._stat = self.stat()
            return self.mtime

    @property
    def atime(self):
        """Get most recent access time in timestamp.
        """
        try:
            return self._stat.st_atime
        except:
            self._stat = self.stat()
            return self.atime

    @property
    def ctime(self):
        """Get most recent create time in timestamp.
        """
        try:
            return self._stat.st_ctime
        except:
            self._stat = self.stat()
            return self.ctime

    @property
    def modify_datetime(self):
        """Get most recent modify time in datetime.
        """
        return datetime.fromtimestamp(self.mtime)

    @property
    def access_datetime(self):
        """Get most recent access time in datetime.
        """
        return datetime.fromtimestamp(self.atime)

    @property
    def create_datetime(self):
        """Get most recent create time in datetime.
        """
        return datetime.fromtimestamp(self.ctime)

    def change(self,
               new_abspath=None,
               new_dirpath=None, new_dirname=None,
               new_fname=None,
               new_ext=None):
        """Return a new :class:`Path` object with updated information.
        """
        if new_abspath is not None:
            p = Path(new_abspath)
            return p

        if (new_dirpath is None) and (new_dirname is not None):
            new_dirpath = os.path.join(self.parent.dirpath, new_dirname)

        elif (new_dirpath is not None) and (new_dirname is None):
            new_dirpath = new_dirpath

        elif (new_dirpath is None) and (new_dirname is None):
            new_dirpath = self.dirpath

        elif (new_dirpath is not None) and (new_dirname is not None):
            raise ValueError("Cannot having both new_dirpath and new_dirname!")

        if new_fname is None:
            new_fname = self.fname

        if new_ext is None:
            new_ext = self.ext

        return Path(new_dirpath, new_fname + new_ext)

    def moveto(self,
               new_abspath=None,
               new_dirpath=None, new_dirname=None,
               new_fname=None,
               new_ext=None,
               overwrite=False):
        """An advanced ``Path.rename`` method provide ability to rename by parts of
        a path. A new ``Path`` instance will returns.

        **中文文档**

        高级重命名函数, 允许用于根据路径的各个组成部分进行重命名。
        """
        p = self.change(new_abspath, new_dirpath, new_dirname, new_fname, new_ext)

        if p.exists():
            if self.abspath == p.abspath:
                pass
            else:
                if overwrite:
                    self.rename(p)
                else:
                    raise EnvironmentError("'%s' exists!" % p.abspath)
        else:
            self.rename(p)

        return p

    def copyto(self,
               new_abspath=None,
               new_dirpath=None, new_dirname=None,
               new_fname=None,
               new_ext=None,
               overwrite=False):
        """Copy this file to other place.
        """
        p = self.change(new_abspath, new_dirpath, new_dirname, new_fname, new_ext)

        if self.abspath == p.abspath:
            return p

        if not self.exists():
            raise EnvironmentError("'%s' not exists!" % self.abspath)
        
        if p.exists():
            if not overwrite:
                raise EnvironmentError("'%s' exists!" % p.abspath)
            else:
                shutil.copy(self.abspath, p.abspath)
        else:
            shutil.copy(self.abspath, p.abspath)

        return p

    remove = unlink

    #--- select ---
    all_true = lambda x: True

    def select(self, filters=all_true, recursive=True):
        """Select path by criterion.

        :param filters: a lambda function that take a `pathlib.Path` as input,
          boolean as a output.
        :param recursive: include files in subfolder or not.

        **中文文档**

        根据filters中定义的条件选择路径。
        """
        if not self.is_dir():
            raise TypeError("%s is not a directory!" % self)

        if recursive:
            for p in self.glob("**/*"):
                if filters(p):
                    yield p
        else:
            for p in self.iterdir():
                if filters(p):
                    yield p

    def select_file(self, filters=all_true, recursive=True):
        """Select file path by criterion.

        **中文文档**

        根据filters中定义的条件选择文件。
        """
        for p in self.select(filters, recursive):
            if p.is_file():
                yield p

    def select_dir(self, filters=all_true, recursive=True):
        """Select dir path by criterion.

        **中文文档**

        根据filters中定义的条件选择文件夹。
        """
        for p in self.select(filters, recursive):
            if p.is_dir():
                yield p

    #--- Select by built-in criterion ---
    def select_by_ext(self, ext, recursive=True):
        """Select file path by extension.

        :param ext:

        **中文文档**

        选择与预定义的若干个扩展名匹配的文件。
        """
        ext = [ext.strip().lower() for ext in _preprocess(ext)]
        filters = lambda p: p.suffix.lower() in ext
        return self.select_file(filters, recursive)

    def select_by_pattern_in_fname(self, pattern, recursive=True, case_sensitive=False):
        """Select file path by text pattern in file name.


        **中文文档**

        选择文件名中包含指定子字符串的文件。
        """
        if case_sensitive:
            pattern = pattern.lower()
            filters = lambda p: pattern in p.fname.lower()
        else:
            filters = lambda p: pattern in p.fname

        return self.select_file(filters, recursive)

    def select_by_pattern_in_abspath(self, pattern, recursive=True, case_sensitive=False):
        """Select file path by text pattern in absolute path.

        **中文文档**

        选择绝对路径中包含指定子字符串的文件。
        """
        if case_sensitive:
            pattern = pattern.lower()
            filters = lambda p: pattern in p.abspath.lower()
        else:
            filters = lambda p: pattern in p.abspath

        return self.select_file(filters, recursive)

    def select_by_size(self, min_size=0, max_size=1 << 40, recursive=True):
        """Select file path by size.

        **中文文档**

        选择所有文件大小在一定范围内的文件。
        """
        filters = lambda p: min_size <= p.size <= max_size
        return self.select_file(filters, recursive)

    def select_by_mtime(self, min_time=0, max_time=4102462800.0, recursive=True):
        """Select file path by modify time.

        :param min_time: lower bound timestamp
        :param max_time: upper bound timestamp

        **中文文档**

        选择所有mtime在一定范围内的文件。
        """
        filters = lambda p: min_time <= p.mtime <= max_time
        return self.select_file(filters, recursive)

    def select_by_atime(self, min_time=0, max_time=4102462800.0, recursive=True):
        """Select file path by access time.

        :param min_time: lower bound timestamp
        :param max_time: upper bound timestamp

        **中文文档**

        选择所有atime在一定范围内的文件。
        """
        filters = lambda p: min_time <= p.atime <= max_time
        return self.select_file(filters, recursive)

    def select_by_ctime(self, min_time=0, max_time=4102462800.0, recursive=True):
        """Select file path by create time.

        :param min_time: lower bound timestamp
        :param max_time: upper bound timestamp

        **中文文档**

        选择所有ctime在一定范围内的文件。
        """
        filters = lambda p: min_time <= p.ctime <= max_time
        return self.select_file(filters, recursive)

    #--- Select Special File Type ---
    def select_image(self, recursive=True):
        """Select image file.
        """
        ext = [".jpg", ".jpeg", ".png", ".gif", ".tiff",
               ".bmp", ".ppm", ".pgm", ".pbm", ".pnm", ".svg"]
        return self.select_by_ext(ext, recursive)

    def select_audio(self, recursive=True):
        """Select audio file.
        """
        ext = [".mp3", ".mp4", ".aac", ".m4a", ".wma",
               ".wav", ".ape", ".tak", ".tta",
               ".3gp", ".webm", ".ogg", ]
        return self.select_by_ext(ext, recursive)

    def select_video(self, recursive=True):
        """Select video file.
        """
        ext = [".avi", ".wmv", ".mkv", ".mp4", ".flv",
               ".vob", ".mov", ".rm", ".rmvb", "3gp", ".3g2", ".nsv", ".webm",
               ".mpg", ".mpeg", ".m4v", ".iso", ]
        return self.select_by_ext(ext, recursive)

    def select_word(self, recursive=True):
        """Select Microsoft Word file.
        """
        ext = [".doc", ".docx", ".docm", ".dotx", ".dotm", ".docb"]
        return self.select_by_ext(ext, recursive)

    def select_excel(self, recursive=True):
        """Select Microsoft Excel file.
        """
        ext = [".xls", ".xlsx", ".xlsm", ".xltx", ".xltm"]
        return self.select_by_ext(ext, recursive)

    def select_archive(self, recursive=True):
        """Select compressed archive file.
        """
        ext = [".zip", ".rar", ".gz", ".tar.gz", ".tgz", ".7z"]
        return self.select_by_ext(ext, recursive)

    def _sort_by(key):
        """High order function for sort methods.
        """
        @staticmethod
        def sort_by(p_list, reverse=False):
            return sorted(p_list, key=lambda p: getattr(p, key), reverse=reverse)
        return sort_by


    sort_by_abspath = _sort_by("abspath")
    """Sort list of :class:`Path` by absolute path.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    sort_by_fname = _sort_by("fname")
    """Sort list of :class:`Path` by file name.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    sort_by_ext = _sort_by("ext")
    """Sort list of :class:`Path` by extension.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    sort_by_size = _sort_by("size")
    """Sort list of :class:`Path` by file size.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    sort_by_mtime = _sort_by("mtime")
    """Sort list of :class:`Path` by modify time.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    sort_by_atime = _sort_by("atime")
    """Sort list of :class:`Path` by access time.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    sort_by_ctime = _sort_by("ctime")
    """Sort list of :class:`Path` by create time.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    sort_by_md5 = _sort_by("md5")
    """Sort list of :class:`Path` by md5.
    
    :params p_list: list of :class:`Path`
    :params reverse: if False, return in descending order
    """
    
    #--- Recipe ---
    def print_big_dir(self, top_n=5):
        """Print ``top_n`` big dir in this dir.
        """
        if not self.is_dir():
            raise EnvironmentError("'%s' not exists!" % self)
        
        size_table = sorted(
            [(p, p.dirsize) for p in self.select_dir(recursive=False)],
            key=lambda x: x[1],
            reverse=True,
        )
        for p, size in size_table[:top_n]:
            print("{:<9}    {:<9}".format(repr_data_size(size), p.abspath))

    def print_big_file(self, top_n=5):
        """Print ``top_n`` big file in this dir.
        """
        if not self.is_dir():
            raise EnvironmentError("'%s' not exists!" % self)
        
        size_table = sorted(
            [(p, p.size) for p in self.select_file(recursive=True)],
            key=lambda x: x[1],
            reverse=True,
        )
        for p, size in size_table[:top_n]:
            print("{:<9}    {:<9}".format(repr_data_size(size), p.abspath))

    def print_big_dir_and_big_file(self, top_n=5):
        """Print ``top_n`` big dir and ``top_n`` big file in each dir.
        """
        if not self.is_dir():
            raise EnvironmentError("'%s' not exists!" % self)
        
        size_table1 = sorted(
            [(p, p.dirsize) for p in self.select_dir(recursive=False)],
            key=lambda x: x[1],
            reverse=True,
        )
        for p1, size1 in size_table1[:top_n]:
            print("{:<9}    {:<9}".format(repr_data_size(size1), p1.abspath))
            size_table2 = sorted(
                [(p, p.size) for p in p1.select_file(recursive=True)],
                key=lambda x: x[1],
                reverse=True,
            )
            for p2, size2 in size_table2[:top_n]:
                print("    {:<9}    {:<9}".format(repr_data_size(size2), p2.abspath))

    def mirror_to(self, dst):
        src = self.abspath
        dst = os.path.abspath(dst)
        if not self.exists():
            raise Exception("source is not exists!")
        if not self.is_dir():
            raise Exception("source is not a dir!")
        if os.path.exists(dst):
            raise Exception("distination already exist!")

        folder_to_create = list()
        file_to_create = list()

        for current_folder, _, file_list in os.walk(self.abspath):
            current_folder = current_folder.replace(src, dst)
            try:
                os.mkdir(current_folder)
            except:
                pass
            for basename in file_list:
                abspath = os.path.join(current_folder, basename)
                with open(abspath, "wb") as _:
                    pass

    def backup(self, dst=None, 
               ignore=None, 
               ignore_ext=None, 
               ignore_pattern=None,
               ignore_size_smaller_than=None,
               ignore_size_larger_than=None,
               case_sensitive=False):
        """The backup utility method. Basically it just add files that need to be
        backupped to zip archives.
    
        :param filename: the output file name, DO NOT NEED FILE EXTENSION.
        :param root_dir: the directory you want to backup.
        :param ignore: file or directory defined in this list will be ignored.
        :param ignore_ext: file with extensions defined in this list will be ignored.
        :param ignore_pattern: any file or directory that contains this pattern
          will be ignored.
        """
        from zipfile import ZipFile

        def preprocess_arg(arg):
            if arg is None:
                return []
            
            if isinstance(arg, (tuple, list)):
                return list(arg)
            else:
                return [arg, ]
            
        if not (self.is_dir() and self.exists()):
            raise Exception("")
        
        tab = "    "
        
        # Step 0, preprocess input argument
        surfix = " %s.zip" % datetime.now().strftime("%Y-%m-%d %Hh-%Mm-%Ss")
        if dst is None:
            dst = Path(os.getcwd(), self.basename + surfix).abspath
        else:
            dst = str(dst)
            if dst.endswith(".zip") or dst.endswith(".ZIP"):
                dst = dst[:-4]
            dst = Path(Path(dst).abspath + surfix).abspath
        print("Backup '%s' to '%s'..." % (self.abspath, dst))
            
        # Step 1, calculate files to backup
        print(tab + "1. Calculate files...")
        
        ignore = preprocess_arg(ignore)
        for i in ignore:
            if i.startswith("/") or i.startswith("\\"):
                raise ValueError
        
        ignore_ext = preprocess_arg(ignore_ext)
        for ext in ignore_ext:
            if not ext.startswith("."):
                raise ValueError
        
        ignore_pattern = preprocess_arg(ignore_pattern) 
        
        if case_sensitive:
            pass
        else:
            ignore = [i.lower() for i in ignore]
            ignore_ext = [i.lower() for i in ignore_ext]
            ignore_pattern = [i.lower() for i in ignore_pattern]
            
        def filters(p):
            relpath = p.relative_to(self).abspath
            if not case_sensitive:
                relpath = relpath.lower()
            
            # ignore
            for i in ignore:
                if relpath.startswith(i):
                    return False
            
            # ignore_ext
            if case_sensitive:
                ext = p.ext
            else:
                ext = p.ext.lower()
                
            if ext in ignore_ext:
                return False
            
            # ignore_pattern
            for pattern in ignore_pattern:
                if pattern in relpath:
                    return False
            
            # ignore_size_smaller_than
            if ignore_size_smaller_than:
                if p.size < ignore_size_smaller_than:
                    return False
                
            # ignore_size_larger_than
            if ignore_size_larger_than:
                if p.size > ignore_size_larger_than:
                    return False
            
            return True
        
        total_size = 0
        selected = list()
        for p in self.glob("**/*"):
            if filters(p):
                selected.append(p)
                total_size += p.size
        
        print(tab * 2 + "Done, got %s files, total size is %s." % (
            len(selected), repr_data_size(total_size)))
        
        # Step 2, write files to zip archive
        print(tab + "2. Backup files...")
        current_dir = os.getcwd()
        
        with ZipFile(dst, "w") as f:
            os.chdir(self.abspath)
            for p in selected:
                relpath = p.relative_to(self).__str__()
                f.write(relpath)
    
        os.chdir(current_dir)
    
        print(tab * 2 + "Complete!")
    
    
class PosixPath(Path, PurePosixPath):
    __slots__ = ()


class WindowsPath(Path, PureWindowsPath):
    __slots__ = ()


#--- pathlib_mate ---
def _preprocess(path_or_path_list):
    """Preprocess input argument, whether if it is:

    1. abspath
    2. Path instance
    3. string
    4. list or set of any of them

    It returns list of path.

    :return path_or_path_list: always return list of path in string

    **中文文档**

    预处理输入参数。
    """
    if isinstance(path_or_path_list, (list, set)):
        path_or_path_list = [str(path) for path in path_or_path_list]
        return path_or_path_list
    else:
        path_or_path_list = [path_or_path_list,]
        return _preprocess(path_or_path_list)


def repr_data_size(size_in_bytes, precision=2):
    """Return human readable string represent of a file size. Doesn"t support
    size greater than 1EB.

    For example:

    - 100 bytes => 100 B
    - 100,000 bytes => 97.66 KB
    - 100,000,000 bytes => 95.37 MB
    - 100,000,000,000 bytes => 93.13 GB
    - 100,000,000,000,000 bytes => 90.95 TB
    - 100,000,000,000,000,000 bytes => 88.82 PB
    ...

    Magnitude of data::

        1000         kB    kilobyte
        1000 ** 2    MB    megabyte
        1000 ** 3    GB    gigabyte
        1000 ** 4    TB    terabyte
        1000 ** 5    PB    petabyte
        1000 ** 6    EB    exabyte
        1000 ** 7    ZB    zettabyte
        1000 ** 8    YB    yottabyte
    """
    if size_in_bytes < 1024:
        return "%s B" % size_in_bytes

    magnitude_of_data = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    index = 0
    while 1:
        index += 1
        size_in_bytes, mod = divmod(size_in_bytes, 1024)
        if size_in_bytes < 1024:
            break
    template = "{0:.%sf} {1}" % precision
    s = template.format(size_in_bytes + mod/1024.0, magnitude_of_data[index])
    return s


def md5file(abspath, nbytes=0):
    """Return md5 hash value of a piece of a file

    Estimate processing time on:

    :param abspath: the absolute path to the file
    :param nbytes: only has first N bytes of the file. if 0, hash all file

    CPU = i7-4600U 2.10GHz - 2.70GHz, RAM = 8.00 GB
    1 second can process 0.25GB data

    - 0.59G - 2.43 sec
    - 1.3G - 5.68 sec
    - 1.9G - 7.72 sec
    - 2.5G - 10.32 sec
    - 3.9G - 16.0 sec
    """
    m = hashlib.md5()
    with open(abspath, "rb") as f:
        if nbytes:
            data = f.read(nbytes)
            if data:
                m.update(data)
        else:
            while True:
                data = f.read(4 * 1 << 16)  # only use first 4GB data
                if not data:
                    break
                m.update(data)
    return m.hexdigest()