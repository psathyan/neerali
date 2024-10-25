# ceph

This role installs and configures Ceph storage. The role reads the configuration
information under the each cluster name / location.

## Privilege escalation

Yes, privileged access is required for installing ceph.

## Parameters

* `neerali_ceph_cluster_name` (str) defaults to `ceph`, name of the cluster
  location.
* `neerali_ceph_config` (dict) is the primary source of configuration. The keys
  under it are cluster / site specific configurations. The site / cluster
  specific are also `dict`. The supported keys are listed under the
  [section](#supported-keys-for-ceph-config)
* `neerali_ceph_container_images` (dict) key value pair holding details about
  custom container images to be used for deployment. The key must the suffix
  added to `container_image_<key>` with the value pointing to the URI of the
  image. The supported keys can be referred from
  [docs](https://docs.ceph.com/en/latest/cephadm/services/monitoring/#using-custom-images)
  Refer the [section](#example-for-overriding-default-images)

### Supported keys for ceph config

* `public_network` (str) public network CIDR
* `bootstrap` (dict) key value pairs as supported by cephadm bootstrap.
  Refer [link](https://docs.ceph.com/en/latest/man/8/cephadm/#bootstrap) for
  all supportted options.
* `osd` (dict) supports `options | specs` keys. `options` holds a string that
  can be directly passed to the orchestrator. Whereas `specs` is a list of spec
  file contents that needs to be applied.
* `conf` (dict) cluster configuration or tuning parameters.
* `nvmeof` (dict) keys supported are describe [here](#supported-keys-of-nvmeof).

### Supported keys of nvmeof

* `specs` (list) list of service specifications as described in the documment
  [1](https://docs.ceph.com/en/latest/rbd/nvmeof-target-configure/).
* `pg` (int) The placement group allowed in a OSD device
* `pg_num` (int) number of placement groups to be applied / changed.
* `cli_image` (uri) absolute docker image to be used for creating the alias.
* `target` (dict) key/value pairs required for configuring the storage target.
  Please refer [section](#supported-keys-of-nvmeoftarget)

### Supported keys of nvmeof.target

A dict that has the name of subsytem as the key. The following keys are further
supported by each subsystem key.

* `options` (list) Supported key/value pairs that can be passed as CLI options
  while creating a subsystem. Please refer the supported keys in the
  [section](#supported-keys-of-nvmeoftargetoptions).
* `listeners` (list) A list key/value pairs that can be passed as CLI options
  for creating a listener.
  Please refer [section](#supported-keys-of-nvmeoftargetlisteners)
* `allowed_hosts` (list) A list of allowed hosts.

### Supported keys of nvmeof.target.[*].options

* `serial-number` (str) serial number to be configured.
* `max-namespaces` (int) The maximum number of namespaces allowed.

### Supported keys of nvmeof.target.[*].listeners

* `hostname` (str) Host name of the NVMe-oF gateway host.
* `traddr` (str) Optional, the IP address of the host.
* `trsvcid` (int) The port number to be used.
* `adrfam` (str) IP address family. Allowed values are `ipv4 | ipv6`.
* `count` (int) Optional, the number of hosts to be selected. It cannot be used
  with other keys.

#### Example for passing additional bootstrap arguments

```YAML
neerali_ceph_config:
  ceph:
    bootstrap:
      cluster-network: 192.168.10.0/24
      ssh-user: zuul
    nvmeof:
      specs:
        - |
          ---
          service_type: nvmeof
          service_id: nvmeof_pool1
          placement:
            label: nvemof_group1
          spec:
            pool: nvmeof_pool1
      target:
        group01:
          'nqn.2016-04.spdk.io:cnode01`:
            options:
              max-namespaces: 100
            listeners:
              - hostname: ceph-node-gw-01
                traddr: 192.168.10.11
              - hostname: ceph-node-gw-02
                traddr: 192.168.10.12
            allowed_hosts:
              - nqn.2014-08.com:nvme:client01
              - nqn.2014-08.com:nvme:client02
```

#### Example for overriding default images

```YAML
neerali_ceph_container_images:
  prometheus: quay.io/prometheus/prometheus:latest
  loki: docker.io/grafana/loki:latest
```
