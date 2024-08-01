# teuthology
This role is wrapper around teuthology framework. The main purpose of this role
is to perform reimage of baremetal system using teuthology.

## Privilege escalation
Yes, teuthology configuration file needs to be placed in /etc directory. Also,
packages installation needed to execute teuthology.

## Parameters
* `neerali_teuthology_repo` (str) Teuthology repository URL. Defaults to
  https://github.com/ceph/teuthology.git.
* `neerali_teuthology_conf_fog` (mapping) holds the access details of the FOG
  server. This is required for creating the configuration file and reimage.
  Refer [supported](#supported-keys-for-neerali_teuthology_conf_fog)
* `neerali_teuthology_reimage` (bool) Defaults to `false`. When enabled the
  physical systems mentioned in `neerali_systems_layout` will be reprovisioned.

### Supported keys for neerali_teuthology_conf_fog
* `api_token` (str) API token to be used for provisioning.
* `user_token` (str) User token to be used for provisioning.
* `endpoint` (url) URL of the fog server.
* `types` (str) Only valid known families of machines.

## Examples
This role looks for system under information in the below format

```YAML
neerali_systems_layout:
  baremetal:
    - name: ceph-node-1
      driver: teuthology
      bmc:
        endpoint: foo.bar
        username: user_foo
        passwd: xxxx
      os:
        type: rhel
        version: 9.4
      roles:
        - _admin
        - osd
      devices:
        data: []
        db: []
        wal: []
```
