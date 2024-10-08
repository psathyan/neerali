#!/bin/bash
set -euo pipefail

LONGOPTS=io-type:,device:,interval:,max-capacity,file-size
OPTIONS=t:d:i:m:s

io_type=fs
filesize="1000"
interval=2
max_capacity="10000"
percentage=7

_args=$(getopt --options=${OPTIONS} --longoptions=${LONGOPTS} --name "$@" -- "$@")
while [ "$#" -gt 0 ]; do
  case "$1" in
    -t|--io-type)
        io_type=$2
        shift 2
        ;;
	-d|--device)
	    blk_device=$2
	    shift 2
	    ;;
    -i|--interval)
        interval=$2
        shift 2
        ;;
	-m|--max-capacity)
        numjobs=$2
        shift 2
        ;;
	-s|--file-size)
	    filesize=$2
	    shift 2
	    ;;
	-p|--delete-percentage)
		delete_percentage=$2
	    percentage=`expr ${delete_percentage} / 10`
	    shift 2
	   ;;
    --)
	   shift 2
       break
       ;;
	*)
	  echo " Usage:"
	  echo "	$0 -t fs -s <file_size_in_MB> -s <size_in_MB> [-p num]"
	  echo " where:"
	  echo "    -t | --io-type: Type of device ie., file or block device. valid options are 'fs' or 'blk'. Default: fs"
	  echo "	-i | --interval: Time in seconds to sleep before moving to next file. Default: 2"
	  echo "	-s | --file-size: size of the file in MB to write to before moving to next file. Default: 1000"
	  echo "    -m | --max-capacity: maximum capacity in MB it can write before deleting the files. Default: 10000"
	  echo "    -p | --delete-percentage: Percentage of files to delete on reaching max-capacity. Default: 70"
      exit 3
  esac
done

working_dir="/data"
filename="datafile"

# Format and mount if block device is supplied

if [[ $io_type != "fs" ]]; then
	mkdir /data
	mkfs.xfs -f $blk_device
	mount $blk_device $working_dir
fi 

COUNT=0
cd $working_dir

while true; do
	COUNT=`expr $COUNT + 1`
	echo "creating $filename$COUNT of ${filesize}MB"
	dd if=/dev/random of=$working_dir/$filename$COUNT bs=1M count=$filesize status=progress > /dev/null 2>&1
	
	USAGE=`du -csh $working_dir --block-size=1M  | grep total |  awk '{print $1}'`
	
	if [ $USAGE -gt $max_capacity ]; then
		to_delete=`expr \`ls -1 ${working_dir}/${filename}* | wc -l\` \* ${percentage} / 10`
		echo "reached max-capacity: ${max_capacity}MB. Deleting ${to_delete} files..."
		delete_count=0
		for file in `ls -1tr $working_dir/$filename*`; do
			delete_count=`expr $delete_count + 1`
			if [ $delete_count -gt $to_delete ]; then
				break
			fi
			rm -f $file
		done
	fi
	sleep $interval
done
