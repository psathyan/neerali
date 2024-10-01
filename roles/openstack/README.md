# openstack

This role performs create, update and delete operations on openstack resources like networks, volumes and compute instances.

## Parameters

* `neerali_openstack_auth` (dict): holds openstack cloud authentication information.
We will get the required params value by downloading clouds.yaml file from openstack.
Refer [supported](#supported-keys-for-neerali_openstack_auth)

### Supported keys for neerali_openstack_auth

* `auth_type` (str) Auth type for openstack cloud.
* `auth` (dict) has the below key value paris.
  * `auth_url` (url) URL for RHOS openstack.
  * `application_credential_id` (str) User id for openstack.
  * `application_credential_secret` (str) Secret/password for openstack.

## Examples

This role looks for system information in the below format.

```YAML
neerali_systems_layout:
  vms:
    - name: node-01
      type: ceph
      cluster: ceph
      driver: openstack
      count: N
      image: <image_name>
      flavor: <flavor_name>
      roles:
        - _admin
        - mgr
        - mon
      networks:
        - public
      volumes:
        size: M
        count: N
    - name: node-02
      type: ceph
      cluster: ceph
      driver: openstack
      image: <image_name>
      flavor: <flavor_name>
      roles:
        - osd
      volumes:
        count: N
        size: M
      networks:
        - public
        - data
    - name: node-03
      type: client
      driver: openstack
      roles:
        - client
      networks:
        - public
  networks:
    public:
      name: <network-name>
      driver: openstack
    data:
      name: <network-name>
      cidr: <value>
      domain: <value>
      driver: openstack

neerali_use_openstack: true
```
