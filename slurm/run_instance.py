#!/usr/bin/env python3
"""
Run one recognizer method on one experiment instance and write a ProblemOutput
record to an output file.

Usage:
    run_instance.py <exp_file> <method> <out_file> [extra options for Program_Options]

Extra options are passed directly to Program_Options, e.g. -S soplex.
The caller (run_experiment.sh) sets the working directory to an isolated temp
directory; extracted PDDL files land in the CWD and are cleaned up at the
start of each call so previous instances don't interfere.
"""

import sys
import os

# Repo root is on PYTHONPATH (set by run_experiment.sh).
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory
import data_output as do

exp_file = sys.argv[1]
method = sys.argv[2]
out_file = sys.argv[3]
extra = sys.argv[4:]

# Remove any leftover files from the previous instance in this working dir.
os.system('rm -rf ./*.pddl ./*.dat ./*.log ./*.csv')

options = Program_Options(['-r', method] + extra)
options.extract_exp_file(exp_file)

recognizer = PlanRecognizerFactory(options).get_recognizer(method, options)
recognizer.run_recognizer()

print(
    f"LP: {recognizer.lp_time:.3f}s  FD: {recognizer.fd_time:.3f}s  "
    f"Total: {recognizer.total_time:.3f}s"
)

# Store only domain/obs/filename.tar.bz2 so data_output.py path lookups work
# regardless of where the dataset lives on the filesystem.
parts = exp_file.replace("\\", "/").split("/")
problem_name = "/".join(parts[-3:])
output = do.ProblemOutput(problem_name, recognizer)
os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(out_file, 'w') as f:
    f.write(output.print_content())
