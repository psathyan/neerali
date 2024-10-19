# prepare_sys

The purpose of this role is to prepare the system for Ceph deployment. It performs
installing the required packages and configuring the system.

## Privilege escalation

Yes, privileged access is required as the tasks performed are related to package
install. Along with system configuration.

## Parameters

* `neerali_prepare_sys_ulimit` (bool) defaults to `false`. Sets the ulimit to
  unlimited for the non-root user.
* `neerali_prepare_sys_packages_extra` (list) defaults to `[]`. Additional
  packages to be installed can be mentioned in this list.
* `neerali_prepare_sys_chrony_server` (str) defaults to `clock.corp.redhat.com`
  server name to be configured with chronyd
* `neerali_prepare_sys_certs` (list) defaults to `[]`. The elements point to a
  location for downloading required CA trust certificates. It could be an URI
  or an path to the certificate.
* `neerali_prepare_sys_user`(str) name of the privileged user to be created.
  Defaults to `cephuser`
* `neerali_prepare_sys_dtrs` (list) defaults to `[]`. The elements are maps
  holding information to access Docker / Container registeries.
* `neerali_prepare_sys_sysctl_conf` (dict) holds the kernel tunable parameters
  that needs to be applied on the systems.
* `neerali_prepare_sys_firewalld` (boo) defaults to `true`. Ensure the firewall
  service is enabled on the host.
* `neerali_prepare_sys_use_fqdn` (bool) when enable configures the hostname of
  the system to use FQDN. Defaults to `false`
* `neerali_prepare_sys_use_shortname` (bool) defaults to `true`. Ensure the
  hostname of the system is the shortname.
* `neerali_prepare_sys_firewall_ports` (list) the custom ports to be opened in
  the firewall.

## Examples

Some the values that are used

```yaml
neerali_prepare_sys_ulimit: true
neerali_prepare_sys_dtrs:
  - username: service-account
    password: "<masked>"
    registry: quay.io
neerali_prepare_sys_packages_extra:
  - docker
neerali_prepare_sys_sysctl_conf:
  'net.ipv6.conf.all.disable_ipv6': 1
  'vm.min_free_kbytes': 968578
```
