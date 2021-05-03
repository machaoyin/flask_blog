# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import logging

from .base import (
    Decorator,
    InstanceDecorator,
    ClassDecorator,
    FuncDecorator,
)
from .descriptor import (
    property,
    classproperty,
)
from .misc import (
    once,
    deprecated,
)


__version__ = "2.0.7"


# get rid of "No handler found" warnings (cribbed from requests)
logging.getLogger(__name__).addHandler(logging.NullHandler())

