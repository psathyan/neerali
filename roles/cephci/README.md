# cephci

This role is a wrapper around the existing downstream qe ci framework. The
source code is [here](https://github.com/red-hat-storage/cephci).

This wrapper expects the provisioning and pre_install not to be part of
cephci call.

## Privilege escalation

No, privileged escalation is not required.

## Parameters

* `neerali_cephci_repo` (str) The repository link to be used.
* `neerali_cephci_repo_branch` (str) The branch to be used for cloning.
  Defaults to `master`.
* `neerali_cephci_params` (dict) Arguments to be passed `run.py`. Please refer
  to [using user provided infrastructure](https://cephci.readthedocs.io/en/latest/source/getting_started.html#execution)
  for supportted parameters.
* `neerali_cephci_conf` (dict) Key/value pairs to stored in `.cephci.yaml`

## Examples

The below parameters are set when `neerali` is used for provisioning and
pre-requisites configuration.

```yaml
neerali_cephci_conf:
  reports:
    polarion:
      url: http://polarion.example.com/polarion
      user: foo
      token: basr
      default_project: CEPH

neerali_cephci_params:
  suite: 'suites/squid/rgw/tier-0_rgw.yaml'
  'log-level': 'debug'
  build: 'latest'
  rhbuild: '8.0'
  platform: 'rhel-9'
```
