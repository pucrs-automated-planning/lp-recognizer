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

if [[ ! -d "fast-downward-original" ]]; then
	hg clone http://hg.fast-downward.org fast-downward-original
else
	pushd fast-downward-original
	hg pull
	hp update
fi

# Generate the patch in the current directory
diff -x builds -x .hg -X fast-downward/.hgignore -ruN fast-downward-original/ fast-downward > fd-patch.diff

mv fd-patch.diff $DIR/

