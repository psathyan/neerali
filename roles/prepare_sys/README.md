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

## Examples
Add samples on using the role.
