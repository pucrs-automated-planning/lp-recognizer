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
		self.lp_infos = {}
		if recognizer is None:
			return

		# Problem data
		self.hyp_atoms = [h.atoms for h in recognizer.hyps]

		# Get solution
		self.solution_set = frozenset([h.index for h in recognizer.accepted_hypotheses])
		exact_solution_set = frozenset([h.index for h in recognizer.hyps if h.is_solution])
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
		self.accuracy = 1 if recognizer.get_real_hypothesis().index in self.solution_set else 0
		self.perfect_agr = 1 if agr == 1 else 0

		# Hyp data
		for h in recognizer.hyps:
			if not h.test_failed:
				self.scores[h.index] = [h.h, h.h_c]
				self.lp_infos[h.index] = h.lp_info
		# Chosen hyp
		if hyp:
			self.lp_info_best = hyp.lp_info
			self.h_value_best = hyp.h
			self.hc_value_best = hyp.h_c
		else:
			self.lp_info_best = [0, 0]
			self.h_value_best = 0
			self.hc_value_best = 0
		# Reference hyp
		if not real_hyp.test_failed:
			self.lp_info_real = real_hyp.lp_info
			self.h_value_real = real_hyp.h
			self.hc_value_real = real_hyp.h_c
		else:
			self.lp_info_real = [0, 0]
			self.h_value_real = 0
			self.hc_value_real = 0

	def load(self, problem_data, raw_problem):
		# Problem data
		self.hyp_atoms = problem_data.hyps

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
		hyp = None # index
		for goal in raw_problem.goals:
			score = raw_problem.scores[goal][1] - raw_problem.scores[goal][0]
			if score < min_score:
				min_score = score
				hyp = goal
		self.solution_set = frozenset([i for i in raw_problem.goals if raw_problem.accepted[i] == True])
		exact_solution_set = frozenset(problem_data.get_solution_indexes())
		real_hyp = problem_data.get_true_hyp_index()

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
		self.lp_infos = raw_problem.lp_infos
		# Chosen hyp
		if hyp:
			self.lp_info_best = raw_problem.lp_infos[hyp]
			self.h_value_best = raw_problem.scores[hyp][0]
			self.hc_value_best = raw_problem.scores[hyp][1]
		else:
			self.lp_info_best = [0, 0]
			self.h_value_best = 0
			self.hc_value_best = 0
		# Reference hyp
		if real_hyp in raw_problem.goals:
			self.lp_info_real = raw_problem.lp_infos[real_hyp]
			self.h_value_real = raw_problem.scores[real_hyp][0]
			self.hc_value_real = raw_problem.scores[real_hyp][1]
		else:
			self.lp_info_real = [0, 0]
			self.h_value_real = 0
			self.hc_value_real = 0

	def print_content(self):
		content = self.name + ":" + str(self.total_time) + ":" + str(self.lp_time) + ":" + str(self.fd_time) + "\n"
		hyps = list(self.scores.keys())
		for h in hyps:
			#atoms = ','.join(self.hyp_atoms[h])
			atoms = str(h)
			score = ','.join([str(int(x)) for x in self.scores[h]])
			lp_info = ','.join([str(int(x)) for x in self.lp_infos[h]])
			accepted = str(h in self.solution_set)
			content += "> " + atoms + ":" + accepted + ":" + score + ":" + lp_info + "\n"
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
		content += str([x.h_value_real for x in self.problem_outputs.values()]) + '\n'
		content += str([x.h_value_best for x in self.problem_outputs.values()]) + '\n'
		content += str([x.spread for x in self.problem_outputs.values()]) + '\n'
		content += str([x.hc_value_real for x in self.problem_outputs.values()]) + '\n'
		content += str([x.hc_value_best for x in self.problem_outputs.values()]) + '\n'
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
		sum([p.lp_info_real[0] for p in problems]) / n, \
		sum([p.lp_info_real[1] for p in problems]) / n, \
		sum([p.h_value_real for p in problems]) / n, \
		sum([p.hc_value_real for p in problems]) / n, \
		sum([cmp(p.hc_value_real, 0) for p in problems])]
		for i in range(2, len(problems[0].lp_info_real)):
			values.append(sum([p.lp_info_real[i] for p in problems]) / n) # Avg U'
			values.append(sum([cmp(p.lp_info_real[i], 0) for p in problems])) # U' > 0 
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
		self.lp_infos = {}
		self.times = []

	def add_goal(self, line):
		line = line.strip().replace("> ", "").split(":")
		#hyp = frozenset([tok.strip().lower() for tok in line[0].split(',')])
		hyp = int(line[0])
		self.goals.append(hyp)
		if len(line) > 1:
			self.accepted[hyp] = line[1] == 'True'
		else:
			self.accepted[hyp] = True
		if len(line) > 2:
			self.scores[hyp] = [float(x) for x in line[2].split(',')]
		else:
			self.scores[hyp] = [0, 0]
		if len(line) > 3:
			self.lp_infos[hyp] = [float(x) for x in line[3].split(',')]
		else:
			self.lp_infos[hyp] = [0, 0]

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
	for obs in domain_data.observabilities:
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