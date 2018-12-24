#!/usr/bin/env bash
DIR=`dirname $0`
echo "Running from ${DIR}"
pushd ..
DOWNWARD_COIN_ROOT64=`pwd`/coin64 
FD_ROOT=`pwd`/fast-downward
if [[ ! -d "$DOWNWARD_COIN_ROOT64" ]]; then
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
else
	echo "OSI Present"
fi

if [[ ! -d "$FD_ROOT" ]]; then
	echo "Downloading Fast Downward"
	hg clone http://hg.fast-downward.org fast-downward
else
	echo "Fast Downward Present"
fi
pushd fast-downward
echo "Patching Fast Downward"
patch -s -p0 < ${DIR}/fd-patch.diff 
./build.py release64