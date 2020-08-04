#!/usr/bin/python
import sys
import os
import math
import argparse

class DomainData:

	def __init__(self, observabilities):
		self.observabilities = observabilities
		self.total_problems = 0
		self.obs_data = dict()
		for obs in observabilities:
			self.obs_data[obs] = dict()
		self.num_lines = 0
		self.avg_data = dict()

	def read_approach_data(self, file, approach):
		file.readline() # Header
		sum_values = [0] * 10
		for obs in self.observabilities:
			line = file.readline().strip().split('\t')
			self.total_problems += int(line[0])
			values = [float(x) for x in line]
			self.obs_data[obs][approach] = values
			sum_values = [x + y for x, y in zip(sum_values, values)]
		self.avg_data[approach] = [x / len(self.observabilities) for x in sum_values]

	def get_avg_goals(self):
		sum_goals = 0
		problems = 0
		for approach_data in self.obs_data.values():
			for values in approach_data.values():
				sum_goals += values[3]
				problems += 1
		return sum_goals / problems if problems > 0 else float("nan")

	def get_avg_obs(self, obs):
		sum_obs = 0
		problems = 0
		approach_data = self.obs_data[obs]
		for values in approach_data.values():
			sum_obs += values[2]
			problems += 1
		return sum_obs / problems if problems > 0 else float("nan")

def average_values(all_domain_data, approach):
	sum_values = [0] * 10
	for domain_data in all_domain_data.values():
		if approach in domain_data.avg_data:
			sum_values = [x + y for x, y in zip(sum_values, domain_data.avg_data[approach])]
	return [x / len(all_domain_data.keys()) for x in sum_values]

def collect_data(file, domains, approaches, basepaths, observabilities):
	all_domain_data = dict()
	for domain_name in domains:
		domain_data = DomainData(observabilities)
		all_domain_data[domain_name] = domain_data
		for basepath, approach in zip(basepaths, approaches):
			path = basepath + "/" + domain_name + '-' + approach + '.txt'
			if not os.path.isfile(path):
				continue
			with open(path) as f:
				domain_data.read_approach_data(f, basepath + approach)
	return all_domain_data


def main(template, file, domains, approaches, basepaths):
	print("Tabulating data from %s for domains %s"%(basepaths,domains))
	observabilities = ['10', '30', '50', '70', '100']
	all_domain_data = collect_data(file, domains, approaches, basepaths, observabilities)

	content_table = ''

	for domain_name in domains:
		domain_name_4table = domain_name
		domain_name_4table = domain_name_4table.replace('-optimal', '')
		domain_name_4table = domain_name_4table.replace('-suboptimal', '')
		domain_name_4table = domain_name_4table.replace('-noisy', '')
		if 'intrusion-detection' in domain_name:
			domain_name_4table = domain_name_4table.replace("-detection", "")
		if 'blocks-world' in domain_name:
			domain_name_4table = domain_name_4table.replace("-world", "")
		if 'zeno-travel' in domain_name:
			domain_name_4table = domain_name_4table.replace("-travel", "")
		if 'easy-ipc-grid' in domain_name:
			domain_name_4table = domain_name_4table.replace("easy-", "")

		domain_data = all_domain_data[domain_name]
		
		content_table += '\n\\multirow{%s}{*}{\\rotatebox[origin=c]{90}{\\textsc{%s}} \\rotatebox[origin=c]{90}{(%s)}} & \\multirow{%s}{*}{%s} ' \
			% (len(observabilities), domain_name_4table, domain_data.total_problems, len(observabilities), round(domain_data.get_avg_goals(), 1))

		for obs in observabilities:
			content_table += '\n\t' + ('\\\\ & & ' if (obs != '10') else ' & ') + obs + '\t & ' + str(round(domain_data.get_avg_obs(obs), 2)) + '\n'
			for basepath, approach in zip(basepaths, approaches):
				content_table += '\n\t\t% ' + approach + ' - ' + obs + '% '
				if (basepath + approach) not in domain_data.obs_data[obs]:
					content_table += '\n\t\t& - & - & - & - \t \n'
					continue
				values = domain_data.obs_data[obs][basepath + approach]
				time = round(values[9], 3)
				accuracy = round(values[7] * 100, 1)
				spread = round(values[8], 2)
				ratio = 0 if (values[8] == 0) else round(100 * values[7] / values[8], 1)
				ar = round(values[4], 2)
				fpr = round(values[5], 2)
				fnr = round(values[6], 2)
				content_table += '\n\t\t& {0} & {1} & {2} & {3}'.format(time, ar, fpr, fnr)

				content_table += ' \t \n'
		content_table += ' \\\\ \hline'

	content_avg = ''
	for basepath, approach in zip(basepaths, approaches):
		values = average_values(all_domain_data, basepath + approach)
		time = round(values[9], 3)
		accuracy = round(values[7] * 100, 2)
		spread = round(values[8], 2)
		ratio = 0 if (values[8] == 0) else round(100 * values[7] / values[8], 2)
		ar = round(values[4], 2)
		fpr = round(values[5], 2)
		fnr = round(values[6], 2)
		content_avg += ' & {0} & {1} & {2} & {3}'.format(time, ar, fpr, fnr)

	latexContent = ''
	with open(template, 'r') as latex:
		latexContent = latex.read()
	latexContent = latexContent.replace('<TABLE_LP_RESULTS>', content_table)
	latexContent = latexContent.replace('<AVG_APPROACH>', content_avg)
	with open(file, 'w') as latex:
		latex.write(latexContent)
	os.system("pdflatex " + file)

