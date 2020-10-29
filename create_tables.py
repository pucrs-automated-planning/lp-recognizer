#!/usr/bin/env python2.7
#./create_tables.py -fast "delta-cd" "delta-clp" "delta-clp-uncertainty" "delta-cls" "delta-cl" "delta-cls-uncertainty" "delta-cl-uncertainty" "delta-cps" "delta-cp" "delta-cps-uncertainty" "delta-cp-uncertainty" "delta-cs" "delta-cs-uncertainty" "delta-o-cd" "delta-o-cl" "delta-o" "delta" "delta-uncertainty"

import os, sys, re

EXP_FILTER = False
def filter(name):
    if EXP_FILTER:
        return ("_2.tar" in name) or ("_3.tar" in name) or ("hyp-4" in name) or ("hyp-3" in name)
    else:
        return False

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


class RawResults:
	def __init__(self):
		self.hyps = {}
		self.solutions = {}
		self.true_solutions = {}
		self.true_hyps = {}
		self.obs = {}
		self.total_time = 0
		self.lp_time = 0
		self.fd_time = 0

	def read_problems(self, base_path, domain, obs):
		exp_path = domain + '/' + obs + '/'
		files = [file for file in os.listdir(base_path + exp_path) if file.endswith(".tar.bz2") and not filter(file)]
		for problem_file in files:
			problem = exp_path + problem_file
			unpack(base_path + problem)
			hyps = self.read_hyps()
			self.hyps[problem] = hyps
			self.true_hyps[problem] = self.read_real_hyp(hyps)
			self.true_solutions[problem] = self.read_solutions(hyps)
			self.obs[problem] = self.read_observations()
			self.solutions[problem] = set()
		self.num_problems = len(files)

	def read_hyps(self):
		hyps = set()
		with open("hyps.dat") as f:
			for line in f:
				atoms = [tok.strip().lower() for tok in line.split(',')]
				hyps.add(frozenset(atoms))
		return hyps

	def read_real_hyp(self, hyps):
		with open("real_hyp.dat") as f:
			atoms = frozenset([tok.strip().lower() for tok in f.readline().split(',')])
			for hyp in hyps:
				if hyp == atoms:
					return hyp
		print("No real hyp.")
		return None

	def read_solutions(self, hyps):
		goals = set()
		with open("solution.dat") as f:
			for line in f:
				atoms = [tok.strip().lower() for tok in re.findall("\(.*?\)", line)]
				goals.add(frozenset(atoms))
		return set([hyp for hyp in hyps if hyp in goals])

	def read_observations(self):
		observations = []
		with open("obs.dat") as f:
			for line in f:
				observations.append(line.strip().lower())
		return observations

	def clear(self):
		self.total_time = 0
		self.lp_time = 0
		self.fd_time = 0
		for problem in self.solutions.keys():
			self.solutions[problem] = set()

class Experiment:
	def __init__(self, obs, results):
		self.accuracy = 0.0
		self.spread  = 0.0
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
		self.total_time = results.total_time
		self.lp_time = results.lp_time
		self.fd_time = results.fd_time

	def add_problem(self, raw_obs_results, problem):
		print(problem)

		solution_set = raw_obs_results.solutions[problem]
		exact_solution_set = raw_obs_results.true_solutions[problem]

		self.num_obs += len(raw_obs_results.obs[problem])
		self.num_goals += len(raw_obs_results.hyps[problem])
		self.num_solutions += len(exact_solution_set)

		if raw_obs_results.true_hyps[problem] in solution_set:
			self.accuracy += 1
		self.spread += len(solution_set)

		total = float(len(exact_solution_set | solution_set))
		fp = float(len(solution_set - exact_solution_set))
		fn = float(len(exact_solution_set - solution_set))
		agr = (total - fp - fn) / total
		self.fpr += fp / total
		self.fnr += fn / total
		self.agreement += agr
		if agr == 1:
			self.perfect_agr += 1

	def print_content(self):
		num_problems = float(self.num_problems)
		file_content = "%s\t%s" % (int(self.num_problems), self.obs)

		file_content += "\t%2.1f" % (self.num_obs / num_problems)
		file_content += "\t%2.1f" % (self.num_goals / num_problems)
		file_content += "\t%2.1f" % (self.num_solutions / num_problems)

		file_content += "\t%2.2f" % (self.agreement / num_problems)
		file_content += "\t%2.2f" % (self.fpr / num_problems)
		file_content += "\t%2.2f" % (self.fnr / num_problems)
		file_content += "\t%2.2f" % (self.accuracy / num_problems)
		file_content += "\t%2.2f" % (self.spread / num_problems)
		file_content += "\t%s" % (self.perfect_agr)

		file_content += "\t%2.4f" % (self.total_time / num_problems)
		file_content += "\t%2.4f" % (self.lp_time / num_problems)
		file_content += "\t%2.4f" % (self.fd_time / num_problems)
		file_content += "\n"
		return file_content


def read_experiments(raw_results, domain, method, observabilities):
	for obs in observabilities:
		raw_results[obs].clear()
	current_results = None
	current_file = None
	reading_obs = 0
	print(domain + "-" + method + ".txt")
	with open(domain + "-" + method + ".success") as f:
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
			if filter(current_file):
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
				if len(line) >= 3:
					current_results.lp_time += float(line[2])
				if len(line) >= 4:
					current_results.fd_time += float(line[3])
			current_results.solutions[current_file] = set()
	experiments = []
	for obs in observabilities:
		#raw_results[obs].read_problems(base_path, domain, obs)
		exp = Experiment(obs, raw_results[obs])
		for problem in raw_results[obs].hyps.keys():
			exp.add_problem(raw_results[obs], problem)
		experiments.append(exp)
	return experiments


def write_domain_tables(base_path, domain, methods):
	print(domain)
	observabilities = ['10', '30', '50', '70', '100']
	raw_results = {}
	for obs in observabilities:
		raw_results[obs] = RawResults()
		raw_results[obs].read_problems(base_path, domain, obs)
	for method in methods:
		experiments = read_experiments(raw_results, domain, method, observabilities)
		with open(domain + "-" + method + ".txt", 'w') as f:
			f.write("#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tPER\tTime\tTimeLP\tTimeFD\n")
			for experiment in experiments:
				f.write(experiment.print_content())


if __name__ == '__main__':
	base_path = '../goal-plan-recognition-dataset'
	domains = [
	'blocks-world',
	'depots',
	'driverlog',
	'dwr',
	'easy-ipc-grid',
	'ferry',
	'logistics',
	'miconic',
	'rovers',
	'satellite',
	'sokoban',
	'zeno-travel'
	]
	domain_types = [
	'-optimal',
	'-optimal-old-noisy',
	'-suboptimal',
	'-suboptimal-old-noisy'
	]
	methods = sys.argv[1:]
	if methods[0] == '-test':
		base_path = 'experiments'
		domains = ['small-sokoban']
		domain_types = ['']
		methods = ['delta-o-cd', 'delta-cl']
	elif methods[0] == '-fast':
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
		methods = methods[1:]

	for domain in domains:
		for dt in domain_types:
			write_domain_tables(base_path + '/', domain + dt, methods)

