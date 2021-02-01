#!/usr/bin/env bash
#  Downloads all experiments from our group's repository
#  get-all-experiments.sh
#  lp-recognizer
#
#  Created by Felipe Meneguzzi on 2019-08-28.
#  Copyright 2019 Felipe Meneguzzi. All rights reserved.
#

## Alternative repo
# EXPERIMENTS_REPO="https://github.com/pucrs-automated-planning/goal-plan-recognition-dataset-lp.git"

EXPERIMENTS_REPO="https://github.com/luisaras/goal-plan-recognition-dataset.git"

pushd ../../
git clone --depth=1 $EXPERIMENTS_REPO goal-plan-recognition-dataset
popd