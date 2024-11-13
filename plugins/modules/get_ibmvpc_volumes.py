#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core.api_exception import ApiException

from ansible_collections.neerali.general.plugins.module_utils.ceph_vm_ibmvpc import CephVMNodeIBMVPC

DOCUMENTATION = '''
---
module: get_ibmvpc_volumes
short_description: Retrieve IBM Cloud volumes information.
description:
  - This module retrieves and returns volumes of IBM cloud.
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
      - Name of volume.
    required: false
    type: str
  zone_name:
    description:
      - Name of zone with which volumes are associated with.
    required: false
    type: str
  state:
    description:
      - State of volume attachment
    required: false
    type: str
'''

EXAMPLES = '''
# Retrieve volumes information
- name: Get volumes from IBM Cloud
  get_ibmvpc_volumes:
    access_key: "your_ibm_access_key"
    service_url: "https://us-south.iaas.cloud.ibm.com/v1"
    name: "test-vol1"
  register: result
'''

RETURN = '''
volumes:
    description: List of volumes in the IBM Cloud.
    type: list
    elements: dict
    returned: always
'''

def run_module():
    # Define module arguments
    module_args = dict(
        access_key=dict(type='str', required=True),
        service_url=dict(type='str', required=False),
        name=dict(type='str', required=False),
        zone_name=dict(type='str', required=False),
        state=dict(type='str', required=False)
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
    zone_name = module.params['zone_name']
    state = module.params['state']

    # Initialize the IBM Cloud VPC instance handler
    try:
        vm_node = CephVMNodeIBMVPC(access_key=access_key, service_url=service_url)
    except ApiException as e:
        module.fail_json(msg=f"Failed to authenticate or initialize VPC service: {str(e)}")

    # Gather volumes information
    try:
        volumes = vm_node.get_volumes(volume_name=name, zone_name=zone_name, state=state)
        result = dict(
            changed=False,
            volumes=volumes
        )
        module.exit_json(**result)
    except ApiException as e:
        module.fail_json(msg=f"Failed to retrieve volume information: {str(e)}")

def main():
    run_module()

if __name__ == '__main__':
    main()