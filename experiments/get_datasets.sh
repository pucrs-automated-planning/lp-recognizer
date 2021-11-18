#!/usr/bin/env bash

EXPERIMENTS_REPO="https://github.com/pucrs-automated-planning/goal-plan-recognition-dataset-lp.git"
## Alternative repo
# EXPERIMENTS_REPO="https://github.com/luisaras/goal-plan-recognition-dataset.git"

pushd ../../
git clone --depth=1 $EXPERIMENTS_REPO goal-plan-recognition-dataset
popd