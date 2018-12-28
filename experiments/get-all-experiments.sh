#!/usr/bin/env bash

EXPERIMENTS_REPO="https://github.com/pucrs-automated-planning/Planning-PlanRecognition-Experiments.git"

declare -a domains=("blocks-world"
					"blocks-world-aaai"
					"campus"
					"campus-noisy"
					"depots"
					"driverlog"
					"dwr"
					"dwr"
					"easy-ipc-grid"
					"easy-ipc-grid-noisy"
					"ferry"
					"hanoi"
					# "hanoi_handmade"
					"intrusion-detection"
					"intrusion-detection-noisy"
					"kitchen"
					"kitchen-noisy"
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

pushd ../../

git clone --depth=1 $EXPERIMENTS_REPO plan-recognition-experiments

popd

pushd experiments

for $domain in domains; do
	cp "../../plan-recognition-experiments/experiments/$domain/*.tar.bz2" .
	bash prepare-domain.sh $domain
done
