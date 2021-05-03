# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from .compat import *
from .base import FuncDecorator


class classproperty(property):
    """
    allow a readonly class property to exist on a class with a similar interface
    to the built-in property decorator

    NOTE -- because of Python's architecture, this can only be read only, you can't
        create a setter or deleter

    :Example:
        class Foo(object):
            @classproperty
            def bar(cls):
                return 42
        Foo.bar # 42

    http://stackoverflow.com/questions/128573/using-property-on-classmethods
    http://stackoverflow.com/questions/5189699/how-can-i-make-a-class-property-in-python
    https://stackoverflow.com/a/38810649/5006
    http://docs.python.org/2/reference/datamodel.html#object.__setattr__
    https://stackoverflow.com/a/3203659/5006
    """
    def __init__(self, fget, doc=None):
        super(classproperty, self).__init__(fget, doc=doc)

    def __get__(self, instance, instance_class=None):
        return self.fget(instance_class)

    def setter(self, fset):
        raise TypeError("classproperty is readonly due to python's architecture")

    def deleter(self, fdel):
        raise TypeError("classproperty is readonly due to python's architecture")


class property(FuncDecorator):
    """A replacement for the built-in @property that enables extra functionality

    See http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    see https://docs.python.org/2/howto/descriptor.html
    see http://stackoverflow.com/questions/17330160/python-how-does-the-property-decorator-work
    see https://docs.python.org/2/howto/descriptor.html

    as of 3.8, functools as a cached_property decorator:
        https://docs.python.org/3/library/functools.html#functools.cached_property

    :Example:
        # make this property memoized (cached)
        class Foo(object):
            @property(cached="_bar")
            def bar(self):
                return 42 # will be cached to self._bar
        f = Foo()
        f.bar # 42
        f._bar # 42

    Options you can pass into the decorator to customize the property

        * allow_empty -- boolean (default True) -- False to not cache empty values (eg, None, "")
        * cached -- string, pass in the variable name (eg, "_foo") that the value
            returned from the getter will be cached to
        * setter -- string, set this to variable name (similar to cached) if you want the decorated
            method to act as the setter instead of the getter, this will cause a default
            getter to be created that just returns variable name
        * deleter -- string, same as setter, but the descorated method will be the deleter and default
            setters and getters will be created
        * readonly -- string, the decorated method will be the getter and set the value 
            into the name defined in readonly, and no setter or deleter will be allowed
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None, **kwargs):
        self.getter(fget)
        self.setter(fset)
        self.deleter(fdel)

        if doc:
            self.__doc__ = doc

        self.name = ""
        for k in ["cached", "cache", "setter", "deleter"]:
            if k in kwargs:
                self.name = kwargs[k]
                break

        self.readonly = False
        if "readonly" in kwargs:
            self.name = kwargs["readonly"]
            self.readonly = True

        self.cached = True if self.name else False
        self.allow_empty = kwargs.pop('allow_empty', True)

    def log(self, format_str, *format_args, **log_options):
        fget = getattr(self, "fget", None)
        if fget:
            log_options.setdefault(
                "prefix",
                "[{}.{}]".format(self.__class__.__name__, fget.__name__)
            )
        return super(property, self).log(format_str, *format_args, **log_options)

    def decorate(self, method, *args, **kwargs):
        if "setter" in kwargs:
            ret = self.setter(method)

        elif "deleter" in kwargs:
            ret = self.deleter(method)

        else:
            ret = self.getter(method)

        return ret

    def get_value(self, instance):
        if self.fget:
            try:
                return self.fget(instance)

            except AttributeError as e:
                # if there is a __getattr__ then this AttributeError could get
                # swallowed and so let's log it before raising it
                # fixes https://github.com/Jaymon/decorators/issues/4
                if hasattr(instance, "__getattr__"):
                    self.log(e)
                raise
                # swallowed and so let's reraise it as a ValueError
#                     exc_info = sys.exc_info()
#                     reraise(ValueError, e, exc_info[2])
# 
#                 else:
#                     raise

        else:
            raise AttributeError("Unreadable attribute")

    def __get__(self, instance, instance_class=None):
        # if there is no instance then they are requesting the property from the class
        if instance is None:
            return self

        # we temporarily set readonly to False to make it possible to set the
        # value when fetched from the getter, then we set the value back to the
        # original value
        readonly = self.readonly
        self.readonly = False

        if self.cached:
            if self.name in instance.__dict__:
                self.log("Checking cache for {}", self.name)
                value = instance.__dict__[self.name]
                if not value and not self.allow_empty:
                    self.log("Cache failed for {}", self.name)
                    value = self.get_value(instance)
                    if value or self.allow_empty:
                        self.__set__(instance, value)

            else:
                value = self.get_value(instance)
                if value or self.allow_empty:
                    self.log("Caching value in {}", self.name)
                    self.__set__(instance, value)

        else:
            value = self.get_value(instance)

        self.readonly = readonly

        return value

    def __set__(self, instance, value):
        if self.readonly:
            raise AttributeError("Can't set readonly attribute")

        if self.cached:
            self.log("Caching value in {}", self.name)
            if self.fset:
                self.fset(instance, value)

            else:
                instance.__dict__[self.name] = value

        else:
            if self.fset is None:
                raise AttributeError("Can't set attribute")

            self.fset(instance, value)

    def __delete__(self, instance):
        if self.readonly:
            raise AttributeError("Can't delete readonly attribute")

        if self.cached:
            self.log("Deleting cached value in {}", self.name)
            if self.fdel:
                self.fdel(instance)

            else:
                if self.name in instance.__dict__:
                    instance.__dict__.pop(self.name, None)

                else:
                    raise AttributeError("Can't delete attribute")

        else:
            if self.fdel:
                self.fdel(instance)
            else:
                raise AttributeError("Can't delete attribute")

    def getter(self, fget):
        self.fget = fget
        return self

    def setter(self, fset):
        self.fset = fset
        return self

    def deleter(self, fdel):
        self.fdel = fdel
        return self

