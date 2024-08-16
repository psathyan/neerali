# ceph
This role installs and configures Ceph storage.

## Privilege escalation
Yes, privileged access is required for installing ceph.

## Parameters
* `neerali_ceph_public_network` (str) public network CIDR
* `neerali_ceph_bootstrap_config` (dict) key value pairs as supported by
  cephadm bootstrap.
  Refer [link](https://docs.ceph.com/en/latest/man/8/cephadm/#bootstrap) for
  all supportted options
* `neerali_ceph_mgr_custom_images` (dict) key value pair holding details about
  custom container images to be used for deployment. The key must the suffix
  added to `container_image_<key>` with the value pointing to the URI of the
  image. The supported keys can be referred from
  [docs](https://docs.ceph.com/en/latest/cephadm/services/monitoring/#using-custom-images)
  Refer the
  [section](#example-for-overriding-default-images) 

### Example for passing additional bootstrap arguments
```YAML
neerali_ceph_bootstrap_config:
  cluster-network: 192.168.10.0/24
  ssh-user: zuul
```

### Example for overriding default images
```YAML
neerali_ceph_mgr_custom_images:
  prometheus: quay.io/prometheus/prometheus:latest
  loki: docker.io/grafana/loki:latest
```

## Examples
Add samples on using the role.
