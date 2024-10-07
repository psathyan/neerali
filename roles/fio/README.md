# fio

This role creates a fio image that can be used to create multiple containers to generate concurrent i/o's for both block and file storage.
A target image by name `neerali_fio:latest` will be created on client machines.

## Privilege escalation

Yes, privileged access is required to build/run this container

## Parameters

No parameters are needed for this role

## Usage

All parameters are Optional: 
* `-d`/`--dev-type`       : Device Type, Valid options are `fs` for file (CIFS/NFS) or `blk` (block), By default the value is `fs`  
* `-b`/`--block-device`   : if `dev-type` ( or `-d`) is `blk`, then specify device path (eg: `/dev/sdb` or `/dev/sdc`)
* `-t`/`--time-to-run`    : For time based run, Specify in seconds 
* `-n`/`--num-jobs`        : number of parallel fio jobs, by default it is `1`
* `-s`/`--file-size`      : file size for `dev-type`=`fs`. default is `1G`

## Example

```podman run neerali_fio:latest --dev-type=fs --time-to-run=600 --file-size=10G```
