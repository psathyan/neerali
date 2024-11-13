#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core.api_exception import ApiException

from ansible_collections.neerali.general.plugins.module_utils.ceph_vm_ibmvpc import CephVMNodeIBMVPC

DOCUMENTATION = '''
---
module: get_ibmvpc_dnszones
short_description: Retrieve IBM Cloud dns zones information.
description:
  - This module retrieves and returns dns zones on IBM cloud.
author:
  - Venkatesh Ravula
options:
  access_key:
    description:
      - IBM Cloud API access key.
    required: true
    type: str
  dns_service_url:
    description:
      - Endpoint URL for the IBM Cloud dns service.
    required: false
    type: str
  instance_id:
    description:
      - ID of dns service instance
    required: false
    type: str
  name:
    description:
      - Name of dns zone.
    required: false
    type: str
'''

EXAMPLES = '''
# Retrieve dns zones information
- name: Get dns zones from IBM Cloud
  get_ibmvpc_dnszones:
    access_key: "your_ibm_access_key"
    name: "zesty-spinach"
  register: result
'''

RETURN = '''
dnszones:
    description: Dict of dns zones in the IBM Cloud.
    type: dict
    elements: str
    returned: always
'''

def run_module():
    # Define module arguments
    module_args = dict(
        access_key=dict(type='str', required=True),
        dns_service_url=dict(type='str', required=False),
        instance_id=dict(type='str', required=False),
        name=dict(type='str', required=False)
    )

    # Initialize the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Collect input parameters
    access_key = module.params['access_key']
    dns_service_url = module.params['dns_service_url']
    instance_id = module.params['instance_id']
    name = module.params['name']

    # Initialize the IBM Cloud dns service
    try:
        vm_node = CephVMNodeIBMVPC(access_key=access_key, dns_service_url=dns_service_url)
    except ApiException as e:
        module.fail_json(msg=f"Failed to authenticate or initialize VPC service: {str(e)}")

    # Gather dns zones information
    try:
        dns_zones = vm_node.get_dnszones(instance_id=instance_id, zone_name=name)
        result = dict(
            changed=False,
            dns_zones=dns_zones
        )
        module.exit_json(**result)
    except ApiException as e:
        module.fail_json(msg=f"Failed to retrieve dns zones information: {str(e)}")

def main():
    run_module()

if __name__ == '__main__':
    main()