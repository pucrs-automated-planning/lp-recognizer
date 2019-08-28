#!/usr/bin/env bash

EXPERIMENTS_REPO="https://github.com/pucrs-automated-planning/Planning-PlanRecognition-Experiments.git"

declare -a domains=("blocks-world"
					"blocks-world-aaai"
					"campus"
					"depots"
					"driverlog"
					"dwr"
					"dwr"
					"easy-ipc-grid"
					"ferry"
					"hanoi"
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
					#"logistics"
					"miconic-noisy"
					"rovers-noisy"
					"satellite-noisy"
					"sokoban-noisy"
					"zeno-travel-noisy"
					)

pushd ../../

git clone --depth=1 $EXPERIMENTS_REPO plan-recognition-experiments

popd

pushd experiments

echo "Preparing regular experiments"

for domain in "${domains[@]}"; do
	echo $domain
	rm -rf $domain
	cp -R "../../plan-recognition-experiments/experiments/$domain" .
	if [ $domain = "blocks-world" ] || [ $domain = "blocks-world-aaai" ]; then
		pushd $domain
		bash ../patch-blocks-world.sh
		popd
	fi
	if [ $domain = "kitchen" ]; then
		pushd $domain
		bash ../patch-kitchen.sh
		popd
	fi
	bash prepare-domain.sh $domain
done

echo "Preparing noisy experiments"

for domain in "${noisy_domains[@]}"; do
	echo $domain
	rm -rf $domain
	cp -R "../../plan-recognition-experiments/experiments/$domain" .
done