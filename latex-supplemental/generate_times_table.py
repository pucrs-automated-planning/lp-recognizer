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

def average_values(all_domain_data, approach, dt):
	sum_values = [0] * 13
	for name, domain_data in all_domain_data.items():
		if dt not in name:
			continue
		if approach in domain_data.avg_data:
			sum_values = [x + y for x, y in zip(sum_values, domain_data.avg_data[approach])]
	return [x / len(all_domain_data.keys()) for x in sum_values]


def collect_data(file, domains, approaches, observabilities, dt):
	all_domain_data = dict()
	for domain in domains:
		# No noise
		domain_name = domain+dt
		domain_data = DomainData(observabilities)
		all_domain_data[domain_name] = domain_data
		for approach in approaches:
			path = '../results/' + domain_name + '-' + approach + '.txt'
			if not os.path.isfile(path):
				continue
			with open(path) as f:
				domain_data.read_approach_data(f, approach)
		domain_data.total_problems /= len(approaches)
	return all_domain_data


def get_latex_content(file, domains, dt):
	print("Tabulating data for domains %s" % domains)
	observabilities = ['10', '30', '50', '70', '100']
	approaches = ['delta-h-c', 'delta-h-c-uncertainty', 'delta-h-c-f2', 'delta-h-c-cs', 'delta-h-c-cl', 'delta-h-c-cp', 'delta-h-c-cls', 'delta-h-c-clp', 'delta-h-c-cps']
	all_domain_data = collect_data(file, domains, approaches, observabilities, dt)

	content_table = ''
	def print_agreements(obs, domain_data, approaches):
		content_line = ''
		for approach in approaches:
			values = domain_data.obs_data[obs][approach]
			total_time = round(values[10], 3)
			py_time = round(values[10] - values[12], 3)
			fd_time = round(values[12] - values[11], 3)
			lp_time = round(values[11], 3)
			content_line += ' & {0} & {1} & {2}'.format(py_time, lp_time, total_time)
		return content_line
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
		content_table += '\\multirow{%s}{*}{ \\rotatebox[origin=c]{90}{\\textsc{%s}}}' % (len(observabilities), domain_name_4table)
		content_table += '%\n'
		for obs in observabilities:
			content_table += ' & ' + obs
			content_table += print_agreements(obs, all_domain_data[domain_name + dt], approaches)
			content_table += "\\\\"
		if domain_name == domains[-1]:
			content_table += '\\midrule'
		else:
			content_table += '\\hline'

	content_avg = ''
	def print_agreements_avg(domain_data, dt, approaches):
		content_line = ''
		for approach in approaches:
			values = average_values(domain_data, approach, dt)
			total_time = round(values[10], 3)
			py_time = round(values[10] - values[12], 3)
			lp_time = round(values[11], 3)
			fd_time = round(values[12] - values[11], 3)
			content_line += ' & {0} & {1} & {2}'.format(py_time, lp_time, total_time)
		return content_line
	content_avg += print_agreements_avg(all_domain_data, dt, approaches)

	return content_table, content_avg

def main(template, file, domains, dt):
	# Get content.
	content_table, content_avg = get_latex_content(file, domains, '-optimal' + dt)
	content_table2, content_avg2 = get_latex_content(file, domains, '-suboptimal' + dt)
	# Write latex
	latexContent = ''
	with open(template, 'r') as latex:
		latexContent = latex.read()
	if "noisy" in domains[0]:
		latexContent = latexContent.replace("Optimal", "Optimal, Noisy")
		latexContent = latexContent.replace("Basic", "Noisy")
	latexContent = latexContent.replace('CONTENT2', content_table2)
	latexContent = latexContent.replace('AVERAGE2', content_avg2)
	latexContent = latexContent.replace('CONTENT', content_table)
	latexContent = latexContent.replace('AVERAGE', content_avg)
	with open(file, 'w') as latex:
		latex.write(latexContent)
	os.system("pdflatex " + file)

if __name__ == '__main__' :
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
	file = 'times.tex'
	template = 'times-template.tex'
	dt = ""

	parser = argparse.ArgumentParser(description="Generates LaTeX tables for plan recognition experiments")
	parser.add_argument('-d', '--domains', metavar="D", nargs='+', type=str, help="list of domains to tabulate data")
	parser.add_argument('-t', '--template', metavar="T", nargs=1, type=str, help="template file")
	parser.add_argument('-f', '--file', metavar="F", nargs=1, type=str, help="result file")
	args = parser.parse_args()
	if args.file:
		file = args.file[0]
		if 'old-noisy' in file:
			dt = "-old-noisy"
		elif 'noisy' in file:
			dt = "-noisy"

	main(template, file, domains, dt)