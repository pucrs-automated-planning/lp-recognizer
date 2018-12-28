#!/usr/bin/env bash

echo "Preparing dataset for $1"
pushd $1
for obs in 10 30 50 70 100; do
	mkdir $obs
	if [ $obs == 100 ]; then
		suffix="_full"
	else
		suffix="_${obs}_"
	fi
	mv *$suffix* ./${obs}
done 
echo "Done"
