#!/usr/bin/env bash

#
#  make-fd-patch.sh
#  lp-recognizer
#  Creates/Updates a patch for our hacked version of Fast Downward
#
#  Created by Felipe Meneguzzi on 2018-12-24.
#  Copyright 2018 Felipe Meneguzzi. All rights reserved.
#

# Download the vanilla version of FD
DIR=`pwd`
pushd ..
	FD_ROOT=`pwd`/fast-downward

	pushd $FD_ROOT
		# Capture the revision from which we are generating the diff
		FD_REV=`git rev-parse HEAD`
		echo "Making patch from revision ${FD_REV}"
		echo $FD_REV > $DIR/fd-patch-rev
	popd

	if [[ ! -d "fast-downward-original" ]]; then
		git clone https://github.com/aibasel/downward.git fast-downward-original
	fi

	#Ensure we are comparing with the right revision
	pushd fast-downward-original
		git pull
		git checkout $FD_REV
	popd

	# Generate the patch in the current directory
	diff -X lp-recognizer/fd-patch.ignore -ruN fast-downward-original/ fast-downward/ > $DIR/fd-patch.diff
popd