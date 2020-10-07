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
		sum_values = [0] * 13
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

	def get_avg_solutions(self, obs):
		sum_s = 0
		problems = 0
		approach_data = self.obs_data[obs]
		for values in approach_data.values():
			sum_s += values[4]
			problems += 1
		return sum_s / problems if problems > 0 else float("nan")

def average_values(all_domain_data, approach):
	sum_values = [0] * 13
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
		domain_data.total_problems /= len(approaches)
	return all_domain_data


def get_latex_content(file, domains, approaches, basepaths):
	print("Tabulating data from %s for domains %s"%(basepaths,domains))
	observabilities = ['10', '30', '50', '70', '100']
	all_domain_data = collect_data(file, domains, approaches, basepaths, observabilities)

	content_table = ''

	for domain_name in domains:
		domain_name_4table = domain_name
		domain_name_4table = domain_name_4table.replace('-optimal', '')
		domain_name_4table = domain_name_4table.replace('-suboptimal', '')
		domain_name_4table = domain_name_4table.replace('-noisy', '')
		domain_name_4table = domain_name_4table.replace('-old', '')
		if 'intrusion-detection' in domain_name:
			domain_name_4table = domain_name_4table.replace("-detection", "")
		if 'blocks-world' in domain_name:
			domain_name_4table = domain_name_4table.replace("-world", "")
		if 'zeno-travel' in domain_name:
			domain_name_4table = domain_name_4table.replace("-travel", "")
		if 'easy-ipc-grid' in domain_name:
			domain_name_4table = domain_name_4table.replace("easy-", "")

		domain_data = all_domain_data[domain_name]
		
		content_table += '\n\\multirow{%s}{*}{ \\rotatebox[origin=c]{90}{\\textsc{%s}} } ' \
			% (len(observabilities), domain_name_4table)

		for obs in observabilities:
			len_obs = str(round(domain_data.get_avg_obs(obs), 2))
			len_solutions = str(round(domain_data.get_avg_solutions(obs), 2))
			content_table += '\n' + ('\\\\ & ' if (obs != '10') else ' & ') + obs + '\n'

			# Find best
			best_ar = 0
			best_acc = 0
			best_spread = float("inf")
			for basepath, approach in zip(basepaths, approaches):
				if (basepath + approach) not in domain_data.obs_data[obs]:
					continue
				values = domain_data.obs_data[obs][basepath + approach]
				accuracy = round(values[8], 2)
				if accuracy > best_acc:
					best_acc = accuracy
				spread = round(values[9], 2)
				if spread < best_spread:
					best_spread = spread
				ar = round(values[5], 2)
				if ar > best_ar:
					best_ar = ar

			# Write
			for basepath, approach in zip(basepaths, approaches):
				if (basepath + approach) not in domain_data.obs_data[obs]:
					content_table += '& - & - & - & -'
					continue
				values = domain_data.obs_data[obs][basepath + approach]
				if len(values) <= 11:
					time = round(values[10], 3)
				else:
					py_time = values[10] - values[12]
					lp_time = values[11]
					time = round(lp_time + py_time, 3)
				accuracy = round(values[8], 2)
				spread = round(values[9], 2)
				ratio = 0 if (values[9] == 0) else round(100 * values[8] / values[9], 1)
				ar = round(values[5], 2)
				fpr = round(values[6], 2)
				fnr = round(values[7], 2)
				if ar == best_ar:
					ar = "\\textbf{%s}" % ar
				#if accuracy == best_acc:
				#	accuracy = "\\textbf{%s}" % accuracy
				#if spread == best_spread:
				#	spread = "\\textbf{%s}" % spread
				content_table += '& {0} & {1} & {2} & {3}'.format(time, ar, accuracy, spread)
		if domain_name == domains[-1]:
			content_table += ' \\\\ \midrule'
		else:
			content_table += ' \\\\ \hline'

	content_avg = ''
	# Find best
	best_ar = 0
	best_acc = 0
	best_spread = float("inf")
	for basepath, approach in zip(basepaths, approaches):
		values = average_values(all_domain_data, basepath + approach)
		accuracy = round(values[8], 2)
		if accuracy > best_acc:
			best_acc = accuracy
		spread = round(values[9], 2)
		if spread < best_spread:
			best_spread = spread
		ar = round(values[5], 2)
		if ar > best_ar:
			best_ar = ar

	for basepath, approach in zip(basepaths, approaches):
		values = average_values(all_domain_data, basepath + approach)
		if len(values) <= 11:
			time = round(values[10], 3)
		else:
			py_time = values[10] - values[12]
			lp_time = values[11]
			time = round(lp_time + py_time, 3)
		accuracy = round(values[8], 2)
		spread = round(values[9], 2)
		ratio = 0 if (values[9] == 0) else round(100 * values[8] / values[9], 2)
		ar = round(values[5], 2)
		fpr = round(values[6], 2)
		fnr = round(values[7], 2)
		if ar == best_ar:
			ar = "\\textbf{%s}" % ar
		#if accuracy == best_acc:
		#	accuracy = "\\textbf{%s}" % accuracy
		#if spread == best_spread:
		#	spread = "\\textbf{%s}" % spread
		content_avg += ' & {0} & {1} & {2} & {3}'.format(time, ar, accuracy, spread)

	return content_table, content_avg

