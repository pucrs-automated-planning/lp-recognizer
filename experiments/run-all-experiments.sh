#!/usr/bin/env bash

declare -a optimal_domains=("blocks-world-optimal"
					#"campus-optimal"
					#"depots-optimal"
					#"driverlog-optimal"
					#"dwr-optimal"
					"easy-ipc-grid-optimal"
					#"ferry-optimal"
					#"intrusion-detection-optimal"
					#"kitchen-optimal"
					"logistics-optimal"
					#"miconic-optimal"
					#"rovers-optimal"
					#"satellite-optimal"
					"sokoban-optimal"
					#"zeno-travel-optimal"
					)

declare -a suboptimal_domains=("blocks-world-suboptimal"
					#"campus-suboptimal"
					#"depots-suboptimal"
					#"driverlog-suboptimal"
					#"dwr-suboptimal"
					"easy-ipc-grid-suboptimal"
					#"ferry-suboptimal"
					#"intrusion-detection-suboptimal"
					#"kitchen-suboptimal"
					"logistics-suboptimal"
					#"miconic-suboptimal"
					#"rovers-suboptimal"
					#"satellite-suboptimal"
					"sokoban-suboptimal"
					#"zeno-travel-suboptimal"
					)

declare -a noisy_domains=("blocks-world-noisy"
					#"campus-noisy"
					#"depots-noisy"
					#"driverlog-noisy"
					#"dwr-noisy"
					"easy-ipc-grid-noisy"
					#"ferry-noisy"
					#"intrusion-detection-noisy"
					#"kitchen-noisy"
					"logistics-noisy"
					#"miconic-noisy"
					#"rovers-noisy"
					#"satellite-noisy"
					"sokoban-noisy"
					#"zeno-travel-noisy"
					)

DATASETS=../goal-plan-recognition-dataset
METHODS="dcu-cps dcu-cls dcu-clp"

if [[ ! -d ../$DATASETS ]]; then
	source get-all-experiments.sh
fi

pushd ..

if [[ ! -d results ]]; then
	mkdir results
fi

for domain in "${optimal_domains[@]}"; do
	echo "Running domain ${domain}"
	python2 test_domain.py $DATASETS $domain $METHODS > experiments/$domain.output
done
#for domain in "${suboptimal_domains[@]}"; do#
#	echo "Running domain ${domain}"
#	python2 test_domain.py $DATASETS $domain $METHODS > experiments/$domain.output
#done
#for domain in "${noisy_domains[@]}"; do
#	echo "Running domain ${domain}"
#	python2 test_domain.py $DATASETS $domain $METHODS > experiments/$domain.output
#done

mv *.txt results

popd