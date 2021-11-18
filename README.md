# Goal Recognition via LP-Constraints

[![Build Status](https://travis-ci.com/pucrs-automated-planning/lp-recognizer.svg?token=wcNhPPzeYu4Vp7Wds6rN&branch=master)](https://travis-ci.com/pucrs-automated-planning/lp-recognizer)

[![DOI](https://zenodo.org/badge/163009224.svg)](https://zenodo.org/badge/latestdoi/163009224)

A goal recognizer that uses Linear Programming Heuristics from Automated planning to compute most likely goals. If you find this research useful in your research, place cite the following paper:

```
@inproceedings{Santos2021,
author = {Lu\'{i}sa R. de A. Santos and Felipe Meneguzzi and Ramon F. Pereira and Andr\'{e} Pereira},
title = {{An LP-Based Approach for Goal Recognition as Planning}},
booktitle = {Proceedings of the 35th AAAI Conference on Artificial Intelligence (AAAI)},
year = {2021},
publisher = {AAAI Press}
}
```

## Installation

LP-Recognizer is written mostly in Python, but we rely heavily in the constraints generated by the heurstic functions in the [Fast Downward](http://www.fast-downward.org) planner, so configuration is a two-step process.

1. Configure [IBM CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio) (we need this to enable the OperatorCounting heuristic plugin in Fast Downward) 
2. Download and configure [Fast Downward](http://www.fast-downward.org/ObtainingAndRunningFastDownward) and apply a patch with our modifications for it.

We use a customized build of Fast Downward, so we provide automated scripts to download and build the requirements for a successful compilation (since there is a sign up required for CPLEX, we cannot automate that). Once you have CPLEX configure, you need to run the follow commands to be able to run LP-Recognizer:

```bash
git clone https://github.com/pucrs-automated-planning/lp-recognizer.git
cd lp-recognizer
bash prepare-fd.sh #This should download Fast Downward (and dependencies) apply patches and compile
```

Note that the above command will download many dependencies, including the [Open Solver Interface (OSI)](https://www.coin-or.org) and [SoPlex](https://soplex.zib.de), compile them, and link them to Fast Downward.

## Running LP-Recognizer

### Running plan recognition in a single problem

Our Python code was based off of Ramirez and Geffner's original recognizer, so experiments are in the form of a ```tar.bz2``` file containing:

- A PDDL Domain
- An observation sequence
- A number of hypotheses (possible goal formulas)
- A PDDL Problem Template (containing the initial state)

This recognizer is compatible with all the domains in this publicly available dataset of [Goal and Plan Recognition Datasets](https://github.com/pucrs-automated-planning/goal-plan-recognition-dataset-lp). We currently implement three different approaches to goal recognition based on operator counts:

1.  Comparing overlap of observations and operator counts, accessible with the ```hvalue``` heuristic
2.  Minimizing the operator counts subject to constraints derived from the observations (i.e. all observations must be included in the counts), accessible with the ```hvaluec``` and ```hvaluecu``` (measuring uncertainty) heuristics
3. Minimizing the difference between the operator counts with the observation constraints and the operator counts with then, accessible with the ```delta``` and ```deltau``` (measuring uncertainty) heuristics

It is also possible to add parameters in the heuristic name:

1.  Using noisy filters by adding ```-f``` followed by a number x that means 0.x of noise. Example: ```delta-f2``` for 20% of noise
2.  Change the constraint sets by adding ```-c``` followed by ```l``` (landmarks), ```s``` (state equation), ```p``` (post-hoc), or combations. Example: ```delta-clp``` for landmarks with post-hoc constraints
3.  Use IP instead of LP by adding ```-i```. Example: ```delta-i-cs``` for IP using only state equation constraints

To run any experiment, just run:
```bash
python test_instance.py -r <heuristics> -e <experiment_file>
``` 

Where ```<experiment_file>``` is one of the experiments in your dataset. 
For example, with the experiments we provide here, we could run sokoban with the hard constraints strategy as follows:

```bash
./test_instance.py -r deltac -e experiments/small-sokoban-optimal/10/sokoban_p01_hyp-1_10_1.tar.bz2
```

### Running plan recognition in a set of experiments 

In order to run experiments for an entire domain organized in a folder named ```domain```, you need to run:

```bash
./test_domain.py <path> <domain> <heuristics>
```

For example, to run the sokoban sample using all the heuristics, you need to run:

```bash
./test_domain.py "experiments/" small-sokoban-optimal "delta deltau delta-f2"
```

### Running plan recognition experiments from AAAI paper

In order to run all of the experiments in our paper, you need to run ```get_results.sh``` from the [experiments](experiments) folder, which will run every single domain for all approaches. 
``` 
cd experiments;./get_results.sh -rerun
```

Note that since the dataset is pretty large, this takes a very long time to finish. 

## Commit hacks (changes) to Fast Downward here

We store our changes to Fast Downward in the ```fd-patch.diff``` patch file in this repository. Whenever you change Fast Downward for LP-Recognizer, ensure these changes are stored here by running:
```bash
bash make-fd-patch.sh
git commit -m "Storing patches to Fast Downward" fd-patch.diff fd-patch-rev.txt
git push
```  