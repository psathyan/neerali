# Custom plugins

## Filters

### get_reimage_nodes
Returns an iteratable having information of the operating system family,
version and a list of nodes. The filter expects the below mapping

```YAML
neerali_systems_layout:
  baremetal:
    - name: ceph-node-01
      driver: teuthology
      os:
        type: rhel
        version: 9.4
      roles:
        - _admin
        - mgr
      devices:
        data: []
        wal: []
        db: []
    - name: ceph-node-02
      provisioner: teuthology
      os:
        type: rhel
        version: 9.2
      roles:
        - mon
      devices:
        data: []
        wal: []
        db: []
```

The output format would be

```YAML
- "--os-type rhel --os-version 9.4 ceph-node-01"
- "--os-type rhel --os-version 9.2 ceph-node-02"
```

### get_admin_nodes
Returns a string having information of the first found node with `_admin` label
which would be used for bootstrapping the cluster. The information uses
`neerali_systems_layout` or `neerali_provisioned_systems` for extracting the
required information.

The output would be
```bash
ceph-node-01
```
