# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import warnings
import inspect

from .compat import *
from .base import FuncDecorator, Decorator


class once(FuncDecorator):
    """run the decorated function only once for the given arguments

    :Example:
        @once
        def func(x):
            print("adding")
            return x + 1
        func(4) # prints "adding"
        func(10) # prints "adding"
        func(4) # returns 5, no print
        func(10) # returns 11, no print
    """
    def decorate(self, f, *once_args, **once_kwargs):
        def wrapped(*args, **kwargs):
            name = String(hash(f))
            if args:
                for a in args:
                    name += String(hash(a))

            if kwargs:
                for k, v in kwargs.items():
                    name += String(hash(k))
                    name += String(hash(v))

            try:
                ret = getattr(self, name)

            except AttributeError:
                ret = f(*args, **kwargs)
                setattr(self, name, ret)

            return ret
        return wrapped


class deprecated(Decorator):
    """Mark function/class as deprecated

    python has to be ran with -W flag to see warnings
    """
    def find_definition(self, o, callback):
        src_line = 0
        src_file = ""

        st = inspect.stack()
        for ft in st:
            lines = "\n".join(ft[4])
            if callback(lines):
                src_file = ft[1]
                src_line = ft[2]
                break

        if not src_file:
            if self.is_function(o):
                if is_py2:
                    c = o.func_code

                else:
                    c = o.__code__


                src_file = c.co_filename
                src_line = c.co_firstlineno + 1

            else:
                src_file = inspect.getsourcefile(o)
                if not src_file:
                    src_file = inspect.getfile(o)
                if not src_file:
                    src_file = "UNKNOWN"

        return src_file, src_line

    def decorate_func(self, func, *deprecated_args, **deprecated_kwargs):
        callback = lambda lines: "@" in lines or "def " in lines
        src_file, src_line = self.find_definition(func, callback)

        def wrapped(*args, **kwargs):
            # https://wiki.python.org/moin/PythonDecoratorLibrary#Generating_Deprecation_Warnings
            # http://stackoverflow.com/questions/2536307/decorators-in-the-python-standard-lib-deprecated-specifically
            warnings.warn_explicit(
                "Deprecated function {}".format(func.__name__),
                category=DeprecationWarning,
                filename=src_file,
                lineno=src_line
            )
            return func(*args, **kwargs)
        return wrapped

    def decorate_class(self, cls, *deprecated_args, **deprecated_kwargs):
        callback = lambda lines: "@" in lines or "class " in lines
        src_file, src_line = self.find_definition(cls, callback)

        warnings.warn_explicit(
            "Deprecated class {}.{}".format(cls.__module__, cls.__name__),
            category=DeprecationWarning,
            filename=src_file,
            lineno=src_line,
        )
        return cls