def main(template, file, domains, approaches, basepaths):
	# Get content.
	content_table, content_avg = get_latex_content(file, domains, approaches, basepaths)
	domains = [name.replace("optimal", "suboptimal") for name in domains]
	content_table_2, content_avg_2 = get_latex_content(file, domains, approaches, basepaths)
	# Write latex
	latexContent = ''
	with open(template, 'r') as latex:
		latexContent = latex.read()
	if "noisy" in domains[0]:
		latexContent = latexContent.replace("Optimal", "Optimal, Noisy")
		latexContent = latexContent.replace("Basic", "Noisy")
	latexContent = latexContent.replace('<TABLE_LP_RESULTS>', content_table)
	latexContent = latexContent.replace('<AVG_APPROACH>', content_avg)
	latexContent = latexContent.replace('<TABLE_LP_RESULTS_2>', content_table_2)
	latexContent = latexContent.replace('<AVG_APPROACH_2>', content_avg_2)
	with open(file, 'w') as latex:
		latex.write(latexContent)
	os.system("pdflatex " + file)

if __name__ == '__main__' :
	default_path = '../results-new'
	domains = [
		'blocks-world-optimal',
		'depots-optimal',
		'driverlog-optimal',
		'dwr-optimal',
		'easy-ipc-grid-optimal',
		'ferry-optimal',
		'logistics-optimal',
	 	'miconic-optimal',
	 	'rovers-optimal',
	 	'satellite-optimal',
	 	'sokoban-optimal',
	 	'zeno-travel-optimal'
	 ]
	file = 'all.tex'
	template = 'all-template.tex'
	approaches = [
		'delta-h-c', 
		'delta-h-c-uncertainty', 
		'delta-h-c-f2', 'rg2009', 
		'lm_hc0', 
		'lm_hc10', 
		'lm_hc20', 
		'lm_hc30', 
		'fgr2015', 
		'ml2018'
	]
	paths = [default_path] * 10

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
		if 'old-noisy' in file:
			domains = [name.replace("optimal", "optimal-old-noisy") for name in domains]
		elif 'noisy' in file:
			domains = [name.replace("optimal", "optimal-noisy") for name in domains]
	if args.domains:
		domains = args.domains # Domains used

	# Latex template file
	if args.template:
		template = args.template[0]
		if 'constraints' in template:
			approaches = [
				'delta-h-c-cs',
				'delta-h-c-cl',
				'delta-h-c-cp',
				'delta-h-c-cls',
				'delta-h-c-clp', 
				'delta-h-c-cps',
				'delta-h-c'
			]
			paths = [default_path] * 7
	if args.approaches:
		approaches = args.approaches # Approaches in template

	if args.paths:
		paths=args.paths
	
	if len(paths) < len(approaches):
		paths += [default_path] * (len(approaches) - len(paths))

	main(template, file, domains, approaches, paths)