#!/usr/bin/env bash

declare -a optimal_domains=("blocks-world-optimal"
					"depots-optimal"
					"driverlog-optimal"
					"dwr-optimal"
					"easy-ipc-grid-optimal"
					"ferry-optimal"
					"logistics-optimal"
					"miconic-optimal"
					"rovers-optimal"
					"satellite-optimal"
					"sokoban-optimal"
					"zeno-travel-optimal"
					)

declare -a suboptimal_domains=("blocks-world-suboptimal"
					"depots-suboptimal"
					"driverlog-suboptimal"
					"dwr-suboptimal"
					"easy-ipc-grid-suboptimal"
					"ferry-suboptimal"
					"logistics-suboptimal"
					"miconic-suboptimal"
					"rovers-suboptimal"
					"satellite-suboptimal"
					"sokoban-suboptimal"
					"zeno-travel-suboptimal"
					)

declare -a noisy_domains=("blocks-world-noisy"
					"depots-noisy"
					"driverlog-noisy"
					"dwr-noisy"
					"easy-ipc-grid-noisy"
					"ferry-noisy"
					"logistics-noisy"
					"miconic-noisy"
					"rovers-noisy"
					"satellite-noisy"
					"sokoban-noisy"
					"zeno-travel-noisy"
					)

DATASETS=../goal-plan-recognition-dataset
METHODS="dc dcu"
CONSTRAINT_PAIRS="dcu-cps dcu-cls dcu-clp"
CONSTRAINT_SINGLE="dcu-cl dcu-cp dcu-cs"
FILTERS="dc-f1 dcu-f1 dc-f2 dcu-f2"
WEIGHTED="w wu wdc wdcu"

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
for domain in "${suboptimal_domains[@]}"; do#
	echo "Running domain ${domain}"
	python2 test_domain.py $DATASETS $domain $METHODS > experiments/$domain.output
done
#for domain in "${noisy_domains[@]}"; do
#	echo "Running domain ${domain}"
#	python2 test_domain.py $DATASETS $domain $METHODS > experiments/$domain.output
#done

mv *.txt results

popd