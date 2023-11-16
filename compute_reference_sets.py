#!/usr/bin/env python3

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
        print("Error: %s" % err.returncode)
        return err.returncode

def run_planner(domain, problem, bound=None):
    args = ["../fast-downward/fast-downward.py", "--search-time-limit", "30m", "--search-memory-limit", "8G",\
        domain, problem, "--search", "astar(lmcut())"]
    if bound:
        args[-1] = "astar(lmcut(), bound=%s)" % int(math.ceil(bound) + 1)
    output = run(args)
    if type(output) != str:
        return -output
    for line in output.split('\n'):
        if 'Plan length: ' in line:
            length = line.split(':')[1].replace(" step(s).", "")
            return float(length)
    return -1

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
    translator_output = run(["../obs-compiler/pr2plan", "-d", "domain.pddl", "-i", "problem.pddl", "-o", "obs.dat"])
    if type(translator_output) != str:
        return float("inf")
    opt_length = run_planner("domain.pddl", "problem.pddl")
    print("Optimal plan length: %s" % opt_length)
    if opt_length == -12:
        print("Unsolvable.")
        return float("inf")
    elif opt_length == -22:
        print("Out of memory.")
        return "Out of memory"
    elif opt_length == -23:
        print("Out of time.")
        return "Out of time"
    length = run_planner("pr-domain.pddl", "pr-problem.pddl", opt_length * len_ratio)
    print("Observed plan length: %s" % length)
    if length == -12:
        print("Unsolvable.")
        return float("inf")
    elif length == -22:
        print("Out of memory.")
        return "Out of memory"
    elif length == -23:
        print("Out of time.")
        return "Out of time"
    print(length, opt_length)
    return length / opt_length

def compute_solution(hyps):
    print(str(len(hyps)) + " goals")
    real_hyp = [hyp for hyp in hyps if hyp.is_true][0]
    real_hyp_ir = get_irrationality_ratio(real_hyp, 2)
    print("IR: " + str(real_hyp_ir))
    if type(real_hyp_ir) == str:
        print("Error: " + real_hyp_ir)
        return ["ERROR"]
    solution = []
    for hyp in hyps:
        if hyp.is_true:
            solution.append(' '.join(hyp.atoms))
            continue
        hyp_ir = get_irrationality_ratio(hyp, real_hyp_ir)
        if type(hyp_ir) == str:
            print("Error: " + hyp_ir)
            return ["ERROR"]
        if hyp_ir <= real_hyp_ir:
            solution.append(' '.join(hyp.atoms))
    return solution

def write_file_solution(file):
    print(file)
    opts = Program_Options(['-e', file])
    hyps = load_hypotheses(opts)
    solution = compute_solution(hyps)
    print(solution)
    outstream = open(file.replace("tar.bz2", "solution"), 'w')
    print('\n'.join(solution), file=outstream)
    outstream.close()

def write_directory_solutions(folder):
    print(folder)
    for path in os.listdir(folder):
        if os.path.isdir(folder + "/" + path):
            write_directory_solutions(folder + "/" + path)
        elif path.endswith("tar.bz2"):
            if not os.path.exists(folder + "/" + path.replace("tar.bz2", "solution")):
                write_file_solution(folder + "/" + path)

if __name__ == '__main__':
    os.system('rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2')
    path = sys.argv[1]
    if os.path.isdir(path):
        write_directory_solutions(path)
    else:
        write_file_solution(path)