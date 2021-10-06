# -*- coding: utf-8 -*-
"""Implementation of providers that provision the systems for CephCI."""
import openstack
from utils.config import CephCIConfig


class CephVMNode:
    """Ceph VM Node object."""

    def __new__(cls, *args, **kwargs):
        """Return the correct compute object."""
        conf = CephCIConfig()
        provider = conf["compute"]["type"]

        if provider == "openstack":
            cls = openstack.OpenStack
        else:
            raise NotImplementedError(f"Unknown compute type: {provider}")

        return super(CephVMNode, cls).__new__(cls)
