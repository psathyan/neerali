# -*- coding: utf-8 -*-
"""IBM Cloud VPC provider for provisioning VMs in a VPC environment."""
import re
from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
from typing import Dict, List

from ibm_cloud_networking_services import DnsSvcsV1
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_vpc import VpcV1  # noqa

from compute import CephVMNode
from utils.config import CephCIConfig
from utils.log import Log
from utils.parallel import parallel

LOG = Log()
CONF = CephCIConfig()


def get_ibm_service() -> VpcV1:
    """Return the authenticated VPC client."""
    access_key = CONF["compute"]["credential"]["api-key"]
    authenticator = IAMAuthenticator(access_key)
    service = VpcV1(authenticator=authenticator)

    endpoint = CONF["compute"]["endpoint"]
    service.set_service_url(endpoint)

    return service


def get_dns_service() -> DnsSvcsV1:
    """Return the authenticated DNS API client."""
    access_key = CONF["compute"]["credential"]["api-key"]
    authenticator = IAMAuthenticator(access_key)
    dnssvc = DnsSvcsV1(authenticator=authenticator)
    dnssvc.set_service_url("https://api.dns-svcs.cloud.ibm.com/v1")

    return dnssvc


def get_resource_id(resource_name: str, json_obj: Dict) -> str:
    """
    Return the ID of the provided resource from the given response.

    Args:
        resource_name (str):    Name of the resource whose ID needs to be found.
        json_obj (dict):        Response received from the collection request.
    """
    resource_url = json_obj["first"]["href"]
    resource_list_name = re.search(r"v1/(.*?)\?", resource_url).group(1)
    for i in json_obj[resource_list_name]:
        if i["name"] == resource_name:
            return i["id"]


def get_dns_zone_id(dns_zone_name, json_obj) -> str:
    """
    Gets the Zone ID with Zone name
    Args:
        dns_zone_name (str):    Name of the zone whose ID needs to be found.
        json_obj (dict):        Response received from the collection request.
    """
    for i in json_obj["dnszones"]:
        if i["name"] == dns_zone_name:
            return i["id"]


def remove_dns_records(name: str, zone_name: str) -> None:
    """
    Removes the DNS PTR & A records for the provided node name.

    Args:
        name          Name(pattern) of DNS records for type:A
        zone_name     Name of a zone
    """
    LOG.info(f"Removing DNS records which has name: {name}")
    try:
        dnssvc = get_dns_service()
        dns_zone = dnssvc.list_dnszones("a55534f5-678d-452d-8cc6-e780941d8e31")
        dns_zone_id = get_dns_zone_id(zone_name, dns_zone.get_result())  # noqa
        resource = dnssvc.list_resource_records(
            instance_id="a55534f5-678d-452d-8cc6-e780941d8e31",
            dnszone_id=dns_zone_id,
        )
        records_a = [
            i
            for i in resource.get_result()["resource_records"]
            if i["type"] == "A" and name in i["name"]
        ]
        for record in records_a:
            if record["linked_ptr_record"] is not None:
                LOG.info(f"Deleting dns record {record['linked_ptr_record']['name']}")
                dnssvc.delete_resource_record(
                    instance_id="a55534f5-678d-452d-8cc6-e780941d8e31",
                    dnszone_id=dns_zone_id,
                    record_id=record["linked_ptr_record"]["id"],
                )
            LOG.info(f"Deleting dns record {record['name']}")
            dnssvc.delete_resource_record(
                instance_id="a55534f5-678d-452d-8cc6-e780941d8e31",
                dnszone_id=dns_zone_id,
                record_id=record["id"],
            )
    except Exception:
        raise AssertionError(f"Failed to remove DNS record: {name}")


# Custom exception objects
class ResourceNotFound(Exception):
    pass


class ExactMatchFailed(Exception):
    pass


class VolumeOpFailure(Exception):
    pass


class NetworkOpFailure(Exception):
    pass


class NodeError(Exception):
    pass


class NodeDeleteFailure(Exception):
    pass


