#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
from typing import List, Optional
from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_cloud_networking_services import DnsSvcsV1
from ibm_cloud_networking_services.dns_svcs_v1 import (
    ResourceRecordInputRdataRdataARecord,
    ResourceRecordInputRdataRdataPtrRecord,
)
import logging

logger = logging.getLogger(__name__)


def get_logger(mod_name):
    """
    To activate logs, setup the environment var LOGFILE
    e.g.: export LOGFILE=/tmp/ansible-ibmvpc.log
    Args:
        mod_name: module name
    Returns: Logger instance
    """

    logger = logging.getLogger(os.path.basename(mod_name))
    global LOGFILE
    LOGFILE = os.environ.get('LOGFILE')
    if not LOGFILE:
        logger.addHandler(logging.NullHandler())
    else:
        logging.basicConfig(level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                            format='%(asctime)s %(levelname)s %(name)s %(message)s',
                            filename=LOGFILE, filemode='a')
    return logger

class CephVMNodeIBMVPC:
    """
    A class to represent a Ceph VM Node in IBM Cloud VPC, responsible for
    retrieving volume information associated with a VPC instance.
    """
    
    def __init__(
        self,
        access_key: str,
        service_url: Optional[str] = "https://us-south.iaas.cloud.ibm.com/v1",
        dns_service_url: Optional[str] = "https://api.dns-svcs.cloud.ibm.com/v1",
        # vsi_id: Optional[str] = None,
        # node: Optional[Dict] = None
    ) -> None:
        """
        Initializes the CephVMNodeIBM instance with IBM Cloud API details.

        :param access_key: The API access key for IBM Cloud.
        :param service_url: The URL endpoint for IBM Cloud VPC service.
        :param dns_service_url: The URL endpoint for IBM Cloud dns service.
        :param vsi_id: The virtual server instance (VSI) ID.
        :param node: Node dictionary.
        """
        self._dns_service_instance_id = "b7efc2ce-ebf7-4dca-b7cf-b328171229a5"

        authenticator = IAMAuthenticator(access_key)
        self.vpc_service = VpcV1(authenticator=authenticator)
        if service_url:
            self.vpc_service.set_service_url(service_url=service_url)
        self.dnssvc = DnsSvcsV1(authenticator=authenticator)
        if dns_service_url:
            self.dnssvc.set_service_url(service_url=dns_service_url)

    def get_resource_groups(self, resource_group_name=None) -> None:
        """
        Retrieve resource groups information in the region.

        Args:
          resource_group_name: Name of resource group

        :return: Dictionary of resource group name and its ID.
        """
        vpcs_response = self.vpc_service.list_vpcs().get_result().get("vpcs", [])
        resource_groups_info = {}
        for each_vpc in vpcs_response:
            resource_groups_info.update({
                each_vpc["resource_group"]["name"]: each_vpc["resource_group"]["id"]
            })
        if resource_group_name:
            return resource_groups_info.get(resource_group_name)
        else:
            return resource_groups_info

    def get_vpcs(self, resource_group_name=None, resource_group_id=None, vpc_name=None) -> None:
        """
        Retrieve VPCs information in the region.

        Args:
          resource_group_name: Name of resource group to fetch the vpcs associated with it within the region
          resource_group_id: ID of resource group to fetch the vpcs associated with it within the region
          vpc_name: Name of VPC

        :return: List of VPCs, each as a dictionary.
        """
        try:
            if resource_group_name and not resource_group_id:
                resource_group_id = self.get_resource_groups(resource_group_name)

            vpcs = self.vpc_service.list_vpcs(resource_group_id=resource_group_id).get_result().get("vpcs", [])
            vpcs_info = []
            for vpc_item in vpcs:
                vpc_info = {
                    "name": vpc_item["name"],
                    "id": vpc_item["id"],
                    "resource_group": vpc_item["resource_group"]["name"],
                    "dns_servers": [item["address"] for item in vpc_item["dns"]["resolver"]["servers"]]
                }
                vpcs_info.append(vpc_info)
            if vpc_name:
                return next((item for item in vpcs_info if item["name"] == vpc_name), None)
            return vpcs_info
        except Exception as e:
            raise Exception(f"Failed to retrieve VPCs: {e}")

    def get_subnets(self, resource_group_name=None, resource_group_id=None, zone_name=None, vpc_name=None, network_name=None) -> None:
        """
        Retrieve all subnets information in the region.

        Args:
          resource_group_name: Name of resource group to fetch the subnets associated with it within the region
          resource_group_id: ID of resource group to fetch the subnets associated with it within the region
          zone_name: Name of the zone to filter the subnets associated with it
          vpc_name: Name of VPC
          network_name: Filter subnet info based on name

        :return: List of subnets, each as a dictionary.
        """
        try:
            if resource_group_name and not resource_group_id:
                resource_group_id = self.get_resource_groups(resource_group_name)

            subnets = self.vpc_service.list_subnets(resource_group_id=resource_group_id, zone_name=zone_name, vpc_name=vpc_name).get_result().get("subnets", [])
            subnets_info = []
            for subnet_item in subnets:
                subnet_info = {
                    key: subnet_item[key] for key in ["name", "id", "ipv4_cidr_block", "available_ipv4_address_count"]
                }
                subnets_info.append(subnet_info)
            if network_name:
                return next((item for item in subnets_info if item["name"] == network_name), None)
            return subnets_info
        except Exception as e:
            raise Exception(f"Failed to retrieve subnets: {e}")

    def get_images(self, resource_group_name=None, resource_group_id=None, image_name=None) -> None:
        """
        Retrieve the images information.

        Args:
          resource_group_name: Name of resource group to fetch the images within the region
          resource_group_id: ID of resource group to fetch the images within the region
          image_name: Name of the image

        :return: Dictionary of images.
        """
        try:
            if resource_group_name and not resource_group_id:
                resource_group_id = self.get_resource_groups(resource_group_name)

            images = self.vpc_service.list_images(resource_group_id=resource_group_id, name=image_name).get_result().get("images", [])
            images_info = []
            for image_item in images:
                image_info = {
                    key: image_item[key] for key in ["name", "id", "operating_system"]
                }
                images_info.append(image_info)
            if image_name and len(images_info) == 1:
                return images_info[0]
            return images_info
        except Exception as e:
            raise Exception(f"Failed to retrieve images: {e}")

    def get_sshkeys(self, resource_group_name=None, resource_group_id=None, key_name=None) -> None:
        """
        Retrieve the ssh keys information.

        Args:
          resource_group_name: Name of resource group to fetch the ssh keys associated with it
          resource_group_id: ID of resource group to fetch the ssh keys associated with it
          key_name: Name of the ssh key to filter the ssh keys

        :return: List of ssh keys, each as a dictionary.
        """
        try:
            if resource_group_name and not resource_group_id:
                resource_group_id = self.get_resource_groups(resource_group_name)

            ssh_keys = self.vpc_service.list_keys().get_result().get("keys", [])
            if resource_group_id:
                ssh_keys = [item for item in ssh_keys if item["resource_group"]["id"] == resource_group_id]
            sshkeys_info = []
            for sshkey_item in ssh_keys:
                sshkey_info = {
                    key: sshkey_item[key] for key in ["name", "id", "fingerprint", "public_key"]
                }
                sshkeys_info.append(sshkey_info)
            if key_name:
                return next((item for item in sshkeys_info if item["name"] == key_name), {})
            return sshkeys_info
        except Exception as e:
            raise Exception(f"Failed to retrieve ssh keys: {e}")

    def get_instance_profiles(self) -> List:
        """
        Retrieve the instance profiles information.

        Args:
          profile_name: Name of the instance profile

        :return: List of instance profiles.
        """
        try:
            profiles = self.vpc_service.list_instance_profiles().get_result().get("profiles", [])
            return [profile["name"] for profile in profiles]
        except Exception as e:
            raise Exception(f"Failed to retrieve instance profiles: {e}")

    def get_security_groups(self, resource_group_name=None, resource_group_id=None, vpc_name=None, group_name=None) -> None:
        """
        Retrieve the security groups information.

        Args:
          resource_group_name: Name of resource group to fetch the security groups associated with it within the region
          resource_group_id: ID of resource group to fetch the security groups associated with it within the region
          vpc_name: Name of VPC
          group_name: Name of the security group

        :return: Dictionary of security groups.
        """
        try:
            if resource_group_name and not resource_group_id:
                resource_group_id = self.get_resource_groups(resource_group_name)

            groups = self.vpc_service.list_security_groups(resource_group_id=resource_group_id, vpc_name=vpc_name).get_result().get("security_groups", [])
            groups_info = {item["name"]: item["id"] for item in groups}
            if group_name:
                return groups_info.get(group_name)
            return groups_info
        except Exception as e:
            raise Exception(f"Failed to retrieve security groups: {e}")

    def get_server_instances(self, resource_group_name=None, resource_group_id=None, vpc_name=None, server_name=None) -> None:
        """
        Retrieve the virtual server instances information.

        Args:
          resource_group_name: Name of resource group to fetch the server instances associated with it within the region
          resource_group_id: ID of resource group to fetch the server instances associated with it within the region
          vpc_name: Name of VPC
          server_name: Name of the server instance

        :return: List of dictionary of server instances
        """
        try:
            if resource_group_name and not resource_group_id:
                resource_group_id = self.get_resource_groups(resource_group_name)

            instances = self.vpc_service.list_instances(resource_group_id=resource_group_id, vpc_name=vpc_name, name=server_name).get_result().get("instances", [])
            instances_info = []
            for vsi in instances:
                instance_info = {
                    "name": vsi["name"],
                    "id": vsi["id"],
                    "ip_address": vsi["primary_network_interface"]["primary_ip"]["address"],
                    "profile": vsi["profile"]["name"],
                    "zone": vsi["zone"]["name"],
                    "volumes": self.get_instance_volumes(vsi["id"])
                }
                for attribute in ["image", "resource_group", "vpc"]:
                    instance_info[attribute] = vsi[attribute]["name"]

                instances_info.append(instance_info)
            if server_name and len(instances_info) == 1:
                return instances_info[0]
            return instances_info
        except Exception as e:
            raise Exception(f"Failed to retrieve server instances: {e}")

    def get_instance_volumes(self, vsi_id) -> list:
        """
        Retrieve volume information associated with the instance.

        Args:
          vsi_id: ID of VSI instance

        :return: List of attached volumes, each as a dictionary.
        """
        try:
            volumes_info = []
            response = self.vpc_service.list_instance_volume_attachments(vsi_id)
            volume_attachments = response.get_result().get("volume_attachments", [])

            for attachment in volume_attachments:
                volume_info = {
                    "name": attachment["volume"]["name"],
                    "id": attachment["volume"]["id"],
                    "type": attachment["type"],
                    "delete_with_instance": attachment["delete_volume_on_instance_delete"]
                }
                volumes_info.append(volume_info)

            return volumes_info
        except ApiException as e:
            raise ApiException(f"Failed to retrieve volumes: {e}")

    def get_volumes(self, volume_name=None, zone_name=None, state=None) -> None:
        """
        Retrieve the volumes information.

        Args:
          volume_name: Name of the volume
          zone_name: Filter the volumes associated with the zone
          state: Filter volumes by attachment state

        :return: List of dictionary of volumes
        """
        try:
            volumes = self.vpc_service.list_volumes(name=volume_name, zone_name=zone_name, attachment_state=state).get_result().get("volumes", [])
            volumes_info = []
            for vol in volumes:
                vol_info = {
                    key: vol[key] for key in ["name", "id", "status", "active", "capacity", "attachment_state"]
                }
                vol_info["zone"] = vol["zone"]["name"]
                volumes_info.append(vol_info)
            if volume_name and len(volumes_info) == 1:
                return volumes_info[0]
            return volumes_info
        except Exception as e:
            raise Exception(f"Failed to retrieve volumes: {e}")

    def get_dnszones(self, instance_id=None, zone_name=None) -> None:
        """
        Retrieve the dns zones information.

        Args:
          instance_id: ID of dns service instance
          zone_name: Name of the dns zone

        :return: Dictionary of dns zones.
        """
        try:
            if not instance_id:
                instance_id = self._dns_service_instance_id
            zones = self.dnssvc.list_dnszones(instance_id=instance_id).get_result().get("dnszones", [])
            zones_info = {item["name"]: item["id"] for item in zones}
            if zone_name:
                return zones_info.get(zone_name)
            return zones_info
        except Exception as e:
            raise Exception(f"Failed to retrieve dns zones: {e}")

    def get_resource_records(self, zone_name=None, instance_id=None, record_ip=None) -> None:
        """
        Retrieve the resource records information.

        Args:
          zone_name: Name of the dns zone
          instance_id: ID of dns service instance
          record_ip: ip address of the resource record

        :return: List of dictionary of resource records.
        """
        try:
            if not instance_id:
                instance_id = self._dns_service_instance_id
            zone_id = self.get_dnszones(instance_id=instance_id, zone_name=zone_name)
            resource_records = self.dnssvc.list_resource_records(instance_id=instance_id, dnszone_id=zone_id).get_result().get("resource_records", [])
            records_info = {}
            for each_record in resource_records:
                record_attributes = ["name", "id", "type", "ttl", "rdata"]
                if each_record["type"] == "A":
                    ip_address = each_record["rdata"]["ip"]
                    record = {key: each_record[key] for key in record_attributes}
                    if each_record.get("linked_ptr_record"):
                        record["ptr"] = {key: each_record["linked_ptr_record"][key] for key in record_attributes}
                    records_info[ip_address] = record
            if record_ip:
                return records_info.get(record_ip)
            return list(records_info.values())
        except Exception as e:
            raise Exception(f"Failed to retrieve resource records: {e}")

    def create_resource_records(self, zone_name=None, server_name=None, instance_id=None) -> None:
        """
        Create the resource records for the VSI.

        Args:
          zone_name: Name of the dns zone
          server_name: Name of the server instance
          instance_id: ID of dns service instance

        :return: Dictionary of created resource record.
        """
        if not instance_id:
            instance_id = self._dns_service_instance_id
        dns_zone_id = self.get_dnszones(instance_id=instance_id, zone_name=zone_name)
        server_response = self.get_server_instances(server_name=server_name)

        a_record = ResourceRecordInputRdataRdataARecord(server_response["ip_address"])
        self.dnssvc.create_resource_record(
            instance_id=instance_id,
            dnszone_id=dns_zone_id,
            type="A",
            ttl=900,
            name=server_response["name"],
            rdata=a_record
        )

        ptr_record = ResourceRecordInputRdataRdataPtrRecord(f"{server_response['name']}.{zone_name}")
        self.dnssvc.create_resource_record(
            instance_id=instance_id,
            dnszone_id=dns_zone_id,
            type="PTR",
            ttl=900,
            name=server_response["ip_address"],
            rdata=ptr_record,
        )

    def update_resource_records(self, zone_name=None, server_name=None, instance_id=None) -> None:
        """
        Updates the resource records for the VSI.

        Args:
          zone_name: Name of the dns zone
          server_name: Name of the server instance
          instance_id: ID of dns service instance

        :return: Dictionary of created resource record.
        """
        if not instance_id:
            instance_id = self._dns_service_instance_id
        dns_zone_id = self.get_dnszones(instance_id=instance_id, zone_name=zone_name)
        server_response = self.get_server_instances(server_name=server_name)

        server_record = self.get_resource_records(
            zone_name=zone_name,
            instance_id=instance_id,
            record_ip=server_response["ip_address"]
        )
        if server_record:
            self.dnssvc.update_resource_record(
                instance_id=instance_id,
                dnszone_id=dns_zone_id,
                record_id=server_record["id"],
                name=server_response["name"],
                rdata=server_record["rdata"]
            )

    def delete_resource_records(self, zone_name=None, server_name=None, instance_id=None) -> None:
        """
        Deletes the resource records for the VSI instance.

        Args:
          zone_name: Name of the dns zone
          server_name: Name of the server instance
          instance_id: ID of dns service instance
        """
        if not instance_id:
            instance_id = self._dns_service_instance_id
        dns_zone_id = self.get_dnszones(instance_id=instance_id, zone_name=zone_name)
        server_response = self.get_server_instances(server_name=server_name)

        server_record = self.get_resource_records(
            zone_name=zone_name,
            instance_id=instance_id,
            record_ip=server_response["ip_address"]
        )
        if server_record:
            if server_record.get("ptr"):
                logger.info(
                    f"Deleting PTR record {server_record['ptr']['name']}"
                )
                self.dnssvc.delete_resource_record(
                    instance_id=instance_id,
                    dnszone_id=dns_zone_id,
                    record_id=server_record["ptr"]["id"],
                )

            logger.info(f"Deleting Address record {server_record['name']}")
            self.dnssvc.delete_resource_record(
                instance_id=instance_id,
                dnszone_id=dns_zone_id,
                record_id=server_record["id"],
            )
            return
        logger.debug(f"No matching DNS records found for {server_name}")

    def create_server(
        self,
        server_name: str,
        image_name: str,
        network_name: str,
        ssh_keys: list,
        vpc_name: str,
        profile: str,
        security_group: str,
        dnszone_name: str,
        zone: str,
        resource_group: str = "Ceph-qe",
        volume_size: int = 0,
        volume_count: int = 0,
        user_data: str = "",
    ) -> None:
        """
        Create the server instance in IBM Cloud with the provided data.

        Args:
            server_name:         Name of the VM.
            image_name:          Name of the image to use for creating the VM.
            network_name:        Name of the Network
            ssh_keys:            List of public ssh keys
            access_key:          Users IBM cloud access key
            vpc_name:            Name of VPC
            profile:             Node profile. EX: "bx2-2x8"
            security_group:      Name of security policy
            dnszone_name:        Name of dns zone
            zone:                Name of zone identity model. eg: "us-south-2"
            resource_group:      Name of the resource group
            volume_size:         Size of disk volume in GiB
            volume_count:        Number of volumes for each node
            user_data:           Cloud init user related data

        """
        server_name = server_name.lower()
        logger.info(f"Starting to create VM with name {server_name}")
        try:
            # Retrieve the object id based on names
            vpc_id = self.get_vpcs(vpc_name=vpc_name).get("id")
            subnet = self.get_subnets(network_name=network_name)
            self._subnet = subnet.get("ipv4_cidr_block")
            security_group_id = self.get_security_groups(group_name=security_group)
            image_id = self.get_images(image_name=image_name).get("id")
            ssh_key_ids = [self.get_sshkeys(key_name=sshkey).get("id") for sshkey in ssh_keys]
            resource_group_id = self.get_resource_groups(resource_group_name=resource_group)

            # Construct a dict representation of a IdentityById model
            vpc_identity_model = dict({"id": vpc_id})
            subnet_identity_model = dict({"id": subnet["id"]})
            security_group_identity_model = dict({"id": security_group_id})

            # Construct a dict representation of a NetworkInterfacePrototype model
            network_interface_prototype_model = dict(
                {
                    "allow_ip_spoofing": False,
                    "subnet": subnet_identity_model,
                    "security_groups": [security_group_identity_model],
                }
            )
            image_identity_model = dict({"id": image_id})
            key_identity_model = [dict({"id": key_id}) for key_id in ssh_key_ids]
            resource_group_identity_model = dict({"id": resource_group_id})

            # Construct a dict representation of a IdentityByName model
            instance_profile_identity_model = dict({"name": profile})
            zone_identity_model = dict({"name": zone})

            # Construct a dict representation of a VolumeProfileIdentityByName model
            volume_profile_identity_model = dict({"name": "general-purpose"})
            volume_attachment_list = []
            for i in range(0, volume_count):
                volume_attachment_volume_instance_model = dict(
                    {
                        "name": f"{server_name}-{str(i)}",
                        "profile": volume_profile_identity_model,
                        "capacity": volume_size,
                    }
                )
                volume_attachment_instance_model = dict(
                    {
                        "delete_volume_on_instance_delete": True,
                        "volume": volume_attachment_volume_instance_model,
                    }
                )
                volume_attachment_list.append(volume_attachment_instance_model)

            # Prepare the VSI payload
            instance_prototype_model = dict(
                keys=key_identity_model,
                name=server_name,
                image=image_identity_model,
                profile=instance_profile_identity_model,
                resource_group=resource_group_identity_model,
                vpc=vpc_identity_model,
                zone=zone_identity_model,
                primary_network_interface=network_interface_prototype_model,
                volume_attachments=volume_attachment_list,
                user_data=user_data
            )

            instance_id = self.vpc_service.create_instance(instance_prototype_model).get_result()["id"]
            self.wait_until_vm_state_running(instance_id)

            # DNS record creation phase
            logger.debug(f"Adding DNS records for {server_name}")
            self.update_resource_records(zone_name=dnszone_name, server_name=server_name)
            self.create_resource_records(zone_name=dnszone_name, server_name=server_name)

            return self.get_server_instances(server_name=server_name)
        except NodeError:
            raise
        except BaseException as be:  # noqa
            logger.error(be)
            raise NodeError(f"Unknown error. Failed to create VM with name {server_name}")

    def delete_server(self, server_name: str, dnszone_name: Optional[str] = None) -> None:
        """
        Removes the VSI instance along with its DNS record.

        Args:
            server_name (str): Name of the server instance
            dnszone_name (str): DNS zone name associated with the instance.

        Returns:
            None

        Raises:
            NodeDeleteFailure
        """
        server_name = server_name.lower()
        try:
            self.delete_resource_records(zone_name=dnszone_name, server_name=server_name)
        except BaseException:  # noqa
            logger.warning(f"Encountered an error in removing DNS records of {server_name}")
            pass

        logger.info(f"Preparing to delete VSI: {server_name}")
        server_id = self.get_server_instances(server_name=server_name).get("id")
        resp = self.vpc_service.delete_instance(id=server_id)

        if resp.get_status_code() != 204:
            logger.debug(f"{server_name} cannot be found.")
            return

        # Wait for the VM to be deleted
        end_time = datetime.now() + timedelta(seconds=600)
        while end_time > datetime.now():
            sleep(5)
            try:
                resp = self.vpc_service.get_instance(server_id)
                if resp.get_status_code == 404:
                    logger.info(f"Successfully removed server {server_name}")
                    return
            except ApiException:
                logger.info(f"Successfully removed server {server_name}")
                return

        logger.debug(resp.get_result())
        raise NodeDeleteFailure(f"Failed to delete {server_name}")

    def wait_until_vm_state_running(self, instance_id: str) -> None:
        """
        Waits until the VSI moves to a running state within the specified time.

        Args:
            instance_id (str)   The ID of the VSI to be checked.

        Returns:
            None

        Raises:
            NodeError
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=1200)

        node_details = None
        while end_time > datetime.now():
            sleep(5)
            resp = self.vpc_service.get_instance(instance_id)
            if resp.get_status_code() != 200:
                logger.debug("Encountered an error getting the instance.")
                sleep(5)
                continue

            node_details = resp.get_result()
            if node_details["status"] == "running":
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"{node_details['name']} moved to running state in {duration} seconds.")
                return

            if node_details["status"] == "failed":
                raise NodeError(node_details["status_reasons"])

        raise NodeError(f"{node_details['name']} is in {node_details['status']} state.")


class NodeError(Exception):
    pass


class NodeDeleteFailure(Exception):
    pass
