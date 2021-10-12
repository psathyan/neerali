# -*- coding: utf-8 -*-
"""
CephCI singleton configuration model.

Provides an easy method to access the test configurations. The only drawback is the test
developer must use define a global variable. They tend to get loaded earlier that lead
to empty values.
"""
from .utils import Singleton


class CephCIConfig(dict, metaclass=Singleton):
    """Ceph CI configuration object."""

    pass
