# repo_setup

This role configures the system repository using yum or subscription-manager.

## Privilege escalation

Yes, privileged access is required for the role to run successfully.

## Parameters

* `neerali_repo_setup_rhsm` (mapping) key/value pairs required for configuring
  subscription manager. Refer
  [section](#supported-keys-by-neerali_repo_setup_rhsm)
* `neerali_repo_setup_remove_repo_files` (bool) defaults to false. When enabled
  clears the all files found in `/etc/yum.repos.d/` directory.
* `neerali_repo_setup_repos` (list) contains a map that has information about
  the repositories to be enabled. Additional repos can be passed via the var
  `neerali_repo_setup_repos_extras`. The supported keys for the items in the
  list are [section](#supported-keys-by-neerali_repo_setup_repos).
* `neerali_repo_setup_os_update` (bool) defaults to `true`, updates the system
  when subscription manager and/or repos are configured.

### Supported keys by neerali_repo_setup_rhsm

* `username` (str) the username to be used in RHSM.
* `password` (str) password of the given user.
* `url` (str) base url of CDN
* `release` (str) the operating system version to be configured.

### Supported keys by neerali_repo_setup_repos

* `name` (str) repo custom name
* `baseurl` (str) URL to the repodata directory
* `description` (str) repository description
* `enabled` (bool) defaults to true, enables the yum repository
* `gpgcheck` (bool) defaults to false, enables the gpgcheck for the repository.
