#!/usr/bin/env bash

declare -a domains=(
	                #"blocks-world"
					## "blocks-world-aaai"
					##"campus"  # no
					#"depots"
					#"driverlog"
					#"dwr"
					#"easy-ipc-grid"
					#"ferry"
					## "hanoi"
					## "hanoi_handmade"
					##"intrusion-detection" # no
					##"kitchen" # nope
					## "lo_handmade"
					## "lodigital"
					#"logistics"
					## "lotwisted"
					## "mandrill"
					#"miconic"
					## "mnist"
					## "mnist_handmade"
					#"rovers"
					#"satellite"
					#"sokoban"
					## "spider"
					#"zeno-travel"
					)

declare -a noisy_domains=(
	                #"blocks-world-noisy"
					##"campus-noisy"
					#"depots-noisy"
					#"driverlog-noisy"
					#"dwr-noisy"
					#"easy-ipc-grid-noisy"
					#"ferry-noisy"
					##"intrusion-detection-noisy"
					##"kitchen-noisy"
					#"logistics-noisy"
					#"miconic-noisy"
					#"rovers-noisy"
					#"satellite-noisy"
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
	python2 run_experiments.py $domain -s #-s #-d -u -n -f -k
	mv *.txt results
	# python2 run_experiments.py $domain -v -c -s -d -u -n
	# python2 run_experiments.py $domain -v
	# mkdir results/h_value
# 	mv *.txt ./results/h_value
#
# 	python2 run_experiments.py $domain -c
# 	mkdir results/h_value_c
# 	mv *.txt ./results/h_value_c
#
# 	python2 run_experiments.py $domain -s
# 	mkdir results/soft_c
# 	mv *.txt ./results/soft_c
#
# 	python2 run_experiments.py $domain -d
# 	mkdir results/delta_h_c
# 	mv *.txt ./results/delta_h_c
done

for domain in "${noisy_domains[@]}"; do
	echo "Running domain ${domain}"
	python2 run_experiments.py $domain  -c #-s #-d -u -n -f -k
	mv *.txt results
done
