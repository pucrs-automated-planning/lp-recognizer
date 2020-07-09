#!/usr/bin/env bash
DIR=`dirname $0`
if [[ $DIR == "." ]]; then
	DIR=`pwd`
fi
# echo "Running from ${DIR}"
pushd ..
if [[ ! -d "$DOWNWARD_COIN_ROOT" ]]; then
	export DOWNWARD_COIN_ROOT=`pwd`/coin64
fi
if [[ ! -d "$FD_ROOT" ]]; then
	export FD_ROOT=`pwd`/fast-downward
fi
popd
if [[ ! -d "$DOWNWARD_COIN_ROOT" ]]; then
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
fi

pushd $FD_ROOT
echo "Fast Downward Present"
hg update -r $(cat fd-patch-rev)
if [[ ! $? ]]; then echo "Failed to update fast-downward. Exiting."; exit; fi
popd

echo "Patching Fast Downward at `pwd`"
cp ${DIR}/fd-patch.diff .
patch -s -p0 -i fd-patch.diff 
rm fd-patch.diff
pushd fast-downward
./build.py release
chmod u+x fast-downward