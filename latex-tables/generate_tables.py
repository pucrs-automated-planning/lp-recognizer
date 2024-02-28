#!python

##
## Generate .pdf tables for given methods.
##

## Uses:
# Generate individual table:
# ./generate_tables.py lmc -rows -comp [-fast]
# Generate summarized table by observability level:
# ./generate_tables.py flowf2-sub-old-noisy -obs [-fast]
# Generate summarized table by domain:
# ./generate_tables.py flowf2-sub-old-noisy -dom [-fast]
##

import sys, os

COLS_TYPE = 0
BOLD = True
COMP = None
AVG = 0
NUM_VALUES = 18
VER = 1

class DomainData:

	def __init__(self, name, observabilities):
		self.name = name
		self.observabilities = observabilities
		self.total_problems = 0
		self.obs_data = dict()
		for obs in observabilities:
			self.obs_data[obs] = dict()
		self.num_lines = 0
		self.sum_data = dict()

	def read_approach_data(self, file, approach):
		file.readline() # Header
		sum_values = [0] * NUM_VALUES
		for obs in self.observabilities:
			line = file.readline()
			if line == '':
				break
			line = line.strip().split('\t')
			self.total_problems += int(line[0])
			values = [float(x) for x in line]
			self.obs_data[obs][approach] = values[0:NUM_VALUES]
			sum_values = [x + y for x, y in zip(sum_values, values)]
		self.sum_data[approach] = sum_values

	def add_comp_data(self, file):
		methods = file.readline().split()
		for approach in methods:
			self.sum_data[approach].append(0)
		for obs in self.observabilities:
			values = file.readline().split()
			for i in range(0, len(methods)):
				approach = methods[i]
				self.obs_data[obs][approach].append(int(values[i]))	
				self.sum_data[approach][-1] += int(values[i])

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

def average_values(all_domain_data, approach, obs = None):
	sum_values = [0] * (NUM_VALUES + 1)
	for domain_data in all_domain_data.values():
		if approach in domain_data.sum_data:
			values = domain_data.obs_data[obs][approach] if obs else domain_data.sum_data[approach]
			sum_values = [x + y for x, y in zip(sum_values, values)]
	return sum_values

def collect_data(file, domains, observabilities, approaches):
	if COMP:
		path = "../data-comparison/"
		comp_files = [path + f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and COMP in f]
	all_domain_data = dict()
	for domain_name in domains:
		domain_data = DomainData(domain_name, observabilities)
		all_domain_data[domain_name] = domain_data
		for approach in approaches:
			path = "../data-tables/" + domain_name + '-' + approach + '.txt'
			if not os.path.isfile(path):
				print("File " + path + " not found")
				continue
			try:
				with open(path) as f:
					print("Processing " + approach)
					domain_data.read_approach_data(f, approach)
			except:
				print("Error with file " + path)
				exit()
		domain_data.total_problems /= len(approaches)
		if COMP:
			path = [f for f in comp_files if domain_name + ".txt" in f][0]
			print("Comp file: " + path)
			with open(path) as f:
				domain_data.add_comp_data(f)
	return all_domain_data


def convert_domain_name(domain_name):
	domain_name_4table = domain_name
	domain_name_4table = domain_name_4table.replace('-optimal', '')
	domain_name_4table = domain_name_4table.replace('-suboptimal', '')
	domain_name_4table = domain_name_4table.replace('-old-noisy', '')
	domain_name_4table = domain_name_4table.replace('-noisy', '')
	if 'blocks-world' in domain_name:
		domain_name_4table = domain_name_4table.replace("-world", "")
	if 'zeno-travel' in domain_name:
		domain_name_4table = domain_name_4table.replace("-travel", "")
	if 'easy-ipc-grid' in domain_name:
		domain_name_4table = domain_name_4table.replace("easy-", "")
	return domain_name_4table


def get_line_content(values, best_ar, best_win, num_problems = 1):
	time = round(values[11] / num_problems, 2)
	timelp = round(values[12] / num_problems, 2)
	timefd = round(values[13] / num_problems, 2)
	const = round(values[15] / num_problems, 1)
	hc = round(values[17] / num_problems, 1)
	accuracy = round(values[8] * 100 / num_problems, min(num_problems, 2))
	spread = round(values[9] / num_problems, 2)
	#per = round(values[10], 1) #int(values[10])
	ratio = 0 if (values[9] == 0) else round(100 * values[8] / values[9], min(num_problems, 2))
	ar = round(values[5] / num_problems, 2)
	fpr = round(values[6] / num_problems, 2)
	fnr = round(values[7] / num_problems, 2)
	if BOLD:
		if ar == best_ar:
			ar = "\\textbf{%s}" % ar
	content = ""
	if COLS_TYPE == 0:
		content += '& {0} & {1} & {2} & {3}'.format(ar, hc, time, timelp)
	elif COLS_TYPE == 1:
		win = int(values[18])
		if win == best_win:
			win = "\\textbf{%s}" % win
		content += '& {0} & {1} & {2} & {3} & {4}'.format(ar, hc, win, time, timelp)
	elif COLS_TYPE == 2:
		content += '& {0} & {1} & {2} & {3} & {4}'.format(ar, hc, const, time, timelp)
	elif COLS_TYPE == 3:
		content += '& {0} & {1}'.format(ar, time)
	return content

