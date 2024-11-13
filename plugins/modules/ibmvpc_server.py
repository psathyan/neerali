#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core.api_exception import ApiException

from ansible_collections.neerali.general.plugins.module_utils.ceph_vm_ibmvpc import CephVMNodeIBMVPC

DOCUMENTATION = '''
---
module: ibmvpc_server
short_description: Create or updates server in IBM Cloud.
description:
  - This module creates or updates server in IBM cloud.
author:
  - Venkatesh Ravula
options:
  access_key:
    description:
      - IBM Cloud API access key.
    required: true
    type: str
  service_url:
    description:
      - Endpoint URL for the IBM Cloud VPC service.
    required: false
    type: str
  dns_service_url:
    description:
      - Endpoint URL for the IBM Cloud dns service.
    required: false
    type: str
  state:
    description:
      - Indicates the desired state for the server instance
    default: present
    choices: ['present', 'absent']
    type: str
  name:
    description:
      - Name of server
    required: true
    type: str
  image:
    description:
      - Name of image used to create server
    required: false
    type: str
  network:
    description:
      - Name of the network for primary network interface
    default: sn-20240306-02
    type: str
  ssh_keys:
    description:
      - SSH private keys to be added to instance
    required: false
    type: list
  vpc:
    description:
      - Name of vpc
    default: ceph-qe-vpc
    type: str
  profile:
    description:
      - Name of the instance profile
    default: bx2-2x8
    type: str
  security_group:
    description:
      - Name of the security policy group
    default: flick-outgoing-rejoicing-broadways
    type: str
  dns_zone:
    description:
      - Name of the dns zone
    default: dall.qe.ceph.local
    type: str
  zone:
    description:
      - Name of the zone for cloud instance deployment
    default: Ceph-qe
    type: str
  resource_group:
    description:
      - Name of resource group.
    default: Ceph-qe
    type: str
  volume_size:
    description:
      - Size of each volume disk in GiB
    required: false
    type: int
  volume_count:
    description:
      - Count of volume disks for each server
    default: 1
    type: int
  user_data:
    description:
      - Cloud-init user data for server
    required: false
    type: str
'''

EXAMPLES = '''
# Creates server in ibm cloud vpc
- name: Create server in IBM Cloud
  ibmvpc_server:
    access_key: "your_ibm_access_key"
    service_url: "https://us-south.iaas.cloud.ibm.com/v1"
    state: present
    name: test-server1
    image: ibm-redhat-9-4-minimal-amd64-1
    network: sn-20240306-02
    ssh_keys: cephci-private-key
    vpc: ceph-qe-vpc
    profile: bx2-2x8
    security_group: flick-outgoing-rejoicing-broadways
    zone: us-south-1
    dns_zone: dall.qe.ceph.local
    resource_group: Ceph-qe
    volume_size: 10
    volume_count: 2
    user_data: userdata
  register: result
'''

RETURN = '''
server:
    description: Response of created server in the IBM Cloud.
    type: dict
    elements: str
    returned: always
'''

def run_module():
    # Define module arguments
    module_args = dict(
        access_key=dict(type='str', required=True),
        service_url=dict(type='str', required=False),
        dns_service_url=dict(type='str', required=False),
        state=dict(choices=['present', 'absent'], default='present'),
        name=dict(type='str', required=True),
        image=dict(type='str', required=False),
        network=dict(type='str', default='sn-20240306-02'),
        ssh_keys=dict(type='list', default=['ceph-qe-jenkins']),
        vpc=dict(type='str', default='ceph-qe-vpc'),
        profile=dict(type='str', default='bx2-2x8'),
        security_group=dict(type='str', default='flick-outgoing-rejoicing-broadways'),
        zone=dict(type='str', default='us-south-2'),
        resource_group=dict(type='str', default='Ceph-qe'),
        dns_zone=dict(type='str', default='dall.qe.ceph.local'),
        volume_size=dict(type='int', required=False),
        volume_count=dict(type='int', default=1),
        user_data=dict(type='str', required=False)
    )

    # Initialize the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Collect input parameters
    access_key = module.params['access_key']
    service_url = module.params['service_url']
    dns_service_url = module.params['dns_service_url']
    state = module.params['state']
    name = module.params['name']
    image = module.params['image']
    network = module.params['network']
    ssh_keys = module.params['ssh_keys']
    vpc = module.params['vpc']
    profile = module.params['profile']
    security_group = module.params['security_group']
    zone = module.params['zone']
    dns_zone = module.params['dns_zone']
    resource_group = module.params['resource_group']
    volume_size = module.params['volume_size']
    volume_count = module.params['volume_count']
    user_data = module.params['user_data']

    # Initialize the IBM Cloud VPC instance handler
    try:
        vm_node = CephVMNodeIBMVPC(access_key=access_key, service_url=service_url, dns_service_url=dns_service_url)
    except ApiException as e:
        module.fail_json(msg=f"Failed to authenticate or initialize VPC and DNS service: {str(e)}")

    # Create server instance
    try:
        changed = False
        server_instance = None
        if state == 'present':
            server_instance = vm_node.get_server_instances(server_name=name)
            if not server_instance:
                changed = True
                server_instance = vm_node.create_server(
                    server_name=name,
                    image_name=image,
                    network_name=network,
                    ssh_keys=ssh_keys,
                    vpc_name=vpc,
                    profile=profile,
                    zone=zone,
                    security_group=security_group,
                    dnszone_name=dns_zone,
                    resource_group=resource_group,
                    volume_size=volume_size,
                    volume_count=volume_count,
                    user_data=user_data
                )
        elif state == 'absent':
            if vm_node.get_server_instances(server_name=name):
                changed = True
                server_instance = vm_node.delete_server(
                    server_name=name,
                    dnszone_name=dns_zone
                )

        result = dict(
            changed=changed,
            server=server_instance
        )
        module.exit_json(**result)
    except ApiException as e:
        module.fail_json(msg=f"Failed to create/delete server instance: {str(e)}")

def main():
    run_module()

if __name__ == '__main__':
    main()