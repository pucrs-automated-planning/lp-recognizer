#!/usr/bin/env python2.7

# Code originally developed by Miquel Ramirez
import sys, os, subprocess, math
from planner_interface import Hypothesis
from options import Program_Options

def run(cmd):
    try:
        #Python 3:
        #return subprocess.run(args, capture_output=True, text=True).stdout
        return subprocess.check_output(cmd)
    except subprocess.CalledProcessError as err:
        print(err.output)
        return None

def run_planner(domain, problem, bound=None):
    args = ["../fast-downward/fast-downward.py", domain, problem, "--search", "astar(lmcut())"]
    if bound:
        args[-1] = "astar(lmcut(), bound=%s)" % int(math.ceil(bound) + 1)
    output = run(args)
    if output == None:
        return -1.0
    for line in output.split('\n'):
        if 'Plan length: ' in line:
            length = line.split(':')[1].replace(" step(s).", "")
            return float(length)
    return -1.0

def load_hypotheses(opts):
    hyps = []
    instream = open('hyps.dat')
    for line in instream:
        line = line.strip()
        atoms = [tok.strip() for tok in line.split(',')]
        H = Hypothesis(opts, atoms)
        H.check_if_actual()
        hyps.append(H)
    instream.close()
    return hyps

def get_irrationality_ratio(hyp, len_ratio):
    hyp.generate_pddl_for_hyp_plan("problem.pddl")
    if run(["../obs-compiler/pr2plan", "-d", "domain.pddl", "-i", "problem.pddl", "-o", "obs.dat"]) == None:
        return float("inf")
    opt_length = run_planner("domain.pddl", "problem.pddl")
    print("Optimal plan length: %s" % opt_length)
    if opt_length < 0:
        return float("inf")
    length = run_planner("pr-domain.pddl", "pr-problem.pddl", opt_length * len_ratio)
    print("Observed plan length: %s" % length)
    if length < 0:
        return float("inf")
    print(length, opt_length)
    return length / opt_length

def compute_solution(file):
    opts = Program_Options(['-e', file])
    hyps = load_hypotheses(opts)
    print(file)
    print(str(len(hyps)) + " goals")
    real_hyp = [hyp for hyp in hyps if hyp.is_true][0]
    irrationality_ratio = get_irrationality_ratio(real_hyp, 2)
    print("IR: " + str(irrationality_ratio))
    if irrationality_ratio > 2:
        solution = []
    else:
        solution = [' '.join(hyp.atoms) for hyp in hyps if hyp.is_true or (get_irrationality_ratio(hyp, irrationality_ratio) <= irrationality_ratio)]
    print(solution)
    outstream = open(file.replace("tar.bz2", "solution"), 'w')
    print >> outstream, '\n'.join(solution)
    outstream.close()

def compute_directory_solutions(folder):
    print(folder)
    for path in os.listdir(folder):
        if os.path.isdir(folder + "/" + path):
            compute_directory_solutions(folder + "/" + path)
        elif path.endswith("tar.bz2"):
            if not os.path.exists(folder + "/" + path.replace("tar.bz2", "solution")):
                compute_solution(folder + "/" + path)

if __name__ == '__main__':
    os.system('rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2')
    path = sys.argv[1]
    if os.path.isdir(path):
        compute_directory_solutions(path)
    else:
        compute_solution(path)
    