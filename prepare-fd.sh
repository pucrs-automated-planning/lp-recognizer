#!/usr/bin/env bash
DIR=`dirname $0`
if [[ $DIR == "." ]]; then
	DIR=`pwd`
fi

if [[ ! -d "data-domains" ]]; then
	mkdir data-domains
fi

if [[ ! -d "data-charts" ]]; then
	mkdir data-charts
fi

if [[ ! -d "data-tables" ]]; then
	mkdir data-tables
fi

if [[ ! -d "data-comparison" ]]; then
	mkdir data-comparison
fi

if [[ ! -d "outputs" ]]; then
	mkdir outputs
fi

FD_REV=`cat fd-patch-rev`

pushd ..
	# Set soplex path
	if [[ -z "$soplex_DIR" ]]; then
		#export soplex_DIR=/opt/soplex-6.0.4x
		export soplex_DIR=`pwd`/soplex
		echo "soplex_DIR=\"${soplex_DIR}\"" >> ~/.profile
	fi
	# Check for soplex in path
	if [[ ! -d "$soplex_DIR" ]]; then
		git clone https://github.com/scipopt/soplex.git
		export CXXFLAGS="$CXXFLAGS -Wno-use-after-free" # Ignore compiler warnings about use-after-free
		cmake -S soplex -B build
		cmake --build build
		cmake --install build --prefix $soplex_DIR
		rm -rf soplex build
	else
		echo "Soplex Present"
	fi

	# Check for fast-downward
	FD_ROOT=`pwd`/fast-downward
	if [[ ! -d "$FD_ROOT" ]]; then
		echo "Downloading Fast Downward"
		git clone https://github.com/aibasel/downward.git $FD_ROOT
		if [[ ! $? ]]; then echo "Failed to clone fast-downward. Exiting."; exit; fi
	else
		echo "Fast Downward Present"
	fi

	# Change fast-downard branch
	pushd $FD_ROOT
		git reset --hard
		git clean -fd .
		git checkout $FD_REV
	popd
	# Apply lp-recognizer's changes
	echo "Patching Fast Downward"
	patch -s -p0 -i ${DIR}/fd-patch.diff 
	# Build fast-downward
	pushd $FD_ROOT/
		./build.py release
	popd
popd