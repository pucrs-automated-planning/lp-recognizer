#!/usr/bin/env bash

##
## Master script to run tests and generate all .txt and .pdf files for the results.
##

## Uses:
# Run methods and generate new .txt and .pdf files:
# ./get_results.sh -rerun [-fast]
# ./get_results.sh -rerun -comp [-fast]
# Generate .txt tables files from existing .output files:
# ./get_results.sh -txt [-fast]
# Generate .pdf tables from existing .txt files:
# ./get_results.sh -tables [-fast] 
# Generate .txt files and .pdf tables:
# ./get_results.sh -txt -comp [-fast]
# Generate .pdf charts from existing .txt files:
# ./get_results.sh -charts [-fast] 
##

# Default list of domains.
export DOMAINS='
	blocks-world
	depots
	driverlog
	dwr
	easy-ipc-grid
	ferry
	logistics
	miconic
	rovers
	satellite
	sokoban
	zeno-travel'

# Root folder for all domains.
export DATASETS=../goal-plan-recognition-dataset/

# Parse arguments.
for arg in "$@"; do
	if [[ "$arg" == "-fast" ]]; then
		# Use smaller list of domains.
		TEST=-fast
		export DOMAINS='
			blocks-world
			depots
			driverlog
			dwr
			rovers
			sokoban'
	elif [[ "$arg" == "-test" ]]; then
		# Use sample domain.
		TEST=-test
		export DOMAINS=small-sokoban
		export DATASETS=experiments/
	elif [[ "$arg" == "-txt" ]]; then
		# Generate method .txt tables.
		EXP=txt
	elif [[ "$arg" == "-rerun" ]]; then
		# Re-run all experiments.
		EXP=output
	elif [[ "$arg" == "-dd" ]]; then
		# Generate domain .txt tables.
		DD=txt
	elif [[ "$arg" == "-comp" ]]; then
		# Generate .txt tables for pair comparisons.
		COMP=txt
	elif [[ "$arg" == "-tables" ]]; then
		# Generate pdf tables.
		COMP=pdf
	elif [[ "$arg" == "-charts1" ]]; then
		# Generate pdf charts (ref goals).
		CHARTS=-ref
	elif [[ "$arg" == "-charts2" ]]; then
		# Generate pdf charts (nonref goals).
		CHARTS=-nonref
	elif [[ "$arg" == "-charts3" ]]; then
		# Generate pdf charts (all goals).
		CHARTS=-all
	elif [[ "$arg" == "-charts4" ]]; then
		# Generate pdf charts (all goals, sum scatter).
		CHARTS=-sums
	fi
done

# Methods from the First paper.
export BASIC="delta deltau"
export BASIC_N="delta-f1 deltau-f1 delta-f2 deltau-f2"
export CONSTRAINT_PAIRS="delta-cps delta-cls delta-clp deltau-cps deltau-cls deltau-clp"
export CONSTRAINT_SINGLE="delta-cl delta-cp delta-cs deltau-cl deltau-cp deltau-cs"

# Methods from the second paper.
export LMC="delta-cl delta-o-cl delta-o-cl3 delta-o-cl1"
export LMC_N="delta-cl-f2 delta-o-cl-f2 delta-o-cl3-f2 delta-o-cl1-f2 delta-o-cl2-f2"
export DELR="delta-cdt delta-o-cdt delta-o-cdto delta-o-cdto1 delta-o-cdtb1"
export DELR_N="delta-cdt-f2 delta-o-cdt-f2 delta-o-cdto-f2 delta-o-cdto1-f2 delta-o-cdtb1-f2 delta-o-cdta1-f2"
export FLOW="delta-cf1 delta-cf1ab delta-o-cf17 delta-o-cf16 delta-cf2"
export FLOW_N="delta-cf1-f2 delta-cf1ab-f2 delta-o-cf17-f2 delta-o-cf16-f2 delta-cf2-f2"
export NEW_PAIRS="delta-o-csdto delta-o-csl1 delta-o-cl1dto"
export NEW_PAIRS_N="delta-o-csdto-f2 delta-o-csl1-f2 delta-o-cl1dto-f2"

export TEST_METHODS="div-cl div-o-cl div-o-cl3 div-o-cl1"

# Download datasets if necessary.
if [[ ! -d ../$DATASETS ]]; then
	echo "Datasets not found at ../$DATASETS"
	source get_datasets.sh
fi
# Create output folder
if [[ ! -d stdout ]]; then
	mkdir stdout
fi

pushd ..

