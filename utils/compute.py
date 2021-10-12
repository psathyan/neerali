# -*- coding: utf-8 -*-
"""Implements frequently used workflows related to compute lifecycle."""
from time import sleep
from typing import List, Optional

from libcloud.compute.base import Node  # noqa
from libcloud.compute.drivers.openstack import StorageVolume  # noqa

from compute.openstack import OpenStack, get_openstack_driver

from .config import CephCIConfig
from .log import Log
from .parallel import parallel

LOG = Log()


def list_servers_softlayer(name: Optional[str] = None) -> List:
    """
    Returns a list of server objects matching the given name in IBM Cloud.

    The argument can be a substring or pattern to be used for filtering.

    Args:
        name (str):     Name or pattern to be used for retrieving the servers.

    Returns:
        Collection
    """
    pass


def list_servers_openstack(name: Optional[str] = None) -> List[Node]:
    """
    Returns a list of server objects matching the given name in IBM Cloud.

    The argument can be a substring or pattern to be used for filtering.

    Args:
        name (str):     Name or pattern to be used for retrieving the servers.

    Returns:
        Collection
    """
    driver = get_openstack_driver()
    if name:
        url = f"/servers?name={name}"
        obj = driver.connection.request(url).object
        servers = obj["servers"]
        return [driver.ex_get_node_details(server["id"]) for server in servers]

    return driver.list_nodes()


def list_servers(name: Optional[str] = None) -> List:
    """
    Returns a collection of server objects matching the given name or full list.

    The argument can be a pattern or string to be used for filtering the list of servers
    from the specified project in the configuration file.

    Args:
        name (str):     Name or pattern to be used for retrieving the list of servers.

    Returns:

    """
    conf = CephCIConfig()
    if conf["compute"]["type"] == "openstack":
        return list_servers_openstack(name)

    if conf["compute"]["type"] == "softlayer-vpc":
        return list_servers_softlayer(name)


def delete_openstack_vms(pattern: str) -> None:
    """Remove all the VMs that match the given pattern."""
    for node in list_servers_openstack(name=pattern):
        vm = OpenStack(node=node)
        LOG.debug(f"Preparing to remove {vm.node.name}")
        with parallel() as p:
            p.spawn(vm.delete)


def delete_softlayer_vpc_vms(pattern: str) -> None:
    """Remove all the VMs that match the given pattern from IBM-Cloud."""
    for node in list_servers_softlayer(pattern):
        pass


def delete_volume_openstack(vol: StorageVolume) -> None:
    """
    Delete the provided volume.

    Args:
        vol (StorageVolume):    StorageVolume instance that needs to be removed.

    Returns:
        None
    """
    driver = get_openstack_driver()
    LOG.info(f"Removing openstack volume {vol.name}")

    driver.detach_volume(vol)
    sleep(5)
    driver.destroy_volume(vol)


def delete_volumes_openstack(pattern: str) -> None:
    """
    Remove the volumes whose names match the given pattern.

    Args:
        pattern (str):  Name/pattern used for filtering the volume name.

    Returns:
        None
    """
    driver = get_openstack_driver()
    with parallel() as p:
        for vol in driver.list_volumes():
            if not vol.name:
                continue

            if pattern in vol.name:
                p.spawn(delete_volume_openstack, vol)


def delete_vms(pattern: Optional[str] = None) -> None:
    """
    Remove all the VMs that match the given name or pattern.

    Args:
        pattern (str):  The name or pattern of the nodes to be removed.

    Returns:
        None
    """
    conf = CephCIConfig()
    pattern = pattern if pattern else conf.get("compute", {}).get("prefix")

    if not pattern:
        LOG.warning("Missing compute prefix information. Not removing any VMs")
        return

    LOG.info(f"Preparing to remove VMs having {pattern}")

    if conf["compute"]["type"] == "openstack":
        return delete_openstack_vms(pattern)

    if conf["compute"]["type"] == "softlayer-vpc":
        return delete_softlayer_vpc_vms(pattern)


def delete_volumes(pattern) -> None:
    """
    Remove all the VMs that match the given name or pattern.

    Args:
        pattern (str):  The name or pattern of the nodes to be removed.

    Returns:
        None
    """
    conf = CephCIConfig()

    LOG.info(f"Preparing to remove volumes having {pattern}")

    if conf["compute"]["type"] == "openstack":
        return delete_volumes_openstack(pattern)
