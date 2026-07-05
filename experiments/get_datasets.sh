#!/usr/bin/env bash

# goal-plan-recognition-dataset-lp  — LP dataset, includes reference solution sets (.solution);
#                                      use for AAAI/JAIR experiments (default)
# goal-plan-recognition-dataset      — original AIJ dataset, no reference solution sets
EXPERIMENTS_REPO="https://github.com/pucrs-automated-planning/goal-plan-recognition-dataset-lp.git"
# EXPERIMENTS_REPO="https://github.com/pucrs-automated-planning/goal-plan-recognition-dataset.git"

pushd ../../
git clone --depth=1 $EXPERIMENTS_REPO goal-plan-recognition-dataset
popd