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
```

#### Example for overriding default images

```YAML
neerali_ceph_container_images:
  prometheus: quay.io/prometheus/prometheus:latest
  loki: docker.io/grafana/loki:latest
```
