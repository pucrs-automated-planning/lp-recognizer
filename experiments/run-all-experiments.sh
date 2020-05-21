#!/usr/bin/env bash

declare -a domains=("blocks-world"
					"campus"
					"depots"
					"driverlog"
					"dwr"
					"easy-ipc-grid"
					"ferry"
					"intrusion-detection"
					"kitchen"
					"logistics"
					"miconic"
					"rovers"
					"satellite"
					"sokoban"
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

pushd ..
# echo "$domains"
if [[ ! -d results ]]; then
	mkdir results
fi

for domain in "${domains[@]}"; do
	echo "Running domain ${domain}"
	python2 run_experiments.py $domain -d -n > experiments/$domain.output
	mv *.txt results
done

for domain in "${noisy_domains[@]}"; do
	echo "Running domain ${domain}"
	python2 run_experiments.py $domain -d -n > experiments/$domain.output
	mv *.txt results
done