#!/usr/bin/env python2.7
#./create_tables.py "delta-h-c-cd" "delta-h-c-clp" "delta-h-c-clp-uncertainty" "delta-h-c-cls" "delta-h-c-cl" "delta-h-c-cls-uncertainty" "delta-h-c-cl-uncertainty" "delta-h-c-cps" "delta-h-c-cp" "delta-h-c-cps-uncertainty" "delta-h-c-cp-uncertainty" "delta-h-c-cs" "delta-h-c-cs-uncertainty" "delta-h-c-o-cd" "delta-h-c-o-cl" "delta-h-c-o" "delta-h-c" "delta-h-c-uncertainty"

import os, sys, re

EXP_FILTER = True

def unpack(exp_file):
	os.system('tar jxvf %s' % exp_file)
	solution_file = exp_file.replace("tar.bz2", "solution")
	if os.path.exists(solution_file):
		os.system("cp %s solution.dat" % solution_file)
	else:
		if "noisy" in exp_file:
			solution_file_original = solution_file.replace("-noisy_0.2", "").replace("-noisy", "").replace("-old", "").replace("_noisy", "")
			solution_file_original = solution_file_original.replace("full_1", "full").replace("full_2", "full").replace("full_3", "full")
			if os.path.exists(solution_file_original):
				os.system("cp %s solution.dat" % solution_file_original)
			else:
				print("No solution file: %s" % solution_file)
				print("No solution file: %s" % solution_file_original)
				os.system("cp real_hyp.dat solution.dat")
				#exit(-1)
		else:
			print("No solution file: %s" % solution_file)
			os.system("cp real_hyp.dat solution.dat")
			#exit(-1)


def read_hyps():
	hyps = set()
	with open("hyps.dat") as f:
		for line in f:
			atoms = [tok.strip().lower() for tok in line.split(',')]
			hyps.add(frozenset(atoms))
	return hyps

def read_real_hyp(hyps):
	with open("real_hyp.dat") as f:
		atoms = frozenset([tok.strip().lower() for tok in f.readline().split(',')])
		for hyp in hyps:
			if hyp == atoms:
				return hyp
	print("No real hyp.")
	return None

def read_solutions(hyps):
	goals = set()
	with open("solution.dat") as f:
		for line in f:
			atoms = re.findall("\(.*?\)", line)
			atoms = [tok.strip().lower() for tok in atoms]
			goals.add(frozenset(atoms))
	return set([hyp for hyp in hyps if hyp in goals])

def read_observations():
	observations = []
	with open("obs.dat") as f:
		for line in f:
			observations.append(line.strip())
	return observations

class RawResults:
	def __init__(self):
		self.hyps = {}
		self.solutions = {}
		self.true_solutions = {}
		self.true_hyps = {}
		self.num_obs = {}
		self.total_time = 0

	def read_problems(self, base_path, domain, obs):
		exp_path = domain + '/' + obs + '/'
		files = [file for file in os.listdir(base_path + exp_path) if file.endswith(".tar.bz2")]
		if EXP_FILTER:
			files = [file for file in files if "_2.tar" not in file and "_3.tar" not in file]
		for problem_file in files:
			problem = exp_path + problem_file
			unpack(base_path + problem)
			hyps = read_hyps()
			self.hyps[problem] = hyps
			self.true_hyps[problem] = read_real_hyp(hyps)
			self.true_solutions[problem] = read_solutions(hyps)
			self.num_obs[problem] = len(read_observations())
			self.solutions[problem] = set()
		self.num_problems = len(files)

	def clear(self):
		self.total_time = 0
		for problem in self.solutions.keys():
			self.solutions[problem] = set()

