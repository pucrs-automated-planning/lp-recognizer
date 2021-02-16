#!/usr/bin/env python2.7

import os, sys, re
import domain_data as dd

EXP_FILTER = False
def filter(name):
	if EXP_FILTER:
		return ("_2.tar" in name) or ("_3.tar" in name) or ("hyp-4" in name) or ("hyp-3" in name)
	else:
		return False
def set_filter(value):
	EXP_FILTER = value


class ProblemOutput:

	def __init__(self, name, recognizer = None):
		self.name = name
		self.scores = {}
		self.lp_sizes = {}
		if recognizer is None:
			return

		# Get solution
		self.solution_set = frozenset([h.atoms for h in recognizer.accepted_hypotheses])
		exact_solution_set = frozenset([h.atoms for h in recognizer.hyps if h.is_solution])
		real_hyp = recognizer.get_real_hypothesis()
		hyp = recognizer.unique_goal

		# Time results
		self.lp_time = recognizer.lp_time
		self.fd_time = recognizer.fd_time
		self.total_time = recognizer.total_time

		# Domain info
		self.num_obs = len(recognizer.observations)
		self.num_goals = len(recognizer.hyps)
		self.num_solutions = len(exact_solution_set)

		# Results
		total = float(len(exact_solution_set | self.solution_set))
		fp = float(len(self.solution_set - exact_solution_set))
		fn = float(len(exact_solution_set - self.solution_set))
		agr = (total - fp - fn) / total
		self.fpr = fp / total
		self.fnr = fn / total
		self.agreement = agr
		self.spread = len(self.solution_set)
		self.accuracy = 1 if recognizer.get_real_hypothesis().atoms in self.solution_set else 0
		self.perfect_agr = 1 if agr == 1 else 0

		# Hyp data
		for h in recognizer.hyps:
			if not h.test_failed:
				self.scores[h.atoms] = [h.h, h.h_c]
				self.lp_sizes[h.atoms] = [h.num_lp_vars, h.num_lp_consts]
		# Chosen hyp
		self.num_lp_vars = hyp.num_lp_vars
		self.num_lp_consts = hyp.num_lp_consts
		self.h_value = hyp.h
		self.hc_value = hyp.h_c
		# Reference hyp
		if not real_hyp.test_failed:
			self.real_num_lp_vars = real_hyp.num_lp_vars
			self.real_num_lp_consts = real_hyp.num_lp_consts
			self.real_h_value = real_hyp.h
			self.real_hc_value = real_hyp.h_c

	def load(self, problem_data, raw_problem):
		# Time results
		if len(raw_problem.times) > 0:
			self.total_time = raw_problem.times[0]
		if len(raw_problem.times) > 1:
			self.lp_time = raw_problem.times[1]
		if len(raw_problem.times) > 2:
			self.fd_time = raw_problem.times[2]

		# Domain info
		self.num_obs = len(problem_data.obs)
		self.num_goals = len(problem_data.hyps)
		self.num_solutions = len(problem_data.solution)

		# Get solution
		min_score = [float("inf")]
		hyp = None
		for goal in raw_problem.goals:
			score = raw_problem.scores[goal][1] - raw_problem.scores[goal][0]
			if score < min_score:
				min_score = score
				hyp = goal
		self.solution_set = frozenset([atoms for atoms in raw_problem.goals if raw_problem.accepted[atoms] == True])
		exact_solution_set = frozenset(problem_data.solution)
		real_hyp = problem_data.true_hyp

		# Results
		total = float(len(exact_solution_set | self.solution_set))
		fp = float(len(self.solution_set - exact_solution_set))
		fn = float(len(exact_solution_set - self.solution_set))
		agr = (total - fp - fn) / total
		self.fpr = fp / total
		self.fnr = fn / total
		self.agreement = agr
		self.spread = len(self.solution_set)
		self.accuracy = 1 if real_hyp in self.solution_set else 0
		self.perfect_agr = 1 if agr == 1 else 0

		# Hyp data
		self.scores = raw_problem.scores
		self.lp_sizes = raw_problem.lp_sizes
		# Chosen hyp
		self.num_lp_vars = raw_problem.lp_sizes[hyp][0]
		self.num_lp_consts = raw_problem.lp_sizes[hyp][1]
		self.h_value = raw_problem.scores[hyp][0]
		self.hc_value = raw_problem.scores[hyp][1]
		# Reference hyp
		if real_hyp in raw_problem.goals:
			self.real_num_lp_vars = raw_problem.lp_sizes[real_hyp][0]
			self.real_num_lp_consts = raw_problem.lp_sizes[real_hyp][1]
			self.real_h_value = raw_problem.scores[real_hyp][0]
			self.real_hc_value = raw_problem.scores[real_hyp][1]
		else:
			self.real_num_lp_vars = 0
			self.real_num_lp_consts = 0
			self.real_h_value = 0
			self.real_hc_value = 0

	def print_content(self):
		content = self.name + ":" + str(self.total_time) + ":" + str(self.lp_time) + ":" + str(self.fd_time) + "\n"
		for h in self.scores.keys():
			atoms = ','.join(h)
			score = ','.join([str(x) for x in self.scores[h]])
			lp_size = ','.join([str(x) for x in self.lp_sizes[h]])
			accepted = str(h in self.solution_set)
			content += "> " + atoms + ":" + accepted + ":" + score + ":" + lp_size + "\n"
		return content


