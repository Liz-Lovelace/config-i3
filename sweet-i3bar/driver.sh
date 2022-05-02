#!/bin/sh

full_path=$(realpath $0) 
dir_path=$(dirname $full_path)

echo '{ "version": 1 }'
echo '['
echo '[]'
while :;
do
	echo "$(python3 $dir_path/sweet-i3bar.py)"
	sleep 1
done