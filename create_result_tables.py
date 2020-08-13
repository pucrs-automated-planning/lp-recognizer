import os, sys, re

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
		else:
			print("No solution file: %s" % solution_file)
			os.system("cp real_hyp.dat solution.dat")


def read_hyps():
	hyps = set()
	with open("hyps.dat") as f:
		for line in f:
			atoms = [tok.strip() for tok in line.split(',')]
			hyps.add(frozenset(atoms))
	return hyps

def read_real_hyp(hyps):
	with open("real_hyp.dat") as f:
		atoms = frozenset([tok.strip() for tok in f.readline().split(',')])
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
		self.obs = obs
		self.num_problems = results.num_problems
		self.total_time = results.total_time / self.num_problems

	def add_problem(self, raw_obs_results, problem):
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

	def print_content(self):
		num_problems = self.num_problems
		file_content = "%s\t%s\t%s\t%s\t%s" % (int(num_problems), self.obs, self.num_obs / num_problems, self.num_goals / num_problems, self.num_solutions / num_problems)
		file_content += "\t%2.4f" % (self.agreement / num_problems)
		file_content += "\t%2.4f" % (self.fpr / num_problems)
		file_content += "\t%2.4f" % (self.fnr / num_problems)
		file_content += "\t%2.4f" % (self.multi_correct / num_problems)
		file_content += "\t%2.4f" % (self.multi_spread / num_problems)
		file_content += "\t%2.4f" % (self.total_time / num_problems)
		file_content += "\n"
		return file_content

def read_experiments(base_path, domain, method, observabilities):
	raw_results = {}
	for obs in observabilities:
		raw_results[obs] = RawResults()
		raw_results[obs].read_problems(base_path, domain, obs)
	current_results = None
	current_file = None
	reading_obs = 0
	print(method + "-" + domain + ".txt")
	with open(method + "-" + domain + ".txt") as f:
		for line in f:
			if line.startswith(">"):
				atoms = frozenset([tok.strip() for tok in line.replace("> ", "").split(',')])
				for hyp in current_results.hyps[current_file]:
					if atoms == hyp:
						current_results.solutions[current_file].add(hyp)
						break
				continue
			line = line.split(":")
			current_file = line[0]
			if current_file.isdigit():
				raw_results[observabilities[reading_obs]].total_time += float(line)
				reading_obs += 1
			for obs in observabilities:
				print(obs + "/", line[0])
				if obs + "/" in line[0]:
					current_results = raw_results[obs]
					break
			if len(line) > 1 and line[1].strip().isdigit():
				current_results.total_time += float(line[1]) * current_results.num_problems
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
	with open("results/" + file_name, 'w') as f:
		f.write("#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tTime\n")
		for experiment in experiments:
			f.write(experiment.print_content())

if __name__ == '__main__':
	base_path = sys.argv[1]
	method = sys.argv[2]
	domains = [
	'blocks-world-optimal',
	'easy-ipc-grid-optimal',
	'logistics-optimal',
	'miconic-optimal',
	'rovers-optimal',
	'sokoban-optimal',
	'blocks-world-suboptimal',
	'easy-ipc-grid-suboptimal',
	'logistics-suboptimal',
	'miconic-suboptimal',
	'rovers-suboptimal',
	'sokoban-suboptimal',
	'blocks-world-optimal-old-noisy',
	'easy-ipc-grid-optimal-old-noisy',
	'logistics-optimal-old-noisy',
	'miconic-optimal-old-noisy',
	'rovers-optimal-old-noisy',
	'sokoban-optimal-old-noisy',
	'blocks-world-suboptimal-old-noisy',
	'easy-ipc-grid-suboptimal-old-noisy',
	'logistics-suboptimal-old-noisy',
	'miconic-suboptimal-old-noisy',
	'rovers-suboptimal-old-noisy',
	'sokoban-suboptimal-old-noisy',
	]
	observabilities = ['10', '30', '50', '70', '100']
	for domain in domains:
		experiments = read_experiments(base_path + "/", domain, method, observabilities)
	   	write_table(experiments, observabilities, domain + "-" + method + ".txt")