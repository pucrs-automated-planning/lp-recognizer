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
pushd ../fast-downward
# Capture the revision from which we are generating the diff
FD_REV=`hg id -n`
FD_REV=${FD_REV::-1} #Strip the + at the end
echo "Making patch from revision ${FD_REV}"
echo $FD_REV > $DIR/fd-patch-rev
pushd ..

if [[ ! -d "fast-downward-original" ]]; then
	hg clone http://hg.fast-downward.org fast-downward-original
fi

#Ensure we are comparing with the right revision
pushd fast-downward-original
hg pull
hg update -r $FD_REV
popd
# Generate the patch in the current directory
# diff -x builds -X fast-downward/.hgignore -x .hg* -ruN fast-downward-original/ fast-downward > fd-patch.diff
diff -X lp-recognizer/fd-patch.ignore -ruN fast-downward-original/ fast-downward/ > fd-patch.diff

mv fd-patch.diff $DIR/

