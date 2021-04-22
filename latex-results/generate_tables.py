#!/usr/bin/python
import sys, os, math

TIME_TABLE = False

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
		sum_values = [0] * 18
		for obs in self.observabilities:
			line = file.readline()
			if line == '':
				break
			line = line.strip().split('\t')
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
	sum_values = [0] * 18
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
			print(path)
			if not os.path.isfile(path):
				continue
			try:
				with open(path) as f:
					domain_data.read_approach_data(f, basepath + approach)
			except:
				print(path)
				exit()
		domain_data.total_problems /= len(approaches)
	return all_domain_data


def get_latex_content(file, domains, approaches, basepaths):
	observabilities = ['10', '30', '50', '70', '100']
	all_domain_data = collect_data(file, domains, approaches, basepaths, observabilities)

	content_table = ''

	for domain_name in domains:
		domain_name_4table = domain_name
		domain_name_4table = domain_name_4table.replace('-optimal', '')
		domain_name_4table = domain_name_4table.replace('-suboptimal', '')
		domain_name_4table = domain_name_4table.replace('-old-noisy', '')
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
		
		content_table += '\n\\multirow{%s}{*}{\\rotatebox[origin=c]{90}{\\textsc{%s}}} ' \
			% (len(observabilities), domain_name_4table)

		for obs in observabilities:
			len_obs = str(round(domain_data.get_avg_obs(obs), 2))
			len_solutions = str(round(domain_data.get_avg_solutions(obs), 2))
			content_table += '\n\t' + ('\\\\ & ' if (obs != '10') else ' & ') + obs + '\n'
			for basepath, approach in zip(basepaths, approaches):
				content_table += '\n\t\t% ' + approach + ' - ' + obs + '% '
				print(domain_name, basepath, approach)
				if (basepath + approach) not in domain_data.obs_data[obs]:
					if TIME_TABLE:
						content_table += '\n\t\t& - & - & - & -\t \n'
					else:
						content_table += '\n\t\t& - & - & - & - & -\t \n'
					continue
				values = domain_data.obs_data[obs][basepath + approach]
				if 'old' in basepath:
					time = round(values[10], 3)
					timelp = round(values[11], 3)
					timefd = round(values[12], 3)
					const = '-'
					hc = '-'
				else:
					time = round(values[11], 3)
					timelp = round(values[12], 3)
					timefd = round(values[13], 3)
					const = round(values[15], 1)
					hc = round(values[17], 1)
				accuracy = round(values[8] * 100, 1)
				spread = round(values[9], 2)
				per = int(values[10])
				ratio = 0 if (values[9] == 0) else round(100 * values[8] / values[9], 1)
				ar = round(values[5], 2)
				fpr = round(values[6], 2)
				fnr = round(values[7], 2)
				if TIME_TABLE:
					content_table += '\n\t\t& {0} & {1} & {2} & {3}'.format(time, timefd, timelp, timefd-timelp)
				else:
					content_table += '\n\t\t& {0} & {1} & {2} & {3} & {4}'.format(ar, accuracy, spread, const, hc)
				content_table += ' \t \n'
		content_table += ' \\\\ \hline'

	content_avg = ''
	for basepath, approach in zip(basepaths, approaches):
		values = average_values(all_domain_data, basepath + approach)
		if 'old' in basepath:
			time = round(values[10], 3)
			timelp = round(values[11], 3)
			timefd = round(values[12], 3)
			const = '-'
			hc = '-'
		else:
			time = round(values[11], 3)
			timelp = round(values[12], 3)
			timefd = round(values[13], 3)
			const = round(values[15], 1)
			hc = round(values[17], 1)
		accuracy = round(values[8] * 100, 2)
		spread = round(values[9], 2)
		per = round(values[10], 1)
		ratio = 0 if (values[9] == 0) else round(100 * values[8] / values[9], 2)
		ar = round(values[5], 2)
		fpr = round(values[6], 2)
		fnr = round(values[7], 2)
		if TIME_TABLE:
			content_avg += '& {0} & {1} & {2} & {3}'.format(time, timefd, timelp, timefd-timelp)
		else:
			content_avg += '& {0} & {1} & {2} & {3} & {4}'.format(ar, accuracy, spread, const, hc)

	return content_table, content_avg


