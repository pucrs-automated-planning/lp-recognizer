#!/usr/bin/env bash

declare -a domains=("blocks-world"
					"blocks-world-aaai"
					"campus"
					"campus-noisy"
					"depots"
					"driverlog"
					"dwr"
					"dwr"
					"easy-ipc-grid"
					"easy-ipc-grid-noisy"
					"ferry"
					"hanoi"
					# "hanoi_handmade"
					"intrusion-detection"
					"intrusion-detection-noisy"
					"kitchen"
					"kitchen-noisy"
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
pushd ..
for $domain in domains; do
	python2 run_experiments.py $domain
done
