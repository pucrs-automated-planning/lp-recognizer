#!/usr/bin/env python2.7

import sys, os, csv, time, math, subprocess
DEVNULL = open(os.devnull,"r+b")
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory

EXP_FILTER = False
def filter(name):
	if EXP_FILTER:
		return ("_2.tar" in name) or ("_3.tar" in name) or ("hyp-4" in name) or ("hyp-3" in name)
	else:
		return False

class ExperimentH:
	def __init__(self, constraint_sets, obs, test_h_obs = False):
		self.test_h_obs = test_h_obs
		self.constraint_sets = constraint_sets
		self.obs = obs
		self.real_h_values = dict()
		self.h_values = dict()
		self.spread = dict()
		self.real_hc_values = dict()
		self.hc_values = dict()
		self.fpr = dict()
		self.fnr = dict()
		self.agreement = dict()
		constraint_sets = constraint_sets + [c.replace("(", "_o(") for c in constraint_sets]
		for c in constraint_sets:
			self.real_h_values[c] = []
			self.h_values[c] = []
			self.spread[c] = []
			self.real_hc_values[c] = []
			self.hc_values[c] = []
			self.fpr[c] = []
			self.fnr[c] = []
			self.agreement[c] = []

	def test_instance(self, c, recognizer):
		recognizer.run_recognizer()

		real_hyp = recognizer.get_real_hypothesis()
		hyp = recognizer.unique_goal
		self.real_h_values[c].append(real_hyp.h)
		self.h_values[c].append(hyp.h)
		self.real_hc_values[c].append(real_hyp.h_c)
		self.hc_values[c].append(hyp.h_c)

		solution_set = frozenset([h.atoms for h in recognizer.accepted_hypotheses])
		exact_solution_set = frozenset([h.atoms for h in recognizer.hyps if h.is_solution])
		self.spread[c].append(len(solution_set))

		total = float(len(exact_solution_set | solution_set))
		fp = float(len(solution_set - exact_solution_set))
		fn = float(len(exact_solution_set - solution_set))
		self.fpr[c].append(fp / total)
		self.fnr[c].append(fn / total)
		self.agreement[c].append((total - fp - fn) / total)

	def test_contraints(self, path):
		for c in self.constraint_sets:
			options = Program_Options(['-e', path, '-H', c])
			factory = PlanRecognizerFactory(options)
			self.test_instance(c, factory.get_recognizer("delta", options))
			if self.test_h_obs:
				self.test_instance(c.replace("(", "_o("), factory.get_recognizer("delta-o", options))

	def do_experiments(self, domains): 
		for domainName in domains:
			problems_path = '../goal-plan-recognition-dataset/' + domainName + '/' + str(self.obs) + '/'
			files = os.listdir(problems_path)
			files.sort()
			for problem_file in files:
				if not problem_file.endswith(".tar.bz2") or filter(problem_file):
					continue
				print(problem_file)
				path = problems_path + problem_file
				os.system('tar xvjf ' + path) # Untar files
				self.test_contraints(path)

	def save_files(self, prefix=""):
		constraint_sets = self.constraint_sets
		if self.test_h_obs:
			constraint_sets = constraint_sets + [c.replace("(", "_o(") for c in constraint_sets]
		for c in constraint_sets:
			results_file = open("constraint-values/%s_%s_%s.txt" % (prefix, self.obs, c), "w")
			results_file.write(str(self.real_h_values[c]) + '\n')
			results_file.write(str(self.h_values[c]) + '\n')
			results_file.write(str(self.spread[c]) + '\n')
			results_file.write(str(self.real_hc_values[c]) + '\n')
			results_file.write(str(self.hc_values[c]) + '\n')
			results_file.write(str(self.fpr[c]) + '\n')
			results_file.write(str(self.fnr[c]) + '\n')
			results_file.write(str(self.agreement[c]) + '\n')
			results_file.close()


def get_all_h_values():
	observabilities = [10, 30, 50, 70]
	constraint_sets = ["pho_constraints()", "state_equation_constraints()"]
	constraint_sets_obs = ["lmcut_constraints()", "delete_relaxation_constraints()"]

	if len(sys.argv) > 1 and sys.argv[1] == '-fast':
		EXP_FILTER = True
		domains = [
		'blocks-world',
		'depots',
		'driverlog',
		'dwr',
		'rovers',
		'sokoban'
		]
		domain_types = ['-optimal']
	else:
		domains = [
		"blocks-world",
		"depots",
		"driverlog",
		"dwr",
		"easy-ipc-grid",
		"ferry",
		"logistics",
		"miconic",
		"rovers",
		"satellite",
		"sokoban",
		"zeno-travel",
		]
		domain_types = [
		"-optimal",
		"-suboptimal",
		]

	for domain in domains:
		for dt in domain_types:
			for obs in observabilities:
				# pho, seq,
				e = ExperimentH(constraint_sets, obs, False)
				e.do_experiments([domain + dt])
				e.save_files(domain + dt)
				# lmc, lmc+, del, del+
				e = ExperimentH(constraint_sets_obs, obs, True)
				e.do_experiments([domain + dt])
				e.save_files(domain + dt)

if __name__ == '__main__':
	get_all_h_values()
