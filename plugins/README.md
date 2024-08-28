# Custom plugins

## Filters

### get_reimage_nodes

Returns an iteratable having information of the operating system family,
version and a list of nodes. The filter expects the below mapping

```YAML
neerali_systems_layout:
  baremetal:
    - name: ceph-node-01
      cluster: ceph
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
      cluster: ceph
      driver: teuthology
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

### dict2args

An helper that converts a given dictionary into a string in the CLI arguments
format. The return value can be passed directly to any executable.

```YAML
_boostrap_args:
  skip-pull: True
  skip-ping-check: False
  mon-ip: 192.168.10.10
```

After parsing the dictionary the output would be
`--skip-pull --mon-ip 192.168.10.10`

### conf2cmds

An helper that converts a given dictionary into a list of commands that can be
used to configure a Ceph cluster. The return value is a list of ceph commands.

```YAML
neerali_ceph_config:
  conf:
    config:
      set:
        global:
          log_to_file: 'true'
          log_to_journald: 'false'
    balancer: off
    osd:
      set: noscrub
```

The returned value would be

```YAML
- ceph config set global log_to_file true
- ceph config set global log_to_journald false
- ceph balancer off
- ceph osd set noscrub
```
