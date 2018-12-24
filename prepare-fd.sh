#!/usr/bin/env bash
DIR=`dirname $0`

if [[ `uname` == "Darwin" ]]
then
	echo "Installing OSI for Mac"
	source install-osi-mac.sh
elif [[ `uname` == "Linux" ]]
then
	echo "Installing OSI for Linux"
	source install-osi-linux.sh
else
	echo "Install OSI Manually for Windows"
fi
pushd ..
echo "Downloading Fast Downward"
hg clone http://hg.fast-downward.org fast-downward
pushd fast-downward
patch -s -p0 < ${DIR}/file.patch 
./build.py release64