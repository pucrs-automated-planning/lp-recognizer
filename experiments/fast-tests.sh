#!/usr/bin/env bash

declare -a domains=(
					"blocks-world"
					"depots"
					"driverlog"
					"dwr"
					"rovers"
					"sokoban"
					)

DATASETS=../goal-plan-recognition-dataset
BASIC="delta deltau"
CONSTRAINT_PAIRS="delta-cps delta-cls delta-clp deltau-cps deltau-cls deltau-clp"
CONSTRAINT_SINGLE="delta-cl delta-cp delta-cs deltau-cl deltau-cp deltau-cs"
CONSTRAINT_NEW="delta-cd delta-o-cd delta-o-cl delta-cf1 delta-cf2"
FILTERS="delta-f1 deltau-f1 delta-f2 deltau-f2"

if [[ ! -d ../$DATASETS ]]; then
	source get-all-experiments.sh
fi

pushd ..

if [[ ! -d results ]]; then
	mkdir results
fi

run_domain() {
	echo "Running domain $1"
	python2 test_domain.py $DATASETS $1 "$METHODS" -fast -S cplex > experiments/$1.output
}


for domain in "${domains[@]}"; do
	METHODS="delta-cf1ab delta-cf1bb delta-cf1cb delta-cf1db" # Default partial merge
	#METHODS="delta-cf1f3 delta-cf1f4 delta-cf1f5" # All pairs in pre/eff of all operators (intra-op)
	#METHODS="delta-o-cf1 delta-o-cf11 delta-o-cf12" # All pairs in pre/eff for observations (inter-op)
	#METHODS="delta-o-cf13 delta-o-cf14 delta-o-cf15" # All pairs in pre/eff for observations (intra-op)
	METHODS="delta-cf1f3"
	run_domain $domain-optimal
	#run_domain $domain-suboptimal
	#METHODS="$BASIC $FILTERS"
	#run_domain $domain-optimal-old-noisy
	#run_domain $domain-suboptimal-old-noisy
done

popd