# Generates result tables for each domain.
# Runs test_domain.py instead if flag -rerun is set.
# Choose the dataset type by providing it as the first argument for get_results.
# Choose the methods by setting the variable METHODS.
# Each method in METHODS should be separated by spaces.
get_results() {
	# $1 = data set type
	# $2 = method list
	for domain in $DOMAINS; do
		echo "Processing domain $domain-$1"
		# Domain .txt tables.
		if [[ "$DD" == "txt" ]]; then
			python3 data_domain.py $domain-$1 $TEST
		fi
		# Method's results.
		if [[ "$EXP" == "output" ]]; then
			# .output files + .txt tables.
			python3 test_domain.py $DATASETS $domain-$1 "$METHODS" $TEST -S cplex > experiments/stdout/$domain-$1.txt
			for filename in hyp_*_problem.log; do
				mv $filename experiments/stdout/$domain-$1-$filename
			done
		elif [[ "$EXP" == "txt" ]]; then
			# .txt tables only.
			python3 data_output.py "$METHODS" $domain-$1 $TEST
		fi
	done
}
echo "Generating results tables..."
if [[ "$TEST" == "-test" ]]; then
	METHODS="$TEST_METHODS"
	get_results optimal
else
	#METHODS="$LMC $DELR $FLOW"
	METHODS="delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5"
	get_results optimal
	get_results suboptimal
	METHODS="delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2"
	get_results optimal-old-noisy
	get_results suboptimal-old-noisy
fi
echo "Done."

if [[ "$COMP" == "txt" ]]; then
	echo "Generating comparison tables..."
	if [[ "$TEST" == "-test" ]]; then
		./data_comparison.py lmc "$TEST_METHODS" optimal $TEST
	else 
		#./data_comparison.py lmc "delta-cl delta-o-cl delta-o-cl1" optimal suboptimal $TEST
		#./data_comparison.py lmcd "div-cl div-o-cl div-o-cl1" optimal suboptimal $TEST
		#./data_comparison.py lmcf2 "delta-cl-f2 delta-o-cl-f2 delta-o-cl3-f2 delta-o-cl1-f2" optimal-old-noisy suboptimal-old-noisy $TEST
		#./data_comparison.py delr "delta-o-cdt delta-o-cdto delta-o-cdtb5" optimal suboptimal $TEST
		#./data_comparison.py delrf2 "delta-o-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2" optimal-old-noisy suboptimal-old-noisy $TEST
		./data_comparison.py lmc "delta-cl delta-o-cl1" optimal suboptimal $TEST
		./data_comparison.py lmcf2 "delta-cl-f2 delta-o-cl1-f2" optimal-old-noisy suboptimal-old-noisy $TEST
		./data_comparison.py delr "delta-cdt delta-o-cdto delta-o-cdtb5 delta-o1-cdtb5" optimal suboptimal $TEST
		./data_comparison.py delrf2 "delta-cdt-f2 delta-o-cdto-f2 delta-o-cdtb5-f2 delta-o1-cdtb5-f2" optimal-old-noisy suboptimal-old-noisy $TEST
		#./data_comparison.py flow "delta-cf1 delta-cf1ab delta-o-cf17 delta-o-cf16 delta-cf2" optimal suboptimal $TEST
		#./data_comparison.py flowf2 "delta-cf1-f2 delta-cf1ab-f2 delta-o-cf17-f2 delta-o-cf16-f2 delta-cf2-f2" optimal-old-noisy suboptimal-old-noisy $TEST
		pushd data-comparison
		# Generate .txt tables for group comparisons.
		merge_comp_files() {
			for d in $3; do
				echo "$2" > "$1-$d.txt"
				for file in $(ls $1-*-$d.txt); do
					echo $file >> "$1-$d.txt"
					echo "$(cat $file)" >> "$1-$d.txt"
				done
			done
		}
		merge_comp_files lmc "L	L+(uni)	L+(soft)" "optimal suboptimal"
		#merge_comp_files lmcd "L	L+(uni)	L+(soft)" 
		merge_comp_files lmcf2 "L	L+(uni)	L+	L+(soft)" "optimal-old-noisy suboptimal-old-noisy"
		merge_comp_files delr "D+	D+2	D+3" "optimal suboptimal"
		merge_comp_files delrf2 "D+	D+2	D+3" "optimal-old-noisy suboptimal-old-noisy"
		#merge_comp_files flow "F	F(M2)	F(PxE-Intra)	F(PxE-Gen)	F2"
		#merge_comp_files flowf2 "F	F(M2)	F(PxE-Intra)	F(PxE-Gen)	F2"
		popd
	fi
	echo "Done."
fi

if [[ "$TEST" != "-test" ]]; then
	# .pdf tables.
	if [[ ! -z "$COMP" ]]; then
		echo "Generating pdf tables..."
		cd latex-tables
		bash generate_all_tables.sh full $TEST
		cd ..
		echo "Done."
	fi
	# .pdf charts.
	if [[ ! -z "$CHARTS" ]]; then
		echo "Generating pdf charts$CHARTS..."
		cd latex-charts
		bash generate_all_charts.sh $CHARTS $TEST
		cd ..
		echo "Done."
	fi
fi

popd
