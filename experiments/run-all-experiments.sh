#!/usr/bin/env bash

declare -a domains=("blocks-world" 
				# 	"blocks-world-aaai"
				# 	"campus"
				# 	"campus-noisy"
				# 	"depots"
				# 	"driverlog"
				# 	"dwr"
				# 	"dwr"
				# 	"easy-ipc-grid"
				# 	"easy-ipc-grid-noisy"
				# 	"ferry"
				# 	"hanoi"
				# 	"intrusion-detection"
				# 	"intrusion-detection-noisy"
				# 	"kitchen"
				# 	"kitchen-noisy"
				# 	"logistics"
				# 	"miconic"
				# 	"rovers"
				# 	"satellite"
				# 	"sokoban"
				# "zeno-travel"
			)
pushd ..
# echo "$domains"
for domain in "${domains[@]}"; do
	echo "Running domain ${domain}"
	python2 run_experiments.py $domain
	slack_message "Finished running $domain at `hostname`"
done

if [[ ! -d results ]]; then
	mkdir results
fi
mv *.txt ./results