#!/bin/bash
set -euo pipefail

LONGOPTS=fio-file:,block-device:,time-to-run:,num-jobs:,dev-type:,file-size:,iodepth:,format:,rw:,bs:
OPTIONS=f:b:t:n:d:s

format=json
fio_file="null"
fio_file_dir="/fio_files"
devtype=fs
filesize="1G"
numjobs=1
timetorun=0
iodepth=128
bs=4k
rw=randwrite
device=""

_args=$(getopt --options=${OPTIONS} --longoptions=${LONGOPTS} --name "$@" -- "$@")
while [ "$#" -gt 0 ]; do
  case "$1" in
    -f|--fio-file)
	      fio_file=$2
	      shift 2
        ;;
    -b|--block-device)
        device=$2
        shift 2
        ;;
    -t|--time-to-run)
        timetorun=$2
        shift 2
        ;;
    -n|--num-jobs)
        numjobs=$2
        shift 2
        ;;
    --format)
        format=$2
        shift 2
	      ;;
    -d|--dev-type)
        devtype=$2
        shift 2
        ;;
    -s|--file-size)
        filesize=$2
        shift 2
        ;;
    --iodepth)
        iodepth=$2
        shift 2
        ;;
    --bs)
        bs=$2
        shift 2
        ;;
    --rw)
        rw=$2
        shift 2
          ;;
    --)
        shift 2
        break
        ;;
    *)
        echo "Unknown option"
        exit 3
  esac
done

FIO_CMD="fio"

FIO_ARGS="--group_reporting --direct=1 --ioengine=libaio"

if [[ $timetorun -gt 0 ]]; then
    FIO_ARGS="$FIO_ARGS --time_based --runtime=$timetorun"
fi
if [[ ${fio_file} != "null" ]]; then
    FIO_ARGS="${fio_file_dir}/${fio_file}"
elif [[ ${devtype} == "blk" ]]; then
    FIO_ARGS="$FIO_ARGS --name=neerali_${devtype}_test --filename=$device --rw=$rw --bs=$bs --numjobs=$numjobs --iodepth=$iodepth"
elif [[ ${devtype} == "fs" ]]; then
    FIO_ARGS="$FIO_ARGS --name==neerali_${devtype}_test --directory=/data --rw=$rw --bs=$bs --size=$filesize --numjobs=$numjobs --iodepth=$iodepth"
else
    echo "Invalid Arguments"
    exit 1
fi

$FIO_CMD $FIO_ARGS --output-format=$format