# Average per domain, per observability
def get_avg_content(domains, observabilities, approaches, all_domain_data):
	content_table = ''
	for domain_name in domains:
		domain_name_4table = convert_domain_name(domain_name)
		domain_data = all_domain_data[domain_name]
		content_table += '\n\\multirow{%s}{*}{\\rotatebox[origin=c]{90}{\\textsc{%s}}} ' % (len(observabilities), domain_name_4table)
		for obs in observabilities:
			#len_obs = str(round(domain_data.get_avg_obs(obs), 2))
			#len_solutions = str(round(domain_data.get_avg_solutions(obs), 2))
			content_table += '\n\t' + ('\\\\ & ' if (obs != '10') else ' & ') + obs + '\n'
			best_ar = max([round(domain_data.obs_data[obs][i][5], 2) for i in approaches])
			best_win = max([int(domain_data.obs_data[obs][i][18]) for i in approaches]) if COMP else -1
			for approach in approaches:
				content_table += '\n\t\t% ' + approach + ' - ' + obs + '% \n'
				print(domain_name, obs, approach)
				if approach not in domain_data.obs_data[obs]:
					if COLS_TYPE == 0:
						content_table += '\n\t\t' + ('& - ' * 4) + '\t \n'
					elif COLS_TYPE == 1 or COLS_TYPE == 2:
						content_table += '\n\t\t' + ('& - ' * 5) + '\t \n'
					elif COLS_TYPE == 3:
						content_table += '\n\t\t' + ('& - ' * 2) + '\t \n'
					continue
				content_table += get_line_content(domain_data.obs_data[obs][approach], best_ar, best_win)
				content_table += ' \t \n'
		content_table += ' \\\\ \\hline'
	return content_table

# Average per domain
def get_dom_avg_content(domains, approaches, all_domain_data):
	content_table = ''
	for domain_name in domains:
		domain_name_4table = convert_domain_name(domain_name)[0]
		domain_data = all_domain_data[domain_name]
		content_table += '\n\\multicolumn{2}{c|}{\\textsc{%s}} ' % domain_name_4table
		#len_obs = str(round(domain_data.get_avg_obs(obs), 2))
		#len_solutions = str(round(domain_data.get_avg_solutions(obs), 2))
		best_ar = max([round(domain_data.sum_data[i][5], 2) for i in approaches])
		best_win = max([int(domain_data.sum_data[i][18]) for i in approaches]) if COMP else -1
		for approach in approaches:
			content_table += '\n\t\t% ' + approach + ' - ' + domain_name + '% \n'
			print(domain_name, approach)
			if approach not in domain_data.sum_data:
				if COLS_TYPE == 0:
					content_table += '\n\t\t' + ('& - ' * 4) + '\t \n'
				elif COLS_TYPE == 1 or COLS_TYPE == 2:
					content_table += '\n\t\t' + ('& - ' * 5) + '\t \n'
				elif COLS_TYPE == 3:
					content_table += '\n\t\t' + ('& - ' * 2) + '\t \n'
				continue
			content_table += get_line_content(domain_data.sum_data[approach], best_ar, best_win, 5)
			content_table += ' \t \n'
		content_table += ' \\\\'
	content_table += '\\hline'
	return content_table

# Average per observability
def get_obs_avg_content(observabilities, approaches, all_domain_data):
	content_table = ''
	for obs in observabilities:
		content_table += '\n\\multicolumn{2}{c|}{%s} ' % (obs + "\\%")
		num_problems = len(all_domain_data.keys())
		best_ar = max([round(average_values(all_domain_data, i, obs)[5] / num_problems, 2) for i in approaches])
		best_win = max([int(average_values(all_domain_data, i, obs)[18]) for i in approaches]) if COMP else -1
		for approach in approaches:
			content_table += '\n\t\t% ' + approach + ' - ' + obs + '% \n'
			content_table += get_line_content(average_values(all_domain_data, approach, obs), best_ar, best_win, num_problems)
			content_table += ' \t \n'
		content_table += ' \\\\'
	content_table += '\\hline'
	return content_table


