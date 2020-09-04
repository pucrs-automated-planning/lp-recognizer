#!/usr/bin/env python2.7

import sys, os, csv, time, math, subprocess
DEVNULL = open(os.devnull,"r+b")
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory

class ExperimentH:
    def __init__(self, constraint_sets, obs):
        self.constraint_sets = constraint_sets
        self.obs = obs
        self.real_h_values = dict()
        self.h_values = dict()
        self.spread = dict()
        self.real_delta_values = dict()
        self.delta_values = dict()
        self.fpr = dict()
        self.fnr = dict()
        self.agreement = dict()
        for c in constraint_sets:
            self.real_h_values[c] = []
            self.h_values[c] = []
            self.spread[c] = []
            self.real_delta_values[c] = []
            self.delta_values[c] = []
            self.fpr[c] = []
            self.fnr[c] = []
            self.agreement[c] = []

    def test_instance(self, path):
        for c in self.constraint_sets:
            options = Program_Options(['-e', path, '-H', c])
            recognizer = PlanRecognizerFactory(options).get_recognizer("delta-h-c", options)
            recognizer.run_recognizer()
            real_hyp = recognizer.get_real_hypothesis()
            hyp = recognizer.unique_goal
            self.real_h_values[c].append(real_hyp.h)
            self.h_values[c].append(hyp.h)
            self.spread[c].append(len(recognizer.accepted_hypotheses))
            self.real_delta_values[c].append(real_hyp.h_c)
            self.delta_values[c].append(hyp.h_c)

            solution_set = set([h for h in recognizer.hyps if h.is_solution])
            total = float(len(solution_set | recognizer.accepted_hypotheses))
            fp = float(len(recognizer.accepted_hypotheses - solution_set))
            fn = float(len(solution_set - recognizer.accepted_hypotheses))
            self.fpr[c].append(fp / total)
            self.fnr[c].append(fn / total)
            self.agreement[c].append((total - fp - fn) / total)
        return True

    def do_experiments(self, domains): 
        file_failures = open("failed.txt", "w")
        for domainName in domains:
            problems_path = '../goal-plan-recognition-dataset/' + domainName + '/' + str(self.obs) + '/'
            for problem_file in os.listdir(problems_path):
                if not problem_file.endswith(".tar.bz2"):
                    continue
                print(problem_file)
                path = problems_path + problem_file
                os.system('tar xvjf ' + path) # Untar files
                success = self.test_instance(path)
                if not success:
                    file_failures.write(path + "\n")
                #os.system('rm -rf *.pddl *.dat *.log') # Clean
        file_failures.close()
        # Get rid of the temp files
        #os.system('rm -rf *.soln *.csv report.txt h_result.txt results.tar.bz2')

    def save_files(self, prefix=""):
        for c in self.constraint_sets:
            results_file = open("constraint-values/%sh_%s_%s.txt" % (prefix, self.obs, c), "w")
            results_file.write(str(self.real_h_values[c]) + '\n')
            results_file.write(str(self.h_values[c]) + '\n')
            results_file.write(str(self.spread[c]) + '\n')
            results_file.write(str(self.real_delta_values[c]) + '\n')
            results_file.write(str(self.delta_values[c]) + '\n')
            results_file.write(str(self.fpr[c]) + '\n')
            results_file.write(str(self.fnr[c]) + '\n')
            results_file.write(str(self.agreement[c]) + '\n')
            results_file.close()


def get_all_h_values():
    observabilities = [10, 30, 50, 70]
    constraint_sets = ["lmcut_constraints()", "pho_constraints()", "state_equation_constraints()"]
    domains = [
    #"blocks-world",
    #"depots",
    #"driverlog",
    "dwr",
    #"easy-ipc-grid",
    "ferry",
    #"logistics",
    #"miconic",
    #"rovers",
    #"satellite",
    #"sokoban",
    #"zeno-travel",
    ]
    domain_types = [
    "-optimal",
    "-suboptimal",
    ]
    for domain in domains:
        for dt in domain_types:
            for obs in observabilities:
                e = ExperimentH(constraint_sets, obs)
                e.do_experiments([domain + dt])
                e.save_files(domain + dt)

if __name__ == '__main__':
    get_all_h_values()
