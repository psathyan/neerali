# client_nvme

The purpose of the role is to configure NVMe over fabrics using NVMe/TCP.

## Privilege escalation

Yes, privileged access is required for configuring the nodes.

## Parameters

* `neerali_client_nvme_iopolicy` defaults to `round-robin`, the IO policy to be
  configured for NVMe over TCP.
