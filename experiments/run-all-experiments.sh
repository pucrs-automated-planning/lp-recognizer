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
BASIC="dc dcu dcum"
CONSTRAINT_PAIRS="dcu-cps dcu-cls dcu-clp"
CONSTRAINT_SINGLE="dcu-cl dcu-cp dcu-cs"
FILTERS="dc-f1 dcu-f1 dc-f2 dcu-f2"
WEIGHTED="w wu"

if [[ ! -d ../$DATASETS ]]; then
	source get-all-experiments.sh
fi

pushd ..

if [[ ! -d results ]]; then
	mkdir results
fi

run_domain() {
	domain=$1
	echo "Running domain ${domain}"
	python2 test_domain.py $DATASETS $domain $METHODS > experiments/$domain.output
}

for domain in "${domains[@]}"; do
	METHODS=$BASIC
	run_domain $domain-optimal
	run_domain $domain-suboptimal
	METHODS="${BASIC} ${FILTERS}" 
	run_domain $domain-optimal-noisy
	run_domain $domain-suboptimal-noisy
	run_domain $domain-optimal-old-noisy
	run_domain $domain-suboptimal-old-noisy
done

popd

