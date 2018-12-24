#!/usr/bin/env bash
DIR=`dirname $0`
DOWNWARD_COIN_ROOT64=`pwd`/../coin64 
if [[ ! -d "$DOWNWARD_COIN_ROOT64"]]; then
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
	echo "OSI Installed"
fi
pushd ..
echo "Downloading Fast Downward"
hg clone http://hg.fast-downward.org fast-downward
pushd fast-downward
echo "Patching Fast Downward"
patch -s -p0 < ${DIR}/fd-patch.diff 
./build.py release64