class ExperimentOutput:

	def __init__(self, obs):
		self.obs = obs
		self.total_time = 0
		self.max_time = 0
		self.problem_outputs = dict()

	def load(self, domain_data, raw_experiment):
		if self.obs in raw_experiment.experiment_times:
			self.total_time = raw_experiment.experiment_times[self.obs]
			self.max_time = self.total_time
		for raw_problem in raw_experiment.problems[self.obs]:
			problem_data = domain_data.data[self.obs][raw_problem.file]
			problem = ProblemOutput(problem_data.name)
			problem.load(problem_data, raw_problem)
			self.add_problem(problem)

	def add_problem(self, problem):
		self.problem_outputs[problem.name] = problem
		self.total_time += problem.total_time
		self.max_time = max(self.max_time, problem.total_time)

	def print_hdata(self):
		content = self.obs + '\n'
		content += str([x.real_h_value for x in self.problem_outputs.values()]) + '\n'
		content += str([x.h_value for x in self.problem_outputs.values()]) + '\n'
		content += str([x.spread for x in self.problem_outputs.values()]) + '\n'
		content += str([x.real_hc_value for x in self.problem_outputs.values()]) + '\n'
		content += str([x.hc_value for x in self.problem_outputs.values()]) + '\n'
		content += str([x.fpr for x in self.problem_outputs.values()]) + '\n'
		content += str([x.fnr for x in self.problem_outputs.values()]) + '\n'
		content += str([x.agreement for x in self.problem_outputs.values()]) + '\n'
		content += str([x.lp_time for x in self.problem_outputs.values()]) + '\n'
		return content

	def print_stats(self):
		problems = self.problem_outputs.values()
		n = float(len(problems))
		values = [\
		sum([p.num_obs for p in problems]) / n, \
		sum([p.num_goals for p in problems]) / n, \
		sum([p.num_solutions for p in problems]) / n, \
		sum([p.agreement for p in problems]) / n, \
		sum([p.fpr for p in problems]) / n, \
		sum([p.fnr for p in problems]) / n, \
		sum([p.accuracy for p in problems]) / n, \
		sum([p.spread for p in problems]) / n, \
		sum([p.perfect_agr for p in problems]), \
		self.total_time / n, \
		sum([p.lp_time for p in problems]) / n, \
		sum([p.fd_time for p in problems]) / n, \
		sum([p.real_num_lp_vars for p in problems]) / n, \
		sum([p.real_num_lp_consts for p in problems]) / n, \
		sum([p.real_h_value for p in problems]) / n, \
		sum([p.real_hc_value for p in problems]) / n]
		content = "%s\t%s\t" % (len(problems), self.obs)
		content += '\t'.join(["%2.4f" % x for x in values])
		content += '\n'
		return content 


class RawProblem:

	def __init__(self, file):
		self.file = file
		self.goals = []
		self.accepted = {}
		self.scores = {}
		self.lp_sizes = {}
		self.times = []

	def add_goal(self, line):
		line = line.strip().replace("> ", "").split(":")
		atoms = frozenset([tok.strip().lower() for tok in line[0].split(',')])
		self.goals.append(atoms)
		if len(line) > 1:
			self.accepted[atoms] = line[1] == 'True'
		else:
			self.accepted[atoms] = True
		if len(line) > 2:
			self.scores[atoms] = [float(x) for x in line[2].split(',')]
		else:
			self.scores[atoms] = [0, 0]
		if len(line) > 3:
			self.lp_sizes[atoms] = [float(x) for x in line[3].split(',')]
		else:
			self.lp_sizes[atoms] = [0, 0]

	def add_times(self, line):
		self.times = [float(x) for x in line[1:]]


class RawExperiment:

	def __init__(self, filename, observabilities):
		file = open("outputs/" + filename + ".output")
		current_problem = None
		problems = []
		experiment_times = []
		for line in file:
			# New goal for current problem
			if line.startswith(">"):
				if current_problem is not None:
					current_problem.add_goal(line)
				continue
			line = line.split(":")
			current_file = line[0].strip().replace("pb", "p")
			if filter(current_file):
				current_file = None
				continue
			if current_file[0].isdigit():
				experiment_times.append(current_file)
				continue
			current_problem = RawProblem(current_file)
			problems.append(current_problem)
			if len(line) > 1 and line[1].strip()[0].isdigit():
				current_problem.add_times(line)
		# Separate by observability
		self.problems = dict()
		for obs in observabilities:
			self.problems[obs] = []
		for problem in problems:
			for obs in observabilities:
				print(obs + "/", problem.file)
				if obs + "/" in problem.file:
					self.problems[obs].append(problem)
					break
		self.experiment_times = dict()
		for i in range(len(experiment_times)):
			self.experiment_times[observabilities[i]] = experiments[i]


def read_output(base_path, domain_data, method):
	raw_experiment = RawExperiment(domain_data.name + "-" + method, domain_data.observabilities)
	experiments = []
	for obs in observabilities:
		experiment = ExperimentOutput(obs)
		experiment.load(domain_data, raw_experiment)
		experiments.append(experiment)
	return experiments

if __name__ == '__main__':
	observabilities = ['10', '30', '50', '70', '100']
	base_path = '../goal-plan-recognition-dataset/'
	domain_name = sys.argv[1]
	methods = sys.argv[2]
	if '-fast' in sys.argv:
		set_filter(True)
		dd.set_filter(True)
	domain_data = dd.DomainData(domain_name, observabilities)
	if os.path.exists(sys.argv[1] + ".txt"):
		domain_data.read()
	else:
		domain_data.load(base_path)
	for method in methods.split():
		experiments = read_output(base_path, domain_data, method)
		with open("data-latex/" + domain_name + "-" + method + ".txt", 'w') as f:
			f.write("#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tPER\tTime\tTimeLP\tTimeFD\tVars\tConsts\tH\tHC\n")
			for experiment in experiments:
				f.write(experiment.print_stats())
		with open("data-charts/" + domain_name + "-" + method + ".txt", 'w') as f:
			for experiment in experiments:
				f.write(experiment.print_hdata())