# -*- coding: utf-8 -*-
"""Implements frequently used workflows related to compute lifecycle."""
from typing import List, Optional

from libcloud.compute.base import Node  # noqa

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
