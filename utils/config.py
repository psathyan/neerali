"""CephCI singleton configuration model."""
from .utils import Singleton


class CephCIConfig(dict, metaclass=Singleton):
    """Ceph CI configuration object."""

    pass
