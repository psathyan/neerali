# iofiller

This role creates a iofiller image on client nodes that can be used to create multiple contianer to fill 
a filebased or block device to fill to certain extent in a loop.

The purpose is to fill the target by creating random files of an input size till the storage is filled to a define treshold.
When this treshold is reached, some percentage of the hence created files are automatically deleted and the loop goes on.

A target image by name `neerali_iofiller:latest` will be created on client nodes.

## Privilege escalation

Yes, the iofiller needs previliged access as there are format and mount operations done within the container.

## Parameters

* No parameters are needed for this role

## Usage

```podman run --privileged -v /mnt/nfs_mount:/data neerali_iofiller:latest /usr/local/bin/iofiller.sh -s 500 -m 10000```

Note: 
* All write operations for filesystem usage (non-block) assume `/data` to be mounted and hence it has to be set in podman call eg: `-v /mnt/nfs_mount:/data`
* for block data the block device is formatted and mounted under `/data` by the container itself

## All below parameters for the container are optional 

* `-t`/`--io-type`: Type of device ie., file or block device. valid options are `fs` or `blk`. Default: `fs`
* `-d`/`--device`: Device path if `-t blk` ie., block device. Eg: `/dev/sdf`
* `-i`/`--interval`: Time in seconds to sleep before moving to next file. Default: `2`
* `-s`/`--file-size`: size of the file in MB to write to before moving to next file. Default: `1000`
* `-m`/`--max-capacity`: maximum capacity in MB it can write before deleting the files. Default: `10000`
* `-p`/`--delete-percentage`: Percentage of files to delete on reaching max-capacity. Default: `70`

## Examples

* File Mode: 
```podman run --privileged -v /mnt/nfs_mount:/data neerali_iofiller:latest /usr/local/bin/iofiller.sh -s 500 -m 10000```

* Block device mode:
```podman run --privileged neerali_iofiller:latest /usr/local/bin/iofiller.sh -t blk -d /dev/sdf -s 500 -m 10000```
