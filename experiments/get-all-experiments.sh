#!/usr/bin/env bash
#  Downloads all experiments from our group's repository
#  get-all-experiments.sh
#  lp-recognizer
#
#  Created by Felipe Meneguzzi on 2019-08-28.
#  Copyright 2019 Felipe Meneguzzi. All rights reserved.
#

EXPERIMENTS_REPO="https://github.com/pucrs-automated-planning/goal-plan-recognition-dataset.git"

declare -a domains=("blocks-world"
					# "blocks-world-aaai"
					"campus"
					"depots"
					"driverlog"
					"dwr"
					"dwr"
					"easy-ipc-grid"
					"ferry"
					# "hanoi"
					# "hanoi_handmade"
					"intrusion-detection"
					"kitchen"
					# "lo_handmade"
					# "lodigital"
					"logistics"
					# "lotwisted"
					# "mandrill"
					"miconic"
					# "mnist"
					# "mnist_handmade"
					"rovers"
					"satellite"
					"sokoban"
					# "spider"
					"zeno-travel"
					)

declare -a noisy_domains=("blocks-world-noisy"
					"campus-noisy"
					"depots-noisy"
					"driverlog-noisy"
					"dwr-noisy"
					"easy-ipc-grid-noisy"
					"ferry-noisy"
					"intrusion-detection-noisy"
					"kitchen-noisy"
					"logistics-noisy"
					"miconic-noisy"
					"rovers-noisy"
					"satellite-noisy"
					"sokoban-noisy"
					"zeno-travel-noisy"
					)

pushd ../../

git clone --depth=1 $EXPERIMENTS_REPO goal-plan-recognition-dataset

popd

# pushd experiments

echo "Preparing regular experiments"

for domain in "${domains[@]}"; do
	echo $domain
	rm -rf $domain
	cp -R "../../goal-plan-recognition-dataset/$domain" .
done

echo -e "\nPreparing noisy experiments"

for domain in "${noisy_domains[@]}"; do
	echo $domain
	rm -rf $domain
	cp -R "../../goal-plan-recognition-dataset/$domain" .
done