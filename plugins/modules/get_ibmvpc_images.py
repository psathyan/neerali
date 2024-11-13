#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core.api_exception import ApiException

from ansible_collections.neerali.general.plugins.module_utils.ceph_vm_ibmvpc import CephVMNodeIBMVPC

DOCUMENTATION = '''
---
module: get_ibmvpc_images
short_description: Retrieve IBM Cloud images information.
description:
  - This module retrieves and returns images on IBM cloud.
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
  resource_group_name:
    description:
      - Name of resource group.
    required: false
    type: str
  resource_group_id:
    description:
      - ID of resource group.
    required: false
    type: str
  name:
    description:
      - Name of image.
    required: false
    type: str
'''

EXAMPLES = '''
# Retrieve images information
- name: Get images from IBM Cloud
  get_ibmvpc_images:
    access_key: "your_ibm_access_key"
    service_url: "https://us-south.iaas.cloud.ibm.com/v1"
    resource_group_name: "abccsede-sdds"
    name: "rhel-9"
  register: result
'''

RETURN = '''
images:
    description: dict of images in the IBM Cloud.
    type: dict
    elements: str
    returned: always
'''

def run_module():
    # Define module arguments
    module_args = dict(
        access_key=dict(type='str', required=True),
        service_url=dict(type='str', required=False),
        resource_group_name=dict(type='str', required=False),
        resource_group_id=dict(type='str', required=False),
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
    resource_group_name = module.params['resource_group_name']
    resource_group_id = module.params['resource_group_id']
    name = module.params['name']

    # Initialize the IBM Cloud VPC instance handler
    try:
        vm_node = CephVMNodeIBMVPC(access_key=access_key, service_url=service_url)
    except ApiException as e:
        module.fail_json(msg=f"Failed to authenticate or initialize VPC service: {str(e)}")

    # Gather images information
    try:
        images = vm_node.get_images(resource_group_name=resource_group_name, resource_group_id=resource_group_id, image_name=name)
        result = dict(
            changed=False,
            images=images
        )
        module.exit_json(**result)
    except ApiException as e:
        module.fail_json(msg=f"Failed to retrieve images information: {str(e)}")

def main():
    run_module()

if __name__ == '__main__':
    main()