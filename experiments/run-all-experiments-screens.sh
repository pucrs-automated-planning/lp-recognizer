#!/usr/bin/env bash

declare -a optimal_domains=(
					"blocks-world-optimal"
					#"depots-optimal"
					#"driverlog-optimal"
					#"dwr-optimal"
					"easy-ipc-grid-optimal"
					#"ferry-optimal"
					"logistics-optimal"
					"miconic-optimal"
					"rovers-optimal"
					#"satellite-optimal"
					"sokoban-optimal"
					#"zeno-travel-optimal"
					)

declare -a suboptimal_domains=(
					"blocks-world-suboptimal"
					#"depots-suboptimal"
					#"driverlog-suboptimal"
					#"dwr-suboptimal"
					"easy-ipc-grid-suboptimal"
					#"ferry-suboptimal"
					"logistics-suboptimal"
					"miconic-suboptimal"
					"rovers-suboptimal"
					#"satellite-suboptimal"
					"sokoban-suboptimal"
					#"zeno-travel-suboptimal"
					)

declare -a noisy_optimal_domains=(
					"blocks-world-optimal-noisy"
					#"depots-optimal-noisy"
					#"driverlog-optimal-noisy"
					#"dwr-optimal-noisy"
					"easy-ipc-grid-optimal-noisy"
					#"ferry-optimal-noisy"
					"logistics-optimal-noisy"
					"miconic-optimal-noisy"
					"rovers-optimal-noisy"
					#"satellite-optimal-noisy"
					"sokoban-optimal-noisy"
					#"zeno-travel-optimal-noisy"
					)

declare -a noisy_suboptimal_domains=(
					"blocks-world-suboptimal-noisy"
					#"depots-suboptimal-noisy"
					#"driverlog-suboptimal-noisy"
					#"dwr-suboptimal-noisy"
					"easy-ipc-grid-suboptimal-noisy"
					#"ferry-suboptimal-noisy"
					"logistics-suboptimal-noisy"
					"miconic-suboptimal-noisy"
					"rovers-suboptimal-noisy"
					#"satellite-suboptimal-noisy"
					"sokoban-suboptimal-noisy"
					#"zeno-travel-suboptimal-noisy"
					)

DATASETS=../goal-plan-recognition-dataset
METHODS="dc dcu w wu"

pushd ..
# echo "$domains"
if [[ ! -d results ]]; then
	mkdir results
fi

run_domain() {
	domain=$1
	echo "Copying domain ${domain}"
	mkdir ../lp-recognizer-$domain
	cp -R ../lp-recognizer/*.py ../lp-recognizer-$domain
	pushd ../lp-recognizer-$domain
	echo "Running domain ${domain} at `pwd`"
	screen -S $domain -dm bash -c "python2 test_domain.py $DATASETS $domain $METHODS"
	popd
}

for domain in "${optimal_domains[@]}"; do
	run_domain $domain
done
for domain in "${suboptimal_domains[@]}"; do
	run_domain $domain
done
METHODS="dc dcu w wu dc-f1 dcu-f1 dc-f2 dcu-f2"
for domain in "${noisy_optimal_domains[@]}"; do
	run_domain $domain
done
for domain in "${noisy_suboptimal_domains[@]}"; do
	run_domain $domain
done

popd