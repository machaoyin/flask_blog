# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import sys
import hashlib

try:
    import cPickle as pickle
except ImportError:
    import pickle

# shamelessly ripped from https://github.com/kennethreitz/requests/blob/master/requests/compat.py
# Syntax sugar.
_ver = sys.version_info
is_py2 = _ver[0] == 2
is_py3 = _ver[0] == 3

if is_py2:
    basestring = basestring
    unicode = unicode
    range = xrange # range is now always an iterator

    import Queue as queue
    import thread as _thread
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    # shamelously ripped from six https://github.com/benjaminp/six
    exec("""def reraise(exception_class, e, traceback=None):
        try:
            raise exception_class, e, traceback
        finally:
            traceback = None
    """)

    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
    import Cookie as cookies
    import urlparse
    import __builtin__ as builtins


elif is_py3:
    basestring = (str, bytes)
    unicode = str
    long = int

    import queue
    import _thread
    from io import StringIO
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    from http import cookies
    from urllib import parse as urlparse
    import builtins

    # ripped from six https://github.com/benjaminp/six
    def reraise(exception_class, e, traceback=None):
        """the 3 params correspond to the return value of sys.exc_info()

        https://docs.python.org/3/library/sys.html#sys.exc_info

        :param exception_class: BaseException, the class of the exception to reraise
        :param e: BaseException instance, the actual exception instance
        :param traceback: traceback, the stack trace
        """
        try:
#             if value is None:
#                 value = tp()
            e = exception_class("" if e is None else e)
            if e.__traceback__ is not traceback:
                raise e.with_traceback(traceback)
            raise e
        finally:
            e = None
            traceback = None


Str = unicode if is_py2 else str
Bytes = str if is_py2 else bytes


class ByteString(Bytes):
    """Wrapper around a byte string b"" to make sure we have a byte string that
    will work across python versions and handle the most annoying encoding issues
    automatically

    :Example:
        # python 3
        s = ByteString("foo)
        str(s) # calls __str__ and returns self.unicode()
        unicode(s) # errors out
        bytes(s) # calls __bytes__ and returns ByteString
        # python 2
        s = ByteString("foo)
        str(s) # calls __str__ and returns ByteString
        unicode(s) # calls __unicode__ and returns String
        bytes(s) # calls __str__ and returns ByteString
    """
    def __new__(cls, val=b"", encoding="UTF-8"):
        if isinstance(val, type(None)): return None

        if not isinstance(val, (bytes, bytearray)):
            if is_py2:
                val = unicode(val)
            else:
                val = str(val)
            #val = val.__str__()
            val = bytearray(val, encoding)

        instance = super(ByteString, cls).__new__(cls, val)
        instance.encoding = encoding
        return instance

    def __str__(self):
        return self if is_py2 else self.unicode()

    def unicode(self):
        s = self.decode(self.encoding)
        return String(s)
    __unicode__ = unicode

    def bytes(self):
        return self
    __bytes__ = bytes

    def raw(self):
        """because sometimes you need a vanilla bytes()"""
        return b"" + self

    def md5(self):
        # http://stackoverflow.com/a/5297483/5006
        return hashlib.md5(self).hexdigest()


class String(Str):
    """Wrapper around a unicode string "" to make sure we have a unicode string that
    will work across python versions and handle the most annoying encoding issues
    automatically

    :Example:
        # python 3
        s = String("foo)
        str(s) # calls __str__ and returns String
        unicode(s) # errors out
        bytes(s) # calls __bytes__ and returns ByteString
        # python 2
        s = String("foo)
        str(s) # calls __str__ and returns ByteString
        unicode(s) # calls __unicode__ and returns String
        bytes(s) # calls __str__ and returns ByteString
    """
    def __new__(cls, val="", encoding="UTF-8"):
        if isinstance(val, type(None)): return None

        if not isinstance(val, (Str, int)):
            val = ByteString(val, encoding).unicode()

        instance = super(String, cls).__new__(cls, val)
        instance.encoding = encoding
        return instance

    def __str__(self):
        return self.bytes() if is_py2 else self

    def unicode(self):
        return self
    __unicode__ = unicode

    def bytes(self):
        s = self.encode(self.encoding)
        return ByteString(s)
    __bytes__ = bytes

    def raw(self):
        """because sometimes you need a vanilla str() (or unicode() in py2)"""
        return "" + self

    def md5(self):
        # http://stackoverflow.com/a/5297483/5006
        return hashlib.md5(self.bytes()).hexdigest()

