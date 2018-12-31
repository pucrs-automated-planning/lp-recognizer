#!/usr/bin/env bash
#
#  Patches the blocks world domains in the experiments 
# so that they can be parsed by Fast Downward
#  patch-blocks-world.sh
#  Planning-PlanRecognition-Experiments
#
#  Created by Felipe Meneguzzi on 2018-12-27.
#  Copyright 2018 Felipe Meneguzzi. All rights reserved.
#

echo -n "Fixing domain.pddl in all experiments. Please wait. "
for FILE in *.tar.bz2; do
	FOLDER=${FILE::-8}
	# echo $FOLDER
	mkdir $FOLDER
	tar -jxf $FILE -C $FOLDER
	pushd $FOLDER
	# echo "Editing $FOLDER"
	sed -i .orig 's/-block/- block/g' domain.pddl
	rm domain.pddl.orig
	tar -jcf ../$FILE .
 	popd
	rm -rf $FOLDER
done
echo "Done"