class Experiment:
	def __init__(self, obs, results):
		self.multi_correct = 0.0
		self.multi_spread  = 0.0
		self.num_goals = 0.0
		self.num_obs = 0.0
		self.num_solutions = 0.0
		self.total_time = 0.0
		self.fpr = 0.0
		self.fnr = 0.0
		self.agreement = 0.0
		self.perfect_agr = 0
		self.obs = obs
		self.num_problems = results.num_problems
		self.total_time = results.total_time / self.num_problems

	def add_problem(self, raw_obs_results, problem):
		print(problem)

		self.num_goals += len(raw_obs_results.hyps[problem])
		self.num_obs += raw_obs_results.num_obs[problem]

		solution_set = raw_obs_results.true_solutions[problem]
		self.num_solutions += len(solution_set)

		if raw_obs_results.true_hyps[problem] in raw_obs_results.solutions[problem]:
			self.multi_correct += 1
		self.multi_spread += len(raw_obs_results.solutions[problem])

		total = float(len(solution_set | raw_obs_results.solutions[problem]))
		fp = float(len(raw_obs_results.solutions[problem] - solution_set))
		fn = float(len(solution_set - raw_obs_results.solutions[problem]))
		self.fpr += fp / total
		self.fnr += fn / total
		self.agreement += (total - fp - fn) / total
		if total == len(solution_set) and total == len(raw_obs_results.solutions[problem]):
				self.perfect_agr += 1

	def print_content(self):
		num_problems = self.num_problems
		file_content = "%s\t%s" % (int(num_problems), self.obs)
		file_content += "\t%2.2f" % (self.num_obs / num_problems)
		file_content += "\t%2.2f" % (self.num_goals / num_problems)
		file_content += "\t%2.2f" % (self.num_solutions / num_problems)
		file_content += "\t%2.2f" % (self.agreement / num_problems)
		file_content += "\t%2.2f" % (self.fpr / num_problems)
		file_content += "\t%2.2f" % (self.fnr / num_problems)
		file_content += "\t%2.2f" % (self.multi_correct / num_problems)
		file_content += "\t%2.2f" % (self.multi_spread / num_problems)
		file_content += "\t%2.2f" % (self.perfect_agr)
		file_content += "\t%2.2f" % (self.total_time / num_problems)
		file_content += "\n"
		return file_content

def read_raw_results(base_path, domain):
	raw_results = {}
	for obs in observabilities:
		raw_results[obs] = RawResults()
		raw_results[obs].read_problems(base_path, domain, obs)
	return raw_results

def read_experiments(raw_results, domain, method, observabilities):
	for obs in observabilities:
		raw_results[obs].clear()
	current_results = None
	current_file = None
	reading_obs = 0
	print(domain + "-" + method + ".txt")
	with open("solutions/" + domain + "-" + method + ".success") as f:
		for line in f:
			if line.startswith(">"):
				if current_file is None:
					continue
				atoms = frozenset([tok.strip().lower() for tok in line.replace("> ", "").split(',')])
				for hyp in current_results.hyps[current_file]:
					if atoms == hyp:
						current_results.solutions[current_file].add(hyp)
						break
				continue
			line = line.split(":")
			current_file = line[0].strip().replace("pb", "p")
			if EXP_FILTER and ("_2.tar" in current_file or "_3.tar" in current_file):
				current_file = None
				continue
			if current_file[0].isdigit():
				raw_results[observabilities[reading_obs]].total_time += float(line) * current_results.num_problems
				reading_obs += 1
			for obs in observabilities:
				print(obs + "/", line[0])
				if obs + "/" in line[0]:
					current_results = raw_results[obs]
					break
			if len(line) > 1 and line[1].strip()[0].isdigit():
				current_results.total_time += float(line[1])
			current_results.solutions[current_file] = set()
	experiments = []
	for obs in observabilities:
		#raw_results[obs].read_problems(base_path, domain, obs)
		exp = Experiment(obs, raw_results[obs])
		for problem in raw_results[obs].hyps.keys():
			exp.add_problem(raw_results[obs], problem)
		experiments.append(exp)
	return experiments

def write_table(experiments, observabilities, file_name):
	with open("results-small/" + file_name, 'w') as f:
		f.write("#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tPER\tTime\n")
		for experiment in experiments:
			f.write(experiment.print_content())

if __name__ == '__main__':
	base_path = '../goal-plan-recognition-dataset'
	domains = [
	'blocks-world',
	'depots',
	'driverlog',
	'dwr',
	#'easy-ipc-grid',
	#'ferry',
	#'logistics',
	#'miconic',
	'rovers',
	#'satellite',
	'sokoban',
	#'zeno-travel'
	]
	observabilities = ['10', '30', '50', '70', '100']
	domain_types = [
	'-optimal',
	#'-optimal-noisy',
	#'-optimal-old-noisy',
	'-suboptimal',
	#'-suboptimal-noisy',
	#'-suboptimal-old-noisy'
	]
	methods = sys.argv[1:]
	if methods[0] == 'test':
		base_path = 'experiments'
		domains = ['small-sokoban']
		domain_types = ['']
		methods = ['delta-h-c-o-cd', 'delta-h-c-cl']

	for domain in domains:
		for dt in domain_types:
			print(domain + dt)
			raw_results = read_raw_results(base_path + "/", domain + dt)
			for method in methods:
				experiments = read_experiments(raw_results, domain + dt, method, observabilities)
				write_table(experiments, observabilities, domain + dt + "-" + method + ".txt")