if __name__ == '__main__' :
	default_path = '../results-new'
	#domains = ['blocks-world-optimal', 'depots-optimal', 'driverlog-optimal', 'dwr-optimal',\
	# 			'easy-ipc-grid-optimal', 'ferry-optimal', 'logistics-optimal',\
	# 			 'miconic-optimal', 'rovers-optimal', 'satellite-optimal', 'sokoban-optimal', 'zeno-travel-optimal']
	domains = ['blocks-world-optimal', 'easy-ipc-grid-optimal', 'logistics-optimal', 'sokoban-optimal']
	file = 'filters-optimal.tex'
	template = 'filters-template.tex'
	approaches = ['delta-h-c', 'delta-h-c-uncertainty', 'delta-h-c-f1', 'delta-h-c-f1-uncertainty', 'delta-h-c-f2', 'delta-h-c-f2-uncertainty']
	paths = [default_path] * 6

	parser = argparse.ArgumentParser(description="Generates LaTeX tables for plan recognition experiments")
	parser.add_argument('-d', '--domains', metavar="D", nargs='+', type=str, help="list of domains to tabulate data")
	parser.add_argument('-a', '--approaches', metavar="A", nargs='+', type=str, help="approaches to tabulate")
	parser.add_argument('-p', '--paths', metavar="P", nargs='+', type=str, help="base path of data result files for each approach")
	parser.add_argument('-t', '--template', metavar="T", nargs=1, type=str, help="template file")
	parser.add_argument('-f', '--file', metavar="F", nargs=1, type=str, help="result file")
	args = parser.parse_args()

	# Latex resulting files
	if args.file:
		file = args.file[0]
		if 'noisy' in file:
			domains = [name.replace("optimal", "optimal-noisy") for name in domains]
		if 'suboptimal' in file:
			domains = [name.replace("optimal", "suboptimal") for name in domains]
	if args.domains:
		domains = args.domains # Domains used

	# Latex template file
	if args.template:
		template = args.template[0]
		if 'previous' in template:
			paths = [default_path] * 7
			approaches = ['delta-h-c', 'delta-h-c-uncertainty', 'planrecognition-ramirezgeffner', 'goal_recognition-yolanda', 'planrecognition-heuristic_completion-0', 'planrecognition-heuristic_uniqueness-0', 'mirroring_landmarks']
		elif 'filters' in template:
			approaches = ['delta-h-c', 'delta-h-c-uncertainty', 'delta-h-c-f1', 'delta-h-c-f1-uncertainty', 'delta-h-c-f2', 'delta-h-c-f2-uncertainty']
		elif 'weighted' in template:
			approaches = ['delta-h-c', 'delta-h-c-uncertainty', 'weighted-c', 'weighted-c-uncertainty', 'weighted-delta-h-c', 'weighted-delta-h-c-uncertainty']
		elif 'constraints' in template:
			if 'single' in template:
				approaches = ['delta-h-c-cl', 'delta-h-c-cl-uncertainty', 'delta-h-c-cp', 'delta-h-c-cp-uncertainty', 'delta-h-c-cs', 'delta-h-c-cs-uncertainty']
			else:
				approaches = ['delta-h-c-cps', 'delta-h-c-cps-uncertainty', 'delta-h-c-cls', 'delta-h-c-cls-uncertainty', 'delta-h-c-clp', 'delta-h-c-clp-uncertainty']
	if args.approaches:
		approaches = args.approaches # Approaches in template

	if args.paths:
		paths=args.paths
	
	if len(paths) < len(approaches):
		paths += [default_path] * (len(approaches) - len(paths))

	main(template, file, domains, approaches, paths)