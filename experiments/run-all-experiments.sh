#!/usr/bin/env bash

declare -a domains=(
					"blocks-world"
					"depots"
					"driverlog"
					"dwr"
					"easy-ipc-grid"
					"ferry"
					"logistics"
					"miconic"
					"rovers"
					"satellite"
					"sokoban"
					"zeno-travel"
					)

DATASETS=../goal-plan-recognition-dataset
BASIC="delta deltau"
CONSTRAINT_PAIRS="delta-cps delta-cls delta-clp deltau-cps deltau-cls deltau-clp"
CONSTRAINT_SINGLE="delta-cl delta-cp delta-cs deltau-cl deltau-cp deltau-cs"
CONSTRAINT_NEW="delta-cd delta-o-cd delta-o-cl delta-cf1 delta-cf2"
FILTERS="delta-f1 deltau-f1 delta-f2 deltau-f2"

if [[ ! -d ../$DATASETS ]]; then
	echo "Datasets not found at ../$DATASETS"
	source get-all-experiments.sh
fi

pushd ..

if [[ ! -d results ]]; then
	mkdir results
fi

run_domain() {
	echo "Running domain $1"
	python2 test_domain.py $DATASETS $1 "$METHODS" -S soplex > experiments/$1.output
}

for domain in "${domains[@]}"; do
	METHODS="$BASIC"
	run_domain $domain-optimal
	run_domain $domain-suboptimal
	METHODS="$BASIC $FILTERS"
	run_domain $domain-optimal-old-noisy
	run_domain $domain-suboptimal-old-noisy
done

popd