def create_tex_files(title, file, domains, approaches, basepaths, names=None, caption=''):
	# Get names
	if names is None:
		name = approaches
	
	# Get content
	content_table, content_avg = get_latex_content(file, domains, approaches, basepaths)
	domains = [name.replace("optimal", "suboptimal") for name in domains]
	content_table_2, content_avg_2 = get_latex_content(file, domains, approaches, basepaths)

	# Read template
	latexContent = ''
	with open('template.tex', 'r') as latex:
		latexContent = latex.read()
	# Write header
	latexContent = latexContent.replace("<TITLE>", title)
	latexContent = latexContent.replace("<CAPTION>", caption)
	if "noisy" in domains[0]:
		latexContent = latexContent.replace("Optimal", "Optimal, Noisy")
		latexContent = latexContent.replace("Basic", "Noisy")
	if TIME_TABLE:
		names = ["& \\multicolumn{4}{c|}{%s}" % name for name in names]
		latexContent = latexContent.replace("<ALIGN>", "cccc|" * len(approaches))
		latexContent = latexContent.replace("<METRICS>", '& \\textbf{Total} & \\textbf{FD} & \\textbf{LP} & \\textbf{Prep}\n' * len(approaches))
	else:
		names = ["& \\multicolumn{5}{c|}{%s}" % name for name in names]
		latexContent = latexContent.replace("<ALIGN>", "ccccc|" * len(approaches))
		latexContent = latexContent.replace("<METRICS>", '& \\textbf{Agr} & \\textbf{Acc} & \\textbf{Spr} & \\textbf{Rows} & \\textbf{HC}\n' * len(approaches))
	latexContent = latexContent.replace("<NAMES>", '\n'.join(names))
	# Write content
	latexContent = latexContent.replace('<TABLE_LP_RESULTS>', content_table)
	latexContent = latexContent.replace('<AVG_APPROACH>', content_avg)
	latexContent = latexContent.replace('<TABLE_LP_RESULTS_2>', content_table_2)
	latexContent = latexContent.replace('<AVG_APPROACH_2>', content_avg_2)
	with open(file, 'w') as latex:
		latex.write(latexContent)
	os.system("pdflatex " + file)