def get_latex_content(file, domains, observabilities, approaches):
	all_domain_data = collect_data(file, domains, observabilities, approaches)
	if AVG == 0:
		content_table = get_avg_content(domains, observabilities, approaches, all_domain_data)
	elif AVG == 1:
		content_table = get_dom_avg_content(domains, approaches, all_domain_data)
	elif AVG == 2:
		content_table = get_obs_avg_content(observabilities, approaches, all_domain_data)
	# Average all
	content_avg = '\\multicolumn{2}{c|}{AVG} '
	num_problems = len(all_domain_data.keys()) * len(observabilities)
	best_ar = max([round(average_values(all_domain_data, i)[5] / num_problems, 2) for i in approaches])
	best_win = max([int(average_values(all_domain_data, i)[18]) for i in approaches]) if COMP else -1
	for approach in approaches:
		values = average_values(all_domain_data, approach)
		content_avg += get_line_content(values, best_ar, best_win, num_problems)
	if not COMP or COLS_TYPE == 1:
		return content_table, content_avg
	# Number of wins
	content_avg += "\\\\\n\\midrule\n\\multicolumn{2}{c|}{WIN}"
	for approach in approaches:
		values = average_values(all_domain_data, approach)
		win = int(values[18])
		if win == best_win:
			win = "\\textbf{%s}" % win
		if COLS_TYPE == 0:
			content_avg += '& %s & & &' % win
		elif COLS_TYPE == 1 or COLS_TYPE == 2:
			content_avg += '& %s & & & &' % win
		elif COLS_TYPE == 3:
			content_avg += '& %s &' % win
	return content_table, content_avg


def create_tex_files(file, domains, observabilities, approaches, names=None):
	# Get names
	if names is None:
		name = approaches
	# Get content
	content_table, content_avg = get_latex_content(file, domains, observabilities, approaches)
	# Read template
	latexContent = ''
	with open('template.tex', 'r') as latex:
		latexContent = latex.read()
	# Write header
	if COLS_TYPE == 0:
		cols = ['Agr', '$h^\\Omega$', 'Time', 'LP']
	elif COLS_TYPE == 1:
		cols = ['Agr', '$h^\\Omega$', 'Win', 'Total', 'LP']
	elif COLS_TYPE == 2:
		cols = ['Agr', '$h^\\Omega$', 'Rows', 'Total', 'LP']
	elif COLS_TYPE == 3:
		cols = ['Agr', 'Time']
	names = ["& \\multicolumn{%s}{c|}{%s}" % (len(cols), name) for name in names]
	names[-1] = names[-1].replace('c|', 'c')
	midrule = ["\\cmidrule(lr){%s-%s}" % (3 + i * len(cols), 2 + len(cols) * (i + 1)) for i in range(len(approaches))]
	latexContent = latexContent.replace("<ALIGN>", ('|' + 'c' * len(cols)) * len(approaches))
	latexContent = latexContent.replace("<METRICS>", (' '.join(['& \\textbf{%s} ' % col for col in cols]) + '\n') * len(approaches))
	latexContent = latexContent.replace("<NAMES>", '\n'.join(names) + '\\\\\n' + ' '.join(midrule))
	if COLS_TYPE == 0:
		midrule = ["\\cmidrule(lr){%s-%s}" % (5 + i * len(cols), 6 + i * len(cols)) for i in range(len(approaches))]
		names = "& & & \\multicolumn{2}{c}{Time}" * len(approaches)
		latexContent = latexContent.replace("<NAMES2>", "\\multicolumn{2}{c}{}" + names + '\\\\\n' + ' '.join(midrule))
	elif COLS_TYPE == 1 or COLS_TYPE == 2:
		midrule = ["\\cmidrule(lr){%s-%s}" % (6 + i * len(cols), 7 + i * len(cols)) for i in range(len(approaches))]
		names = "& & & & \\multicolumn{2}{c}{Time}" * len(approaches)
		latexContent = latexContent.replace("<NAMES2>", "\\multicolumn{2}{c}{}" + names + '\\\\\n' + ' '.join(midrule))
	else:
		latexContent = latexContent.replace("<NAMES2>", "")
	# Write content
	latexContent = latexContent.replace('<TABLE_LP_RESULTS>', content_table)
	latexContent = latexContent.replace('<AVG_APPROACH>', content_avg)
	with open(file, 'w') as latex:
		latex.write(latexContent)
	os.system("pdflatex " + file)


