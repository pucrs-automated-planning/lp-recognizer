#!/usr/bin/env python2.7

##
## Generate method results summary tables (data-tables and data-charts folder).
##

## Uses:
# For especific domains:
# ./data_output.py "delta-cl delta-o-cl1" blocks-world-optimal depots-optimal [-fast]
# For all domains:
# ./data_output.sh "delta-cl delta-o-cl1" all [-fast]
# For method groups:
# ./data_output.sh lm optimal -hvalues -scatter -stats [-fast]
# ./data_output.sh fl optimal -hvalues -scatter -stats [-fast]
# ./data_output.sh dr optimal -hvalues -stats [-fast]
##

import os, sys, re
import data_domain as dd

EXP_FILTER = False
def filter(name):
	if EXP_FILTER:
		return ("_2.tar" in name) or ("_3.tar" in name) or ("hyp-4" in name) or ("hyp-3" in name)
	else:
		return False
def set_filter(value):
	EXP_FILTER = value


class ProblemOutput:

	#
	# The results for a single goal recognition task. 
	#

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
		wrong_solution_set = frozenset([h for h in recognizer.hyps if not h.is_solution])
		real_hyp = recognizer.get_real_hypothesis()
		hyp = recognizer.unique_goal

		# Wrong hyp
		min_wrong_d = min([h.h_c - h.h for h in wrong_solution_set if not h.test_failed])
		min_wrong_hyps = [h for h in wrong_solution_set if h.h_c - h.h == min_wrong_d]
		wrong_hyp = min_wrong_hyps[0] if len(min_wrong_hyps) > 0 else None

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
		# Wrong hyp
		if wrong_hyp:
			self.lp_info_wrong = wrong_hyp.lp_info
			self.h_value_wrong = wrong_hyp.h
			self.hc_value_wrong = wrong_hyp.h_c
		else:
			self.lp_info_wrong = [0, 0]
			self.h_value_wrong = 0
			self.hc_value_wrong = 0


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
		exact_solution_set = frozenset(problem_data.get_solution_indexes())
		wrong_solution_set = frozenset(raw_problem.goals) - exact_solution_set
		real_hyp = problem_data.get_true_hyp_index()
		self.solution_set = frozenset([i for i in raw_problem.goals if raw_problem.accepted[i] == True])
		min_score = float("inf")
		hyp = None # index
		for goal in raw_problem.goals:
			score = raw_problem.scores[goal][1] - raw_problem.scores[goal][0]
			if score < min_score:
				min_score = score
				hyp = goal
		min_score = float("inf")
		wrong_hyp = None # index
		for goal in wrong_solution_set:
			score = raw_problem.scores[goal][1] - raw_problem.scores[goal][0]
			if score < min_score:
				min_score = score
				wrong_hyp = goal

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
		# Wrong hyp
		if wrong_hyp:
			self.lp_info_wrong = raw_problem.lp_infos[wrong_hyp]
			self.h_value_wrong = raw_problem.scores[wrong_hyp][0]
			self.hc_value_wrong = raw_problem.scores[wrong_hyp][1]
		else:
			self.lp_info_wrong = [0, 0]
			self.h_value_wrong = 0
			self.hc_value_wrong = 0

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

	#
	# The results for the set of goal recognition tasks for a single domain and a single observatility level.
	#

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
		content += str([x.h_value_wrong for x in self.problem_outputs.values()]) + '\n'
		content += str([x.hc_value_wrong for x in self.problem_outputs.values()]) + '\n'
		return content


class MethodOutput:

	#
	# The results for the set of goal recognition tasks for a single domain.
	#

	def __init__(self, method, domain_data):
		self.name = method
		self.domain_data = domain_data
		self.experiments = []
		raw_experiment = RawExperiment(domain_data.name + "-" + self.name, domain_data.observabilities)
		for obs in domain_data.observabilities:
			experiment = ExperimentOutput(obs)
			experiment.load(domain_data, raw_experiment)
			self.experiments.append(experiment)

	def print_table(self):
		content = "#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tPER\tTime\tTimeLP\tTimeFD\tVars\tConsts\tH\tHC\n"
		for experiment in self.experiments:
			content += experiment.print_stats()
		return content