if __name__ == '__main__' :
	default_path = '../results-old'
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

	file = 'variations.tex'
	if len(sys.argv) > 1:
		file = sys.argv[1] + ".tex"
	if '-fast' in sys.argv:
		default_path = '../data-latex'
		domains = [
		'blocks-world-optimal',
		'depots-optimal',
		'driverlog-optimal',
		'dwr-optimal',
		'rovers-optimal',
		'sokoban-optimal'
		]
	if '-time' in sys.argv:
		TIME_TABLE = True
		file = file.replace(".tex", "-time.tex")

	# Latex resulting files
	if 'old-noisy' in file:
		domains = [name.replace("optimal", "optimal-old-noisy") for name in domains]
	elif 'noisy' in file:
		domains = [name.replace("optimal", "optimal-noisy") for name in domains]

	if 'previous' in file:
		paths = [default_path] * 6
		title = 'Previous Methods'
		caption = "Results comparing our method with previous methods."
		approaches = ['delta', 'deltau', 'delta-f2', 'rg2009', 'lm_hc0', 'lm_hc30']
		names = ['\\dhc', '\\dhcu', '\\dhcf', '\\rg', '\\pom', '\\pomC']
	elif 'filters' in file:
		paths = [default_path] * 6
		title = 'Filters'
		caption = "Results for filtering \\epsilon = 0, 0.1 and 0.2."
		approaches = [
		'delta', 'deltau',
		'delta-f1', 'deltau-f1',
		'delta-f2', 'deltau-f2'
		]
		names = [
		'\\dhc \\unreliability = 0', '\\dhcu \\unreliability = 0',
		'\\dhc \\unreliability = 0.1', '\\dhcu \\unreliability = 0.1',
		'\\dhc \\unreliability = 0.2', '\\dhcu \\unreliability = 0.2'
		]
	elif 'variations' in file:
		paths = [default_path] * 4
		title = 'Variations'
		caption = 'L for landmarks, P for post-hoc, S for state equation.'
		approaches = ['delta-cl', 'delta-o-cl', 'delta', 'delta-o']
		names = ['L', 'L+', 'L, P, S', 'L+, P, S']
	elif 'constraints' in file:
		if 'single' in file:
			paths = [default_path] * 8
			title = 'Constraints - Single'
			caption = 'L for landmarks, D for delete relaxation, P for post-hoc, S for state equation, $F^i$ for flow(sys(i)).'
			approaches = [
			'delta-cp', 'delta-cs',
			'delta-cl', 'delta-o-cl',
			'delta-cd', 'delta-o-cd',
			'delta-cf1', 'delta-cf2',
			]
			names = [
			'P', 'S',
			'L', 'L+',
			'D', 'D+',
			'$F^1$', '$F^2$'
			]
		elif 'pairs' in file:
			paths = [default_path] * 6
			title = 'Constraints - Pairs'
			caption = 'L for landmarks, P for post-hoc, S for state equation, D for delete relaxation.'
			approaches = [
			'delta-clp', 'delta-cls', 'delta-cld',
			'delta-cps', 'delta-cpd', 'delta-csd'
			]
			names = [
			'L, P', 'L, S', 'L, D'
			'P, S', 'P, D', 'S, D'
			]
		elif 'mip' in file:
			paths = [default_path] * 8
			title = 'Constraints - MIP'
			caption = 'L for landmarks, P for post-hoc, S for state equation. (i) marks when MIP was used.'
			approaches = [
			'delta-cl', 'delta-cp', 'delta-cs', 'delta-cd',
			'delta-i-cl', 'delta-i-cp', 'delta-i-cs', 'delta-i-cd'
			]
			names = [
			'L', 'P', 'S', 'D',
			'L(i)', 'P(i)', 'S(i)', 'D(i)'
			]
		elif 'lm' in file:
			if 'lmf2' in file:
				paths = [default_path] * 7
				title = 'Constraints - Landmarks with noise filter ($\\epsilon = 0.2$)'
				caption = "Results for landmark variations using noise filter with $\\epsilon = 0.2$. 'I' marks when variables $Y_o$ and $Y_{\\vec{o}}$ are integer. The soft version uses $Y_{\\vec{o}}/occur(\\vec{o})$ instead of 1 for minimum landmark sum. Variables $B_{\\vec{o}}$ are always integer."
				approaches = [
				'delta-cl-f2', 'delta-i-cl-f2', 'delta-o-cl-f2', 'delta-i-o-cl-f2', 'delta-o-cl1-f2', 'delta-i-o-cl1-f2', 'delta-o-cl2-f2'
				]
				names = [
				'$L$', '$L_I$', '$L^+$', '$L_I^+$', '$L^+$ (soft)', '$L_I^+$ (soft)', '$L^+$ (B-var)'
				]
			else:
				paths = [default_path] * 7
				title = 'Constraints - Landmarks'
				caption = "Results for landmark variations. 'I' marks when variables $Y_o$ and $Y_{\\vec{o}}$ are integer. The soft version uses $Y_{\\vec{o}}/occur(\\vec{o})$ instead of 1 for minimum landmark sum. Variables $B_{\\vec{o}}$ are always integer."
				approaches = [
				'delta-cl', 'delta-i-cl', 'delta-o-cl', 'delta-i-o-cl', 'delta-o-cl1', 'delta-i-o-cl1', 'delta-o-cl2'
				]
				names = [
				'$L$', '$L_I$', '$L^+$', '$L_I^+$', '$L^+$ (soft)', '$L_I^+$ (soft)', '$L^+$ (B-var)'
				]
		elif 'del' in file:
			if 'delo' in file:
				paths = [default_path] * 8
				title = 'Constraints - Delete Relaxation with Observations'
				caption = 'Different versions of Delete Relaxation. (i) marks when MIP was used.'
				approaches = [
				'delta-o-csdt', 'delta-o-cdt', 'delta-i-o-cdt', 'delta-i-o-cdt1', 'delta-i-o-cdt5', 'delta-o1-cdu', 'delta-i-o1-cdt', 'delta-i-o1-cdt1'
				]
				names = [
				'D+, S', 'D+', 'D+(i)', 'D+(i ops)', 'D+(i obs)', 'D+ Order hard', 'D+ Order(i) soft', 'D+ Order(i ops) soft'
				]
			elif 'deln' in file:
				paths = [default_path] * 5
				title = 'Constraints - Delete Relaxation with Observations'
				caption = 'Different versions of Delete Relaxation. (i) marks when MIP was used.'
				approaches = [
				'delta-o-cdt', 'delta-i-o-cdt1', 'delta-o-cdto', 'delta-o-i-cdto1', 'delta-i-o-cdts1'
				]
				names = [
				'$D+$', '$D+$(i ops)', '$D^2+$', '$D^2+$(i ops)', '$D^3+$(i ops)'
				]
			else:
				paths = [default_path] * 7
				title = 'Constraints - Delete Relaxation'
				caption = 'Different versions of Delete Relaxation. (i) marks when MIP was used.'
				approaches = [
				'delta-cdt', 'delta-i-cdt', 'delta-i-cdt1', 'delta-i-cdt2', 'delta-i-cdt3', 'delta-i-cdt4', 'delta-csdt'
				]
				names = [
				'D', 'D(i)', 'D(i ops)', 'D(i facts)', 'D(i achiever)', 'D (i time)', 'D, S'
				]
		elif 'flow' in file:
			if 'flowo2' in file:
				paths = [default_path] * 4
				title = 'Constraints - Flow with Observations 2'
				caption = ''
				approaches = [
				'delta-o-cf1ab', 'delta-o-cf1db', 'delta-o-cf13a', 'delta-o-cf10a'
				]
				names = [
				'$F^1O$ (size 2)', '$F^1O$ (size 16)', '$F^1O$ (pre+eff)3 (intra)', '$F^1O$ (pre+eff)3'
				]
			elif 'flowo' in file:
				paths = [default_path] * 8
				title = 'Constraints - Flow with Observations'
				caption = ''
				approaches = [
				'delta-o-cf14', 'delta-o-cf15', 'delta-o-cf13', 'delta-o-cf17', 
				'delta-o-cf11', 'delta-o-cf12', 'delta-o-cf10', 'delta-o-cf16'
				]
				names = [
				'$F^1O$ (pre) (intra)', '$F^1O$ (eff) (intra)', '$F^1O$ (pre+eff) (intra)', '$F^1O$ (preXeff) (intra)',
				'$F^1O$ (pre)', '$F^1O$ (eff)', '$F^1O$ (pre+eff)', '$F^1O$ (preXeff)'
				]
			else:
				paths = [default_path] * 7
				title = 'Constraints - Flow'
				caption = ''
				approaches = [
				'delta-cf1', 'delta-cf1ab', 'delta-cf1db', 'delta-cf1f3', 'delta-cf2', 'delta-cf2n'
				]
				names = [
				'$F^1$', '$F^1$ (size 2)', '$F^1$ (size 16)', '$F^1$ (pre+eff, intra)', '$F^2$', '$F^2$ (full)'
				]
			
	create_tex_files(title, file, domains, approaches, paths, names, caption)