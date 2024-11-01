# client_warp

Install and configure warp across all clients

## Privilege escalation

Yes, privilege escalation is required for warp install and service enablement.

## Parameters

* `neerali_client_warp_rpm` (str) the package to be installed.
* `neerali_client_warp_dry_run` (bool) by default is `false`. When enabled, it
  does not enable or disable the client service. This flag is for unit testing.