class ObsStats:

	#
	# The results for the set of goal recognition tasks for a single observatility level.
	#

	def __init__(self, obs):
		self.level = obs
		self.points = dict()
		self.win = [0, 0, 0]  # better, worse, draw
		self.quads = [0, 0, 0, 0] # Q1, Q2, Q3, Q4
		self.axis = [0, 0, 0, 0, 0] # Origin, X left, X right, Y bottom, Y right

	def count_hvalues(experiments, problem):
		for h in range(len(p.hyps)):
			hc = [m.problem_outputs[p.name].scores[h][1] \
				if h in m.problem_outputs[p.name].scores else 100 \
				for m in experiments]
			line = ' '.join([str(x) for x in hc])
			if line in points:
				points[line] += 1
			else:
				points[line] = 1
			agr = [m.problem_outputs[p.name].agreement for m in experiments]
			if hc[0] > hc[1]:
				self.win[0] += 1
				if agr[0] > agr[1]:
					self.quads[2] += 1
				elif agr[1] > agr[0]:
					self.quads[1] += 1
				else:
					self.axis[1] += 1
			elif hc[1] > hc[0]:
				self.win[1] += 1
				if agr[0] > agr[1]:
					self.quads[3] += 1
				elif agr[1] > agr[0]:
					self.quads[0] += 1
				else:
					self.axis[2] += 1
			else:
				self.win[2] += 1
				if agr[0] > agr[1]:
					self.axis[3] += 1
				elif agr[1] > agr[0]:
					self.axis[4] += 1
				else:
					self.axis[0] += 1

		def print_points():
			return '\n'.join([line + " " + str(c) for line, c in self.points.items()])

		def print_stats(methods):
			content = methods[0] + " vs " + methods[1] + '\n'
			content += methods[0] + " higher than " + methods[1] + ": %.2f" % self.win[0] + "%\n"
			content += methods[1] + " higher than " + methods[0] + ": %.2f" % self.win[1] + "%\n"
			content += methods[0] + " equal to " + methods[1] + ": %.2f" % self.win[2] + "%\n"
			for i in range(0, 4):
				content += "Q%s: %s" % (i + 1, self.quads[i]) + '\n'
			content += "Axis X (left): %s" % self.axis[1] + '\n'
			content += "Axis X (right): %s" % self.axis[2] + '\n'
			content += "Axis Y (bottom): %s" % self.axis[3] + '\n'
			content += "Axis Y (top): %s" % self.axis[4] + '\n'
			content += "Origin: %s" % self.axis[0] + '\n'
			return content


class RawProblem:

	#
	# Output data for a single goal recognition task.
	#

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

	#
	# Output data for a single domain and a single observatility level.
	#

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
				if obs + "/" in problem.file:
					self.problems[obs].append(problem)
					break
		self.experiment_times = dict()
		for i in range(len(experiment_times)):
			self.experiment_times[observabilities[i]] = experiments[i]


def write_dat_files(all_domain_data, methods, observabilities, chart_name = None, scatter = True, stats = True):
	obs_stats = [ObsStats(o) for o in range(len(observabilities))]
	for domain_data in all_domain_data.values():
		method_outputs = [MethodOutput(method, domain_data) for method in methods]
		for o in range(len(observabilities)):
			method_experiments = [m.experiments[o] for m in method_outputs]
			for p in domain_data.data[observabilities[o]].values():
				obs_stats[o].count_hvalues(p, method_experiments)
	if not chart_name:
		chart_name = ' vs '.join(methods) 
	header = ' '.join(["x%s" % i for i in range(len(methods))]) + " w \n"
	for o in range(len(observabilities)):
		if scatter:
			content = obs_stats[o].print_points()
			with open("latex-charts/" + chart_name + "-" + observabilities[o] + "-scatter.dat", 'w') as f:
				f.write(header + content)
		if stats: 
			content = obs_stats[o].print_stats(methods)
			with open("latex-charts/" + chart_name + "-" + observabilities[o] + "-stats.dat", 'w') as f:
				f.write(content)


def write_txt_files(domain_data, methods):
	for domain_data in all_domain_data.values():
		for method in methods:
			method_output = MethodOutput(method, domain_data)
			with open("data-tables/" + domain_data.name + "-" + method + ".txt", 'w') as f:
				f.write(method_output.print_table())
			with open("data-charts/" + domain_data.name + "-" + method + ".txt", 'w') as f:
				for experiment in method_output.experiments:
					f.write(experiment.print_hdata())

if __name__ == '__main__':
	observabilities = ['10', '30', '50', '70', '100']
	base_path = '../goal-plan-recognition-dataset/'
	test = False
	if '-fast' in sys.argv:
		set_filter(True)
		dd.set_filter(True)
		sys.argv.remove('-fast')
	if '-test' in sys.argv:
		test = True
		sys.argv.remove('-test')
		base_path = 'experiments/'
	domains = dd.parse_domains(sys.argv[2:], test)
	all_domain_data = {}
	for d in domains:
		domain_data = dd.DomainData(d, observabilities)
		if os.path.exists("data-domains/" + d + ".txt"):
			domain_data.read("data-domains/")
		else:
			domain_data.load(base_path)
		all_domain_data[d] = domain_data
	methods = sys.argv[1]
	chart_name = None
	if methods == 'lm':
		methods = ["delta-cl", "delta-o-cl1"]
		chart_name = "LMC-vs-LMC+soft"
	elif methods == 'dr':
		methods = ["delta-o-cdt", "delta-o-cdto"]
		chart_name = "DEL+1-vs-DEL+2"
	elif methods == 'fl':
		methods = ["delta-cf1", "delta-o-cf17"]
		chart_name = "F1-vs-FOPxEIntra"
	else:
		methods = methods.split()

	if '-hvalues' in sys.argv:
		write_dat_files(all_domain_data, methods, observabilities[0:-2], \
			 chart_name, "-scatter" in sys.argv, "-stats" in sys.argv)
	else:
		write_txt_files(all_domain_data, methods)
