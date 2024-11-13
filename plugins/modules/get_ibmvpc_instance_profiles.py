#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core.api_exception import ApiException

from ansible_collections.neerali.general.plugins.module_utils.ceph_vm_ibmvpc import CephVMNodeIBMVPC

DOCUMENTATION = '''
---
module: get_ibmvpc_instance_profiles
short_description: Retrieve IBM Cloud instance profiles information.
description:
  - This module retrieves and returns instance profiles on IBM cloud.
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
'''

EXAMPLES = '''
# Retrieve instance profiles information
- name: Get instance profiles from IBM Cloud
  get_ibmvpc_instance_profiles:
    access_key: "your_ibm_access_key"
    service_url: "https://us-south.iaas.cloud.ibm.com/v1"
  register: result
'''

RETURN = '''
instance_profiles:
    description: List of instance profiles in the IBM Cloud.
    type: list
    elements: str
    returned: always
'''

def run_module():
    # Define module arguments
    module_args = dict(
        access_key=dict(type='str', required=True),
        service_url=dict(type='str', required=False),
    )

    # Initialize the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Collect input parameters
    access_key = module.params['access_key']
    service_url = module.params['service_url']

    # Initialize the IBM Cloud VPC instance handler
    try:
        vm_node = CephVMNodeIBMVPC(access_key=access_key, service_url=service_url)
    except ApiException as e:
        module.fail_json(msg=f"Failed to authenticate or initialize VPC service: {str(e)}")

    # Gather instance profiles information
    try:
        instance_profiles = vm_node.get_instance_profiles()
        result = dict(
            changed=False,
            instance_profiles=instance_profiles
        )
        module.exit_json(**result)
    except ApiException as e:
        module.fail_json(msg=f"Failed to retrieve instance profiles information: {str(e)}")

def main():
    run_module()

if __name__ == '__main__':
    main()