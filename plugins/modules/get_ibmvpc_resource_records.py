#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ibm_cloud_sdk_core.api_exception import ApiException

from ansible_collections.neerali.general.plugins.module_utils.ceph_vm_ibmvpc import CephVMNodeIBMVPC

DOCUMENTATION = '''
---
module: get_ibmvpc_resource_records
short_description: Retrieve IBM Cloud resource records information.
description:
  - This module retrieves and returns resource records on IBM cloud.
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
  zone_name:
    description:
      - Name of dns zone
    required: true
    type: str
  record_ip:
    description:
      - ip address of resource record.
    required: false
    type: str
'''

EXAMPLES = '''
# Retrieve resource records information
- name: Get resource records from IBM Cloud
  get_ibmvpc_resource_records:
    access_key: "your_ibm_access_key"
    zone_name: "zesty-spinach"
    record_ip: "10.0.64.222"
  register: result
'''

RETURN = '''
resource_records:
    description: List of resource records in the IBM Cloud.
    type: list
    elements: dict
    returned: always
'''

def run_module():
    # Define module arguments
    module_args = dict(
        access_key=dict(type='str', required=True),
        dns_service_url=dict(type='str', required=False),
        instance_id=dict(type='str', required=False),
        zone_name=dict(type='str', required=True),
        record_ip=dict(type='str', required=False)
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
    zone_name = module.params['zone_name']
    record_ip = module.params['record_ip']

    # Initialize the IBM Cloud dns service
    try:
        vm_node = CephVMNodeIBMVPC(access_key=access_key, dns_service_url=dns_service_url)
    except ApiException as e:
        module.fail_json(msg=f"Failed to authenticate or initialize dns service: {str(e)}")

    # Gather resource records information
    try:
        resource_records = vm_node.get_resource_records(zone_name=zone_name, instance_id=instance_id, record_ip=record_ip)
        result = dict(
            changed=False,
            resource_records=resource_records
        )
        module.exit_json(**result)
    except ApiException as e:
        module.fail_json(msg=f"Failed to retrieve resource records information: {str(e)}")

def main():
    run_module()

if __name__ == '__main__':
    main()