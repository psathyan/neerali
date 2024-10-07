#!/bin/bash
set -euo pipefail

LONGOPTS=block-device:,time-to-run:,num-jobs:,dev-type,file-size
OPTIONS=b:t:n:d:s

devtype=fs
filesize="1G"
numjobs=1
timetorun=0
device=""

_args=$(getopt --options=${OPTIONS} --longoptions=${LONGOPTS} --name "$@" -- "$@")
while [ "$#" -gt 0 ]; do
  case "$1" in
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
	-d|--dev-type)
      devtype=$2
      shift 2
      ;;
	-s|--file-size)
	  filesize=$2
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
if [[ ${devtype} == "blk" ]]; then
	FIO_ARGS="$FIO_ARGS --name=seq_write_test --filename=$device --rw=write --bs=1M --numjobs=$numjobs"
elif [[ ${devtype} == "fs" ]]; then
	FIO_ARGS="$FIO_ARGS --name=nfs_test --directory=/data --rw=randwrite --bs=4k --size=$filesize --numjobs=$numjobs"
else 
	echo "Invalid Arguments"
	exit 1
fi

echo Running: $FIO_CMD $FIO_ARGS

$FIO_CMD $FIO_ARGS
