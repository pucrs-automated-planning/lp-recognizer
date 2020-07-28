#!/usr/bin/env zsh

# declare -a domains=("blocks-world"
# 					)
#
# declare -a noisy_domains=("blocks-world-noisy"
# 					)

declare -a optimal_domains=("blocks-world-optimal"
					"campus-optimal"
					"depots-optimal"
					"driverlog-optimal"
					"dwr-optimal"
					"easy-ipc-grid-optimal"
					"ferry-optimal"
					"intrusion-detection-optimal"
					"kitchen-optimal"
					"logistics-optimal"
					"miconic-optimal"
					"rovers-optimal"
					"satellite-optimal"
					"sokoban-optimal"
					"zeno-travel-optimal"
					)


declare -a suboptimal_domains=("blocks-world-suboptimal"
					"campus-suboptimal"
					"depots-suboptimal"
					"driverlog-suboptimal"
					"dwr-suboptimal"
					"easy-ipc-grid-suboptimal"
					"ferry-suboptimal"
					"intrusion-detection-suboptimal"
					"kitchen-suboptimal"
					"logistics-suboptimal"
					"miconic-suboptimal"
					"rovers-suboptimal"
					"satellite-suboptimal"
					"sokoban-suboptimal"
					"zeno-travel-suboptimal"
					)

declare -a noisy_domains=("blocks-world-noisy"
					"campus-noisy"
					"depots-noisy"
					"driverlog-noisy"
					"dwr-noisy"
					"easy-ipc-grid-noisy"
					"ferry-noisy"
					"intrusion-detection-noisy"
					"kitchen-noisy"
					"logistics-noisy"
					"miconic-noisy"
					"rovers-noisy"
					"satellite-noisy"
					"sokoban-noisy"
					"zeno-travel-noisy"
					)


DATASETS=../goal-plan-recognition-dataset
METHODS="dc dcu w wu wdc wdcu"

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
	screen -dmS lp-recognizer-$domain zsh -c "python2 test_domain.py $DATASETS $domain $METHODS; mv *.txt ..; cd ..; rm -rf lp-recognizer-$domain"
	popd
}

for domain in "${optimal_domains[@]}"; do
	run_domain $domain
done
for domain in "${suboptimal_domains[@]}"; do
	run_domain $domain
done
for domain in "${noisy_domains[@]}"; do
	run_domain $domain
done

popd