class SoftlayerVPC(CephVMNode):
    """Represent the VMNode required for cephci."""

    def __init__(self) -> None:
        """
        Initialize the instance using the provided information."""
        self.service = get_ibm_service()
        self.node = None

        # CephVM attributes
        self._subnet: list = list()
        self._roles: list = list()

    def wait_until_vm_state_running(self, instance_id: str) -> None:
        """
        Wait until the VM moves to running state.

        Args:
            instance_id (str):  Id of node instance

        Returns:
            None

        Raises:
            NodeError
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=1200)

        node = None
        while end_time > datetime.now():
            sleep(5)
            resp = self.service.get_instance(instance_id)
            node = resp.get_result()

            if node["status"] == "running":
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                LOG.info(
                    f"{node['name']} moved to running state in {duration} seconds.",
                )
                return

            if node["status"] == "error":
                raise NodeError(f"{node['name']} has moved to error state.")

        raise NodeError(f"{node['name']} is in {node['status']} state.")

    def wait_until_nodes_delete(self, pattern: str, timeout: int) -> None:
        """
        Wait until the node is removed.

        Args:
            pattern (str):  The pattern to be used to filter the node names.
            timeout (int):  Max time to wait for the deletion to complete

        Returns:
            None
        """
        try:
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=timeout)
            nodes = list()
            while end_time > datetime.now():
                sleep(5)
                instance_list = self.service.list_instances()
                nodes = [
                    i
                    for i in instance_list.get_result()["instances"]
                    if pattern in i["name"]
                ]
                if not nodes:
                    return

            raise NodeError(f"Unable to remove the following instances : {nodes}")
        except ApiException as ae:
            if ae.code == 404:
                return

        raise NodeError("Unable to delete the node")

    def remove_instances(self, pattern: str, zone_name: str, timeout: int) -> None:
        """
        Remove all instances that match the given pattern.

        Args:
            pattern (str):      The substring to be search among instance names.
            zone_name (str):    The name of the DNS zone to used for removal of records.
            timeout (int):      Timeout in seconds provided for cleanup.

        Returns:
            None
        """
        remove_dns_records(pattern, zone_name)
        instances = self.service.list_instances()
        removal_nodes = [
            i for i in instances.get_result()["instances"] if pattern in i["name"]
        ]

        with parallel() as p:
            for instance in removal_nodes:
                LOG.info(f"Destroying node {instance['name']} with timeout:{timeout}")
                p.spawn(self.service.delete_instance, instance["id"])

        self.wait_until_nodes_delete(pattern, timeout)

    def create(
        self,
        node_name: str,
        image_name: str,
        network_name: str,
        private_key: str,
        vpc_name: str,
        profile: str,
        group_access: str,
        zone_name: str,
        zone_id_model_name: str,
        size_of_disks: int = 0,
        no_of_volumes: int = 0,
        userdata: str = "",
    ) -> None:
        """
        Create the instance in IBM Cloud with the provided data.

        Args:
            node_name           Name of the VM.
            image_name          Name of the image to use for creating the VM.
            network_name        Name of the Network
            private_key         Private ssh key
            vpc_name            Name of VPC
            profile             Node profile. EX: "bx2-2x8"
            group_access        group security policy
            zone_name           Name of zone
            zone_id_model_name  Name of zone identity model
            size_of_disks       size of disk
            no_of_volumes       Number of volumes for each node
            userdata            user related data

        """
        LOG.info(f"Starting to create VM with name {node_name}")

        try:
            subnets = self.service.list_subnets()
            subnet_id = get_resource_id(network_name, subnets.get_result())

            images = self.service.list_images()
            image_id = get_resource_id(image_name, images.get_result())

            keys = self.service.list_keys()
            key_id = get_resource_id(private_key, keys.get_result())

            security_group = self.service.list_security_groups()
            security_group_id = get_resource_id(
                group_access, security_group.get_result()
            )

            vpcs = self.service.list_vpcs()
            vpc_id = get_resource_id(vpc_name, vpcs.get_result())

            # Construct a dict representation of a KeyIdentityById model
            key_identity_model = {"id": key_id}

            # IBM-Cloud CI SSH key
            key_identity_shared = {
                "fingerprint": "SHA256:OkzMbGLDIzqUcZoH9H/j5o/v01trlqKqp5DaUpJ0tcQ"
            }

            # Construct a dict representation of a SecurityGroupIdentityById model
            security_group_identity_model = {"id": security_group_id}

            # Construct a dict representation of a ResourceIdentityById model
            resource_group_identity_model = {"id": "cb8d87c33ca04965a180fd7ab7383936"}

            # Construct a dict representation of a SubnetIdentityById model
            subnet_identity_model = {"id": subnet_id}

            # Construct a dict representation of a NetworkInterfacePrototype model
            network_interface_prototype_model = {
                "allow_ip_spoofing": False,
                "subnet": subnet_identity_model,
                "security_groups": [security_group_identity_model],
            }

            # Construct a dict representation of a InstanceProfileIdentityByName model
            instance_profile_identity_model = {"name": profile}

            # Construct a dict representation of a VolumeProfileIdentityByName model
            volume_profile_identity_model = {"name": "general-purpose"}

            volume_attachment_list = []
            for i in range(0, no_of_volumes):
                volume_attachment_volume_prototype_instance_context_model1 = dict()
                volume_attachment_volume_prototype_instance_context_model1["name"] = (
                    node_name.lower() + "-" + str(i)
                )
                volume_attachment_volume_prototype_instance_context_model1[
                    "profile"
                ] = volume_profile_identity_model
                volume_attachment_volume_prototype_instance_context_model1[
                    "capacity"
                ] = size_of_disks
                volume_attachment_prototype_instance_context_model1 = dict()
                volume_attachment_prototype_instance_context_model1[
                    "delete_volume_on_instance_delete"
                ] = True
                volume_attachment_prototype_instance_context_model1[
                    "volume"
                ] = volume_attachment_volume_prototype_instance_context_model1
                volume_attachment_list.append(
                    volume_attachment_prototype_instance_context_model1
                )

            # Construct a dict representation of a VPCIdentityById model
            vpc_identity_model = {"id": vpc_id}

            # Construct a dict representation of a ImageIdentityById model
            image_identity_model = {"id": image_id}

            # Construct a dict representation of a ZoneIdentityByName model
            zone_identity_model = {"name": zone_id_model_name}

            # Construct a dict representation of a InstancePrototypeInstanceByImage
            instance_prototype_model = dict(
                {"keys": [key_identity_model, key_identity_shared]}
            )

            instance_prototype_model["name"] = node_name.lower()
            instance_prototype_model["profile"] = instance_profile_identity_model
            instance_prototype_model["resource_group"] = resource_group_identity_model
            instance_prototype_model["user_data"] = userdata
            instance_prototype_model["volume_attachments"] = volume_attachment_list
            instance_prototype_model["vpc"] = vpc_identity_model
            instance_prototype_model["image"] = image_identity_model
            instance_prototype_model[
                "primary_network_interface"
            ] = network_interface_prototype_model
            instance_prototype_model["zone"] = zone_identity_model

            # Set up parameter values
            instance_prototype = instance_prototype_model
            response = self.service.create_instance(instance_prototype)

            instance_id = response.get_result()["id"]
            self.wait_until_vm_state_running(instance_id)
            self.node = self.service.get_instance(instance_id).get_result()

            dnssvc = get_dns_service()
            dns_zone = dnssvc.list_dnszones("a55534f5-678d-452d-8cc6-e780941d8e31")
            dns_zone_id = get_dns_zone_id(zone_name, dns_zone.get_result())  # noqa

            resource = dnssvc.list_resource_records(
                instance_id="a55534f5-678d-452d-8cc6-e780941d8e31",
                dnszone_id=dns_zone_id,
            )
            records_a = [
                i for i in resource.get_result()["resource_records"] if i["type"] == "A"
            ]
            records_ip = [
                i
                for i in records_a
                if i["rdata"]["ip"]
                == self.node["primary_network_interface"]["primary_ipv4_address"]
            ]
            if records_ip:
                dnssvc.update_resource_record(
                    instance_id="a55534f5-678d-452d-8cc6-e780941d8e31",
                    dnszone_id=dns_zone_id,
                    record_id=records_ip[0]["id"],
                    name=self.node["name"],
                    rdata=records_ip[0]["rdata"],
                )

            dnssvc.create_resource_record(
                instance_id="a55534f5-678d-452d-8cc6-e780941d8e31",
                dnszone_id=dns_zone_id,
                type="A",
                ttl=900,
                name=self.node["name"],
                rdata={
                    "ip": self.node["primary_network_interface"]["primary_ipv4_address"]
                },
            )

            dnssvc.create_resource_record(
                instance_id="a55534f5-678d-452d-8cc6-e780941d8e31",
                dnszone_id=dns_zone_id,
                type="PTR",
                ttl=900,
                name=self.node["primary_network_interface"]["primary_ipv4_address"],
                rdata={"ptrdname": f"{self.node['name']}.{zone_name}"},
            )

        except (ResourceNotFound, NetworkOpFailure, NodeError, VolumeOpFailure):
            raise
        except BaseException as be:  # noqa
            LOG.error(be, exc_info=True)
            raise NodeError(f"Unknown error. Failed to create VM with name {node_name}")

    # properties

    @property
    def ip_address(self) -> str:
        """Return the private IP address of the node."""
        return self.node["primary_network_interface"]["primary_ipv4_address"]

    @property
    def floating_ips(self) -> List[str]:
        """Return the list of floating IP's"""
        return self.node.public_ips if self.node else []

    @property
    def public_ip_address(self) -> str:
        """Return the public IP address of the node."""
        return self.node.public_ips[0]

    @property
    def hostname(self) -> str:
        """Return the hostname of the VM."""
        return self.node["name"]

    @property
    def volumes(self) -> List:
        """Return the list of storage volumes attached to the node."""
        if self.node is None:
            return []
        # Removing boot volume from the list
        volume_attachments = []
        for i in self.node["volume_attachments"]:
            volume_detail = self.service.get_volume(i["volume"]["id"])
            for vol in volume_detail.get_result()["volume_attachments"]:
                if vol["type"] == "data":
                    volume_attachments.append(vol)
        return volume_attachments

    @property
    def subnet(self) -> str:
        """Return the subnet information."""
        subnet_details = self.service.get_subnet(
            self.node["primary_network_interface"]["subnet"]["id"]
        )
        return subnet_details.get_result()["ipv4_cidr_block"]

    @property
    def shortname(self) -> str:
        """Return the short form of the hostname."""
        return self.hostname.split(".")[0]

    @property
    def no_of_volumes(self) -> int:
        """Return the number of volumes attached to the VM."""
        return len(self.volumes)

    @property
    def role(self) -> List:
        """Return the Ceph roles of the instance."""
        return self._roles

    @role.setter
    def role(self, roles: list) -> None:
        """Set the roles for the VM."""
        self._roles = deepcopy(roles)