def v1_methods(file):
	global COMP
	if 'basic' in file:
		approaches = ['delta-cl', 'delta-cp', 'delta-cs']
		names = ['L', 'P', 'S']
	elif 'lmc' in file:
		COMP = 'lmc'
		if 'lmcd' in file:
			approaches = ['div-cl', 'div-o-cl', 'div-o-cl1']
			names = ['\\lmc (div)', '\\lmcu (div)', '\\lmcs (div)']
			COMP += 'd'
		elif 'f2' in file:
			approaches = ['delta-cl', 'delta-o-cl', 'delta-o-cl3', 'delta-o-cl1']
			names = ['\\lmc', '\\lmcu', '\\lmco', '\\lmcs']
		else:
			approaches = ['delta-cl', 'delta-o-cl', 'delta-o-cl1']
			names = ['\\lmc', '\\lmcu', '\\lmcs']
	elif 'delr' in file:
		COMP = 'delr'
		approaches = ['delta-o-cdt', 'delta-o-cdto', 'delta-o-cdtb5']
		names = ['\\drone', '\\drtwo', '\\drthree']
	elif 'flow' in file:
		COMP = 'flow'
		approaches = ['delta-cf1', 'delta-cf1ab', 'delta-o-cf17', 'delta-o-cf16', 'delta-cf2']
		names = ["\\sysone", "\\mtwo", "\\intratwo", "\\intertwo", "\\systwo"]
	elif 'general' in file:
		#COMP = 'gen'
		#approaches = ["delta-o-cl1dto", "delta-o-csl1", "delta-o-csdto", "rg2009", "lm_hc0"]
		#names = ["$L^+$, $D_2^+$", "$S$, $L^+$", "$S$, $D_2^+$", "RG", "POM"]
		approaches = ["rg2009", "lm_hc0"]
		names = ["\\rg", "\\pom"]
	return approaches, names

def v2_methods(file):
	global COMP
	if 'basic' in file:
		approaches = ['delta-cl', 'delta-cp', 'delta-cs']
		names = ['L', 'P', 'S']
	elif 'lmc' in file:
		COMP = 'lmc'
		if 'lmcd' in file:
			approaches = ['div-cl', 'div-o-cl1']
			names = ['\\lmc (div)', '\\lmcs (div)']
			COMP += 'd'
		else:
			approaches = ['delta-cl','delta-o-cl1']
			names = ['\\lmc', '\\lmcs']
	elif 'delr' in file:
		COMP = 'delr'
		approaches = ['delta-cdt', 'delta-o-cdto', 'delta-o-cdtb5', 'delta-o1-cdtb5']
		names = ['\\dr', '\\drtwo', '\\drthree', '\\drtime']
	elif 'flow' in file:
		COMP = 'flow'
		approaches = ['delta-cf1', 'delta-cf1ab', 'delta-o-cf17', 'delta-o-cf16', 'delta-cf2']
		names = ["\\sysone", "\\mtwo", "\\intratwo", "\\intertwo", "\\systwo"]
	elif 'general' in file:
		approaches = ["rg2009", "lm_hc0"]
		names = ["\\rg", "\\pom"]
	return approaches, names


if __name__ == '__main__' :
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
	observabilities = ['10', '30', '50', '70', '100']

	# Flags.
	if '-win' in sys.argv:
		# Include "win" column.
		COLS_TYPE = 1
	if '-rows' in sys.argv:
		# Include "row" column.
		COLS_TYPE = 2
	if '-time' in sys.argv:
		# Include only agr and total time.
		COLS_TYPE = 3
	if '-dom' in sys.argv:
		# Average by domain.
		AVG = 1
	if '-obs' in sys.argv:
		# Average by observability.
		AVG = 2
	if '-v2' in sys.argv:
		# Table version
		VER = 2

	# Data set type.
	file = sys.argv[1] + ".tex"
	if 'noisy' in file:
		domains = [name.replace("optimal", "optimal-old-noisy") for name in domains]
	if 'sub' in file:
		domains = [name.replace("optimal", "suboptimal") for name in domains]

	# Methods.
	if VER == 1:
		approaches, names = v1_methods(file)
	else:
		approaches, names = v2_methods(file)
	if not '-comp' in sys.argv:
		COMP = None
	if 'f2' in file:
		approaches = [approach + "-f2" if 'delta' in approach or 'div' in approach else approach for approach in approaches]
		if COMP:
			COMP += "f2"
			
	print(approaches)
	print(domains)
	create_tex_files(file, domains, observabilities, approaches, names)