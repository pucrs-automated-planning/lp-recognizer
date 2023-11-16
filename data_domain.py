#!/usr/bin/env python3

##
## Generate domain summary tables (data-domains folder).
##

## Uses:
# For especific domains:
# ./data_domain.py blocks-world-optimal depots-optimal [...] [-fast]
# For all domains of a data set type:
# ./data_domain.py optimal suboptimal [...] [-fast]
# For all domains of a problem base:
# ./data_domain.py blocks-world depots [...] [-fast]
# For all domains:
# ./data_domain.py all [-fast]
##

import os, sys, re

EXP_FILTER = False
def filter(name):
    if EXP_FILTER:
        return ("_2.tar" in name) or ("_3.tar" in name) or ("hyp-4" in name) or ("hyp-3" in name)
    else:
        return False
def set_filter(value):
	EXP_FILTER = value


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


class ProblemData:

	def __init__(self, filename):
		self.name = filename

	def load(self, base_path):
		unpack(base_path + self.name)
		self.obs = self.load_observations() # list of string
		self.hyps = self.load_hyps() # list of set of string
		self.true_hyp = self.load_real_hyp() # set of string
		self.solution = self.load_solution() # list of set of string
		self.solution.remove(self.true_hyp)
		self.solution = [self.true_hyp] + self.solution

	def load_hyps(self):
		hyps = []
		hyp_check = set()
		with open("hyps.dat") as f:
			for line in f:
				atoms = frozenset([tok.strip().lower() for tok in line.split(',')])
				if atoms in hyp_check:
					continue
				hyp_check.add(atoms)
				hyps.append(atoms)
		return hyps

	def load_real_hyp(self):
		with open("real_hyp.dat") as f:
			atoms = frozenset([tok.strip().lower() for tok in f.readline().split(',')])
			return atoms

	def load_solution(self):
		hyps = []
		with open("solution.dat") as f:
			for line in f:
				atoms = [tok.strip().lower() for tok in re.findall("\(.*?\)", line.strip())]
				hyps.append(frozenset(atoms))
		return hyps

	def load_observations(self):
		observations = []
		with open("obs.dat") as f:
			for line in f:
				observations.append(line.strip().lower())
		return observations

	def get_hyp_indexes(self):
		return range(len(self.hyps))

	def get_solution_indexes(self):
		solution = [] # list of indexes
		for i in range(0, len(self.hyps)):
			if self.hyps[i] in self.solution:
				solution.append(i)
		return solution

	def get_true_hyp_index(self):
		return self.hyps.index(self.true_hyp)

	def print_header(self):
		return "{0} {1} {2} {3}".format(self.name, len(self.obs), len(self.hyps), len(self.solution))

	def print_obs(self):
		return ','.join(self.obs)

	def print_hyps(self):
		hyps = [','.join(atoms) for atoms in self.hyps]
		return ';'.join(hyps)

	def print_solution(self):
		hyps = [','.join(atoms) for atoms in self.solution]
		return ';'.join(hyps)


class DomainData:

	def __init__(self, name, observabilities):
		self.name = name
		self.observabilities = observabilities
		self.data = {}

	def load(self, base_path):
		for obs in self.observabilities:
			exp_path = self.name + '/' + obs + '/'
			files = [file for file in os.listdir(base_path + exp_path) if file.endswith(".tar.bz2") and not filter(file)]
			data = dict()
			for problem_file in files:
				problem = exp_path + problem_file
				problem_data = ProblemData(problem)
				problem_data.load(base_path)
				data[problem] = problem_data
			self.data[obs] = data

	def read(self, path = ""):
		file = open(path + self.name + ".txt", 'r')
		for obs in self.observabilities:
			line = file.readline()
			num_problems = int(line.split(" ")[0])
			data = dict()
			for i in range(num_problems):
				name = file.readline().strip().split()[0]
				problem_data = ProblemData(name)
				problem_data.obs = file.readline().strip().split(',')
				problem_data.hyps = [frozenset(atoms.split(',')) for atoms in file.readline().strip().split(';')]
				solution = [frozenset(atoms.split(',')) for atoms in file.readline().strip().split(';')]
				problem_data.solution = [hyp for hyp in problem_data.hyps if hyp in solution]
				problem_data.true_hyp = solution[0]
				data[name] = problem_data
			self.data[obs] = data
		file.close()

	def print_header(self, obs):
		num_problems = float(len(self.data[obs]))
		num_obs = sum([len(p.obs) for p in self.data[obs].values()]) / num_problems
		num_hyps = sum([len(p.hyps) for p in self.data[obs].values()]) / num_problems
		num_solutions = sum([len(p.solution) for p in self.data[obs].values()]) / num_problems
		return "{0} {1} {2} {3} {4}\n".format(len(self.data[obs]), obs, num_obs, num_hyps, num_solutions)

	def print_problems(self):
		content = ""
		for obs in self.observabilities:
			content += self.print_header(obs)
			for p in self.data[obs].values():
				content += p.print_header() + '\n'
				content += p.print_obs() + '\n'
				content += p.print_hyps() + '\n'
				content += p.print_solution() + '\n'
		return content

	def write(self, path = ""):
		file = open(path + self.name + ".txt", 'w')
		file.write(self.print_problems())
		file.close()


def parse_domains(domain_names, test = False):
	if test:
		base_domains = ["small-sokoban"]
	else:
		base_domains = [
			'blocks-world', 
			'depots', 
			'driverlog', 
			'dwr', 
			'rovers', 
			'sokoban'
		]
		if not EXP_FILTER:
			base_domains += [
				'easy-ipc-grid', 
				'ferry', 
				'logistics', 
				'miconic', 
				'satellite', 
				'zeno-travel'
			]
	dataset_types = ['optimal', 'suboptimal', 'optimal-old-noisy', 'suboptimal-old-noisy']
	all_domains = []
	for domain_name in domain_names:
		if domain_name == 'all':
			domains = []
			for dt in dataset_types:
				domains += [d + "-" + dt for d in base_domains]
		elif domain_name == 'optimal-all':
			domains = [d + "-optimal" for d in base_domains]
			domains += [d + "-optimal-old-noisy" for d in base_domains]
		elif domain_name == 'suboptimal-all':
			domains = [d + "-suboptimal" for d in base_domains]
			domains += [d + "-suboptimal-old-noisy" for d in base_domains]
		elif domain_name == 'basic-all':
			domains = [d + "-optimal" for d in base_domains]
			domains += [d + "-suboptimal" for d in base_domains]
		elif domain_name == 'noisy-all':
			domains = [d + "-optimal-old-noisy" for d in base_domains]
			domains += [d + "-suboptimal-old-noisy" for d in base_domains]
		elif domain_name in dataset_types:
			domains = [d + "-" + domain_name for d in base_domains]
		elif domain_name in base_domains:
			domains = [domain_name + "-" + dt for dt in dataset_types]
		else:
			domains = [domain_name]
		all_domains += domains
	return all_domains

if __name__ == '__main__':
	observabilities = ['10', '30', '50', '70', '100']
	base_path = '../goal-plan-recognition-dataset/'
	test = False
	replace = False
	if '-fast' in sys.argv:
		EXP_FILTER = True
		sys.argv.remove('-fast')
	if '-test' in sys.argv:
		test = True
		sys.argv.remove('-test')
		base_path = 'experiments/'
	if '-replace' in sys.argv:
		replace = True
		sys.argv.remove('-replace')
	domains = parse_domains(sys.argv[1:], test)
	for domain in domains:
		domain_data = DomainData(domain, observabilities)
		if os.path.exists("data-domains/%s.txt" % domain) and not replace:
			domain_data.read("data-domains/")
			print(domain_data.print_problems())
		else:
			domain_data.load(base_path)
			domain_data.write("data-domains/")