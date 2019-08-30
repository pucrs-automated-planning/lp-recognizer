#!/usr/bin/env zsh

# declare -a domains=("blocks-world"
# 					)
#
# declare -a noisy_domains=("blocks-world-noisy"
# 					)

declare -a domains=("blocks-world"
					# "blocks-world-aaai"
					"campus"
					"depots"
					"driverlog"
					"dwr"
					"easy-ipc-grid"
					"ferry"
					# "hanoi"
					# "hanoi_handmade"
					"intrusion-detection"
					"kitchen"
					# "lo_handmade"
					# "lodigital"
					"logistics"
					# "lotwisted"
					# "mandrill"
					"miconic"
					# "mnist"
					# "mnist_handmade"
					"rovers"
					"satellite"
					"sokoban"
					# "spider"
					"zeno-travel"
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

pushd ..
# echo "$domains"
if [[ ! -d results ]]; then
	mkdir results
fi

if [[ ! -d ../clones ]]; then
	mkdir ../clones
fi

if [[ ! -d ../clones/fast-downward ]]; then
	cp -R ../fast-downward ../clones/fast-downward
fi

for domain in "${domains[@]}"; do
	echo "Copying domain ${domain}"
	cp -R ../lp-recognizer ../clones/lp-recognizer-$domain
	pushd ../clones/lp-recognizer-$domain
	folder=`pwd`
	echo "Running domain ${domain} at $folder"
	screen -dmS lp-recognizer-$domain zsh -c "python2 run_experiments.py $domain -s -d -u -n -f -k; mv *.txt ..; cd ..; rm -rf lp-recognizer-$domain"
	popd
done

for domain in "${noisy_domains[@]}"; do
	echo "Copying domain ${domain}"
	cp -R ../lp-recognizer ../clones/lp-recognizer-$domain
	pushd ../clones/lp-recognizer-$domain
	folder=`pwd`
	echo "Running domain ${domain} at $folder"
	screen -dmS lp-recognizer-$domain zsh -c "python2 run_experiments.py $domain -s -d -u -n -f -k; mv *.txt ..; cd ..; rm -rf lp-recognizer-$domain"
	popd
done