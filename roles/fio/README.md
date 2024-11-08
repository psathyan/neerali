# fio

This role creates a fio image that can be used to create multiple containers to generate concurrent i/o's for both block and file storage.
A target image by name `neerali_fio:latest` will be created on client machines.

## Privilege escalation

Yes, privileged access is required to build/run this container

## Parameters

No parameters are needed for this role
This role creates a fio image that can be used to create multiple containers to generate concurrent i/o's for both block and file storage.
A target image by name `neerali_fio:latest` will be created on client machines.

## Usage

All parameters are Optional: 
* `-d`/`--dev-type`       : Device Type, Valid options are `fs` for file (CIFS/NFS) or `blk` (block), By default the value is `fs`. for `fs` it always assumes `/data` as default path for the fs
* `-b`/`--block-device`   : if `dev-type` ( or `-d`) is `blk`, then specify device path (eg: `/dev/sdb` or `/dev/sdc`)
* `-t`/`--time-to-run`    : For time based run, Specify in seconds 
* `-n`/`--num-jobs`       : number of parallel fio jobs, by default it is `1`
* `-s`/`--file-size`      : file size for `dev-type`=`fs`. default is `1G`
* `--iodepth`             : iodepth for fio, default is `128`, 
* `--rw`                  : Operation type, allowed values are `read`, `write`, `randread`, `randwrite`. default is `randwrite`
* `--bs`                  : block size, default is `4k`
* `--format`              : fio output format. allowed values are `normal`, `json`, `json+`, `terse`. default is `json`
* `--fio-file`            : provide fio file instead of all above arguments. Looks for the file under `/fio_files` and needs to be passed as container volume eg: `podman run --privileged -v $PWD:/fio_files neerali_fio --fio-file my_fio_file`

## Examples

```podman run -v /mnt:/data neerali_fio:latest --dev-type=fs --time-to-run=600 --file-size=10G```
```podman run -v $PWD:/fiofiles neerali_fio:latest --fio-file my_fio_file --format json```
