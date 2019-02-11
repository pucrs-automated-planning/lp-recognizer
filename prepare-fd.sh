#!/usr/bin/env bash
DIR=`dirname $0`
if [[ $DIR == "." ]]; then
	DIR=`pwd`
fi
# echo "Running from ${DIR}"
pushd ..
DOWNWARD_COIN_ROOT64=`pwd`/coin64 
FD_ROOT=`pwd`/fast-downward
popd
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
FD_REV=`cat fd-patch-rev`
pushd ..
if [[ ! -d "$FD_ROOT" ]]; then
	echo "Downloading Fast Downward"
	hg clone -r $FD_REV http://hg.fast-downward.org fast-downward
	if [[ ! $? ]]; then echo "Failed to clone fast-downward. Exiting."; exit; fi
else
	pushd $FD_ROOT
	echo "Fast Downward Present"
	hg update -r $FD_REV
	if [[ ! $? ]]; then echo "Failed to update fast-downward. Exiting."; exit; fi
	popd
fi
echo "Patching Fast Downward at `pwd`"
cp ${DIR}/fd-patch.diff .
patch -s -p0 -i fd-patch.diff 
rm fd-patch.diff
pushd fast-downward
./build.py release64
chmod u+x fast-downward