#!/usr/bin/env bash

declare -a domains=(
					"blocks-world"
					"easy-ipc-grid"
					"logistics"
					"miconic"
					"rovers"
					"satellite"
					"sokoban"
					)

DATASETS=../goal-plan-recognition-dataset

pushd ..

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

for domain in "${domains[@]}"; do
	METHODS="dc dcu dcum w wu"
	run_domain $domain-optimal
	run_domain $domain-suboptimal
	METHODS="dc dcu dcum w wu dc-f1 dcu-f1 dc-f2 dcu-f2"
	run_domain $domain-optimal-noisy
	run_domain $domain-suboptimal-noisy
	run_domain $domain-optimal-old-noisy
	run_domain $domain-suboptimal-old-noisy
done

popd