# run_hook
This role is executes the give playbook/s as part of pre or post stage in the
execution process.

## Privilege escalation
No privilege escalation is required by this role per se. However, the running
playbook may require privilege escalation.

## Parameters
* `step` (list) The phase in which the list of playbooks must be executed.

### dictionary in step
An item in step may have the below parameters
* `name` (string) The name of the playbook to be set.
* `source` (string) absolute path to the playbook
* `extra_vars` (map) key/values pairs to be passed additionally to the playbook.

## Examples
```YAML
pre_infra:
  - name: Sample hook - DNS configuration
    source: hooks/deploy-dns.yaml
    extra_vars:
      doman: ceph.lab
```
