#!/usr/bin/env bash
DIR=`dirname $0`
if [[ $DIR == "." ]]; then
	DIR=`pwd`
fi

if [[ ! -d "data-charts" ]]; then
	mkdir data-charts
fi

if [[ ! -d "data-latex" ]]; then
	mkdir data-latex
fi

if [[ ! -d "outputs" ]]; then
	mkdir outputs
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
	if [[ -z "$DOWNWARD_CPLEX_ROOT" ]]; then
		if [[ `uname` == "Darwin" ]]; then
			export DOWNWARD_CPLEX_ROOT=/Applications/CPLEX_Studio129/cplex
		elif [[ `uname` == "Linux" ]]; then
			export DOWNWARD_CPLEX_ROOT=/opt/ibm/ILOG/CPLEX_Studio129/cplex
		else
			export DOWNWARD_CPLEX_ROOT=C:/Program\ Files/IBM/ILOG/CPLEX_Studio129/cplex
		fi
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
		git reset --hard
		git clean -fd .
		git checkout $FD_REV
	popd

	echo "Patching Fast Downward"
	patch -s -p0 -i ${DIR}/fd-patch.diff 

	pushd $FD_ROOT
		./build.py release
		cp $DIR/fast-downward .
		chmod u+x fast-downward
	popd
popd