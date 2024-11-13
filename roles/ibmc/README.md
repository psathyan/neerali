# ibmc

This role performs fetch, create and delete operations on ibm cloud resources like networks, volumes and compute instances.

## Parameters

* `neerali_ibmc_auth` (dict): holds ibmc cloud authentication information.
Refer [supported](#supported-keys-for-neerali_ibmc_auth)

### Supported keys for neerali_ibmc_auth

* `access_key` (str) Access key for IBM cloud authentication.
* `service_url` (str) Service url for IBM VPC cloud.
* `dns_service_url` (str) Service url for IBM dns service instance.

## Examples

This role looks for system information in the below format.

```YAML
neerali_systems_layout:
  vms:
    - name: neerali-ibmc-node
      type: ceph
      cluster: ceph
      driver: ibmc
      count: 2
      image: ibm-redhat-9-4-minimal-amd64-1
      flavor: bx2-2x8
      ssh_keys:
        - ceph-qe-jenkins
        - ceph-private-key
      vpc: ceph-qe-vpc
      security_group: flick-outgoing-rejoicing-broadways
      zone: us-south-2
      dns_zone: dall.qe.ceph.local
      resource_group: Ceph-qe
      roles:
        - mon
        - osd
      volumes:
        count: 2
        size: 20
      networks:
        - sn-20240306-02

neerali_use_ibmc: true
```
