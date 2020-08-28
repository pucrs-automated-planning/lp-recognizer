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
		sum_values = [0] * 11
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

def average_values(all_domain_data, approach, dt):
	sum_values = [0] * 11
	for name, domain_data in all_domain_data.items():
		if dt not in name:
			continue
		if approach in domain_data.avg_data:
			sum_values = [x + y for x, y in zip(sum_values, domain_data.avg_data[approach])]
	return [x / len(all_domain_data.keys()) for x in sum_values]

def collect_data(file, domains, approaches, basepaths, observabilities):
	all_domain_data = dict()
	for domain in domains:
		for dt in ['-optimal', '-suboptimal']:
			domain_name = domain+dt
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
		if 'intrusion-detection' in domain_name:
			domain_name_4table = domain_name_4table.replace("-detection", "")
		if 'blocks-world' in domain_name:
			domain_name_4table = domain_name_4table.replace("-world", "")
		if 'zeno-travel' in domain_name:
			domain_name_4table = domain_name_4table.replace("-travel", "")
		if 'easy-ipc-grid' in domain_name:
			domain_name_4table = domain_name_4table.replace("easy-", "")

		domain_data = all_domain_data[domain_name+"-optimal"]
		content_table += '\\multirow{%s}{*}{ \\rotatebox[origin=c]{90}{\\textsc{%s}} } & \\multirow{%s}{*}{%s} ' \
			% (len(observabilities), domain_name_4table, len(observabilities), round(domain_data.get_avg_goals(), 1))

		for obs in observabilities:
			content_table += '\n'
			if obs != '10':
				content_table += '\\\\ &'
			print_obs = True
			for dt in ['-optimal', '-suboptimal']:
				domain_data = all_domain_data[domain_name+dt]

				if print_obs:
					content_table += ' & ' + obs
					print_obs = False

				len_obs = str(round(domain_data.get_avg_obs(obs), 2))
				len_solutions = str(round(domain_data.get_avg_solutions(obs), 2))
				content_table +=' & ' + len_obs + ' & ' + len_solutions + '\n'

				# Find best
				best_ar = 0
				for basepath, approach in zip(basepaths, approaches):
					if (basepath + approach) not in domain_data.obs_data[obs]:
						continue
					values = domain_data.obs_data[obs][basepath + approach]
					ar = round(values[5], 2)
					if ar > best_ar:
						best_ar = ar

				# Write
				for basepath, approach in zip(basepaths, approaches):
					content_table += '\n% ' + approach + ' - ' + obs + '% \n'
					values = domain_data.obs_data[obs][basepath + approach]
					ar = round(values[5], 2)
					if ar == best_ar:
						ar = "\\textbf{%s}" % ar
					content_table += ' & ' + str(ar)
		content_table += ' \\\\ \hline'

	content_avg = ''
	for dt in ['-optimal', '-suboptimal']:
		# Find best
		content_avg += ' & & '
		best_ar = 0
		for basepath, approach in zip(basepaths, approaches):
			values = average_values(all_domain_data, basepath + approach, dt)
			ar = round(values[5], 2)
			if ar > best_ar:
				best_ar = ar
		for basepath, approach in zip(basepaths, approaches):
			values = average_values(all_domain_data, basepath + approach, dt)
			ar = round(values[5], 2)
			if ar == best_ar:
				ar = "\\textbf{%s}" % ar
			content_avg += ' & ' + str(ar)

	return content_table, content_avg

def main(template, file, domains, approaches, basepaths):
	# Get content.
	content_table, content_avg = get_latex_content(file, domains, approaches, basepaths)
	# Write latex
	latexContent = ''
	with open(template, 'r') as latex:
		latexContent = latex.read()
	latexContent = latexContent.replace('CONTENT', content_table)
	latexContent = latexContent.replace('AVERAGE', content_avg)
	with open(file, 'w') as latex:
		latex.write(latexContent)
	os.system("pdflatex " + file)

if __name__ == '__main__' :
	default_path = '../results-new'
	domains = ['blocks-world', 'easy-ipc-grid', 'logistics', 'miconic', 'rovers', 'satellite', 'sokoban']
	file = 'constraints.tex'
	template = 'constraints-template.tex'
	approaches = ['delta-h-c-cs', 'delta-h-c-cl', 'delta-h-c-cp', 'delta-h-c-clp', 'delta-h-c-cps', 'delta-h-c-cls']
	paths = [default_path] * 6

	parser = argparse.ArgumentParser(description="Generates LaTeX tables for plan recognition experiments")
	parser.add_argument('-d', '--domains', metavar="D", nargs='+', type=str, help="list of domains to tabulate data")
	parser.add_argument('-a', '--approaches', metavar="A", nargs='+', type=str, help="approaches to tabulate")
	parser.add_argument('-p', '--paths', metavar="P", nargs='+', type=str, help="base path of data result files for each approach")
	parser.add_argument('-t', '--template', metavar="T", nargs=1, type=str, help="template file")
	parser.add_argument('-f', '--file', metavar="F", nargs=1, type=str, help="result file")
	args = parser.parse_args()

	main(template, file, domains, approaches, paths)