#!/usr/bin/env bash
DIR=`dirname $0`
if [[ $DIR == "." ]]; then
	DIR=`pwd`
fi

# Verifying paths
pushd ..
	FD_ROOT=`pwd`/fast-downward
	if [[ -z "$DOWNWARD_COIN_ROOT" ]]; then
		export DOWNWARD_COIN_ROOT=`pwd`/coin64
	fi
	if [[ -z "$DOWNWARD_SOPLEX_ROOT" ]]; then
		export DOWNWARD_SOPLEX_ROOT=`pwd`/soplex
	fi
popd

# Check for libs in paths
if [[ ! -d "$DOWNWARD_COIN_ROOT" ]]; then
	if [[ `uname` == "Darwin" ]]; then
		echo "Installing OSI for Mac"
		source install-osi-mac.sh
	elif [[ `uname` == "Linux" ]]; then
		echo "Installing OSI for Linux"
		source install-osi-linux.sh
	else
		echo "Install OSI Manually for Windows"
		#source install-osi-windows.sh
	fi
else
	echo "OSI Present"
fi

FD_REV=`cat fd-patch-rev`
pushd ..
	if [[ ! -d "$FD_ROOT" ]]; then
		echo "Downloading Fast Downward"
		git clone https://github.com/aibasel/downward.git $FD_ROOT
		if [[ ! $? ]]; then echo "Failed to clone fast-downward. Exiting."; exit; fi
	fi

	pushd $FD_ROOT
		echo "Fast Downward Present"
		git checkout $FD_REV
	popd

	echo "Patching Fast Downward"
	patch -s -p0 -i ${DIR}/fd-patch.diff 

	pushd $FD_ROOT
		./build.py release
		chmod u+x fast-downward
	popd
popd