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

def collect_data(file, domains, observabilities):
	all_domain_data = dict()
	for domain in domains:
		for dt in ['-optimal', '-suboptimal']:
			# No noise
			domain_name = domain+dt
			domain_data = DomainData(observabilities)
			all_domain_data[domain_name] = domain_data
			path = '../results-new/' + domain_name + '-delta-h-c.txt'
			with open(path) as f:
				domain_data.read_approach_data(f, 'delta-h-c')
	return all_domain_data

def get_latex_content(file, domains):
	print("Tabulating data for domains %s" % domains)
	observabilities = ['10', '30', '50', '70', '100']

	all_domain_data = collect_data(file, domains, observabilities)
	
	content_table = '\\multicolumn{3}{c|}{}'
	header = 'c|c|c|'
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
		content_table += ' & \\rotatebox[origin=c]{90}{ \\textsc{%s} }' % domain_name_4table
		header += 'c'
	content_table += '\\\\\\midrule\n'

	domain_types = ['Optimal', 'Sub-optimal']

	# |Gamma|
	content_table += '\\multicolumn{3}{c|}{$|\\goalconditions|$}'
	for domain_name in domains:
		content_table += ' & %s' % round(all_domain_data[domain_name+'-optimal'].get_avg_goals(), 2)
	content_table += '\\\\\\midrule\n'

	for dt_name in domain_types:
		dt = '-' + dt_name.replace('-', '').lower()
		content_table += '\\multirow{%s}{*}{ \\rotatebox[origin=c]{90}{\\textsc{%s}} }' % (len(observabilities) * 2, dt_name)
		# |Omega|
		for obs in observabilities:
			content_table += '& '
			if obs == '10':
				content_table += '\\multicolumn{1}{c}{ \\multirow{%s}{*}{$|\\observations|$} }' % len(observabilities)
			else:
				content_table += '\\multicolumn{1}{c}{}'
			content_table += '& \\multicolumn{1}{|c|}{' + str(obs) + '\\%}'
			for domain_name in domains:
				content_table += '& %s' % str(round(all_domain_data[domain_name+dt].get_avg_obs(obs), 2))
			content_table += '\\\\\n'
		content_table += '\\cline{2-%s}\n' % (len(domains) + 3)

		# |Gamma*|
		for obs in observabilities:
			content_table += '& '
			if obs == '10':
				content_table += '\\multicolumn{1}{c}{ \\multirow{%s}{*}{$|\\grsolution|$} }' % len(observabilities)
			else:
				content_table += '\\multicolumn{1}{c}{}'
			content_table += '& \\multicolumn{1}{|c|}{' + str(obs) + '\\%}'
			for domain_name in domains:
				content_table += ' & %s' % str(round(all_domain_data[domain_name+dt].get_avg_solutions(obs), 2))
			content_table += '\\\\\n'

		if dt_name != domain_types[-1]:
			content_table += '\\midrule\n'

	return header, content_table

def main(template, file, domains):
	# Get content.
	header, content = get_latex_content(file, domains)
	# Write latex
	latexContent = ''
	with open(template, 'r') as latex:
		latexContent = latex.read()
	latexContent = latexContent.replace('HEADER', header)
	latexContent = latexContent.replace('CONTENT', content)
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
	file = 'domains.tex'
	template = 'domains-template.tex'

	parser = argparse.ArgumentParser(description="Generates LaTeX tables for plan recognition experiments")
	parser.add_argument('-d', '--domains', metavar="D", nargs='+', type=str, help="list of domains to tabulate data")
	parser.add_argument('-t', '--template', metavar="T", nargs=1, type=str, help="template file")
	parser.add_argument('-f', '--file', metavar="F", nargs=1, type=str, help="result file")
	args = parser.parse_args()

	main(template, file, domains)