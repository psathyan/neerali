#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core.api_exception import ApiException

from ansible_collections.neerali.general.plugins.module_utils.ceph_vm_ibmvpc import CephVMNodeIBMVPC

DOCUMENTATION = '''
---
module: get_ibmvpc_resource_groups
short_description: Retrieve IBM Cloud resource groups information.
description:
  - This module retrieves and returns resource groups of IBM cloud.
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
  name:
    description:
      - Name of resource group.
    required: false
    type: str
'''

EXAMPLES = '''
# Retrieve resource groups information
- name: Get resource groups from IBM Cloud
  get_ibmvpc_resource_groups:
    access_key: "your_ibm_access_key"
    service_url: "https://us-south.iaas.cloud.ibm.com/v1"
    name: "rg-name"
  register: result
'''

RETURN = '''
resource_groups:
    description: Dictionary of resource group name and ID present in the IBM Cloud.
    type: dict
    elements: str
    returned: always
'''

def run_module():
    # Define module arguments
    module_args = dict(
        access_key=dict(type='str', required=True),
        service_url=dict(type='str', required=False),
        name=dict(type='str', required=False)
    )

    # Initialize the module
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Collect input parameters
    access_key = module.params['access_key']
    service_url = module.params['service_url']
    name = module.params['name']

    # Initialize the IBM Cloud VPC instance handler
    try:
        vm_node = CephVMNodeIBMVPC(access_key=access_key, service_url=service_url)
    except ApiException as e:
        module.fail_json(msg=f"Failed to authenticate or initialize VPC service: {str(e)}")

    # Gather resource group information
    try:
        resource_groups = vm_node.get_resource_groups(resource_group_name=name)
        result = dict(
            changed=False,
            resource_groups=resource_groups
        )
        module.exit_json(**result)
    except ApiException as e:
        module.fail_json(msg=f"Failed to retrieve resource groups information: {str(e)}")

def main():
    run_module()

if __name__ == '__main__':
    main()