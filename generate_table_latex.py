#!/usr/bin/python
import sys
import os
import math
import argparse

def main(template, file, domains, approaches, basepaths, names):
	print("Tabulating data from %s for domains %s"%(basepaths,domains))

	content_table = ''
	
	approaches_metrics = dict()
	for basepath, approach in zip(basepaths, approaches):
		approaches_metrics[basepath + approach] = [0, 0, 0]

	totalInstances = 0
	for domain_name in domains:
		multirow = 0
		observabilities = []
		if 'noisy' in domain_name:
			multirow = 4
			observabilities = ['25', '50', '75', '100']
		else: 
			multirow = 5
			observabilities = ['10', '30', '50', '70', '100']

		totalProblems = 0
		avgGoals = 0
		totalInstances += multirow

		path = basepaths[0] + "/" + domain_name + '-' + str(approaches[0]) + '.txt'
		with open(path) as f:
			printed = False
			for l in f:
				line = l.strip().split('\t')
				if(line[0] == '10' and printed == False):
					avgGoals = float(0)
					printed = True
		
		domain_name_4table = domain_name.replace('-noisy', '')
		if 'intrusion-detection' in domain_name:
			domain_name_4table = 'instrusion'

		if 'blocks-world' in domain_name:
			domain_name_4table = 'blocks'

		if 'zeno-travel' in domain_name:
			domain_name_4table = 'zeno'

		if 'easy-ipc-grid' in domain_name:
			domain_name_4table = 'ipc-grid'			
		
		content_table += '\n\\multirow{' + str(multirow) +'}{*}{\\rotatebox[origin=c]{90}{\\textsc{' + domain_name_4table + '}} \\rotatebox[origin=c]{90}{(' + str((totalProblems * 4)) + ')}} & \\multirow{' + str(multirow) + '}{*}{' + str(round(avgGoals, 1)) + '} '	

		print_metrics = ''
		for obs in observabilities:
			printedObs = False
			for basepath, approach in zip(basepaths, approaches):
				path = basepath + "/" + domain_name + '-' + approach + '.txt'
				with open(path) as f:
					for l in f:
						line = l.strip().replace(' ', '\t').split('\t')
						if not (line[0] == obs):
							continue

						if not printedObs:
							avgObs = float(0)
							print_metrics += '\n\t' + ('\\\\ & & ' if (obs != '25' and obs != '10') else ' & ') + obs + '\t & ' + str(avgObs) + '\n'
							printedObs = True

						if len(line) < 9:
							continue

						time = float(line[8])
						accuracy = (float(line[1]) * 100)
						spreadG = float(line[7])
						if 'uniqueness' in approach and 'noisy' in domain_name:
							time = float(line[10])
							accuracy = (float(line[1]) * 100)
							spreadG = float(line[9])

						if 'completion' in approach and 'noisy' in domain_name:
							time = float(line[10])
							accuracy = (float(line[1]) * 100)
							spreadG = float(line[9])

						if 'mirroring' in approach and 'noisy' in domain_name:
							time = float(line[10])
							accuracy = (float(line[1]) * 100)
							spreadG = float(line[9])

						if 'mirroring' in approach:
							time = float(line[10])
							accuracy = (float(line[1]) * 100)
							spreadG = float(line[9])


						list_metrics = approaches_metrics[basepath + approach]
						list_metrics[0] += time
						list_metrics[1] += accuracy
						list_metrics[2] += spreadG

						print_metrics += '\n\t\t% ' + approach + ' - ' + obs + '% '
						print_metrics += '\n\t\t& ' + str(round(time, 3)) + ' & ' + str(round(accuracy, 1)) + '\% & ' + str(round(spreadG, 2))
						print_metrics += ' \t \n'

		print_metrics += ' \\\\ \hline'
		content_table += print_metrics

	avg_approaches = dict()
	for approach in approaches_metrics.keys():
		time = approaches_metrics[approach][0] / totalInstances
		accuracy = approaches_metrics[approach][1] / totalInstances
		spread = approaches_metrics[approach][2] / totalInstances
		avg_approaches[approach] = [time, accuracy, spread]

	latexContent = ''
	with open(template, 'r') as latex:
		latexContent = latex.read()

	latexContent = latexContent.replace('<TABLE_LP_RESULTS>', content_table)

	index = 0
	for basepath, approach, name in zip(basepaths, approaches, names):
		metrics = avg_approaches[basepath + approach]
		latexContent = latexContent.replace('<APPROACH_' + str(index) + '>', "$"+name+"$")
		latexContent = latexContent.replace('<AVG_APPROACH_' + str(index) + '>', '%.3f'%(metrics[0]) + ' & ' + '%.2f'%(metrics[1]) + '\% & ' + '%.2f'%(metrics[2]))
		index += 1

	with open(file, 'w') as latex:
		latex.write(latexContent)

if __name__ == '__main__' :
	# Domains with noisy observations.
	# domains = ['blocks-world-noisy', 'campus-noisy', 'depots-noisy', 'driverlog-noisy', 'dwr-noisy',\
	#  			'easy-ipc-grid-noisy', 'ferry-noisy', 'intrusion-detection-noisy', 'kitchen-noisy', 'logistics-noisy',\
	#  			 'miconic-noisy', 'rovers-noisy', 'satellite-noisy', 'sokoban-noisy', 'zeno-travel-noisy']
	domains = ['blocks-world', 'depots', 'driverlog', 'dwr',\
	 			'easy-ipc-grid', 'ferry', 'logistics',\
	 			 'miconic', 'rovers', 'satellite', 'sokoban', 'zeno-travel']

	# Domains with missing observations.
	# domains = ['blocks-world', 'campus', 'depots', 'driverlog', 'dwr',\
	#  			'easy-ipc-grid', 'ferry', 'intrusion-detection', 'kitchen', 'logistics' ,\
	#  			 'miconic', 'rovers', 'satellite', 'sokoban', 'zeno-travel']
	# domains = ['blocks-world', 'depots', 'driverlog', 'dwr',\
	#  			'easy-ipc-grid', 'ferry', 'logistics' ,\
	#  			 'miconic', 'rovers', 'satellite', 'sokoban', 'zeno-travel']

	# List of evaluated approaches.
	
	file = 'latex-results/corrections.tex'
	template = 'latex-results/corrections-template.tex'
	approaches = ['delta-h-c', 'delta-h-c-uncertainty'] * 3
	paths = ['results/v1'] * 2 + ['results/v2'] * 2 + ['results/v3'] * 2

	parser = argparse.ArgumentParser(description="Generates LaTeX tables for plan recognition experiments")
	parser.add_argument('-d', '--domains', metavar="D", nargs='+', type=str, help="list of domains to tabulate data")
	parser.add_argument('-a', '--approaches', metavar="A", nargs='+', type=str, help="approaches to tabulate")
	parser.add_argument('-p', '--paths', metavar="P", nargs='+', type=str, help="base path of data result files for each approach")
	parser.add_argument('-n', '--names', metavar="N", nargs='+', type=str, help="approach names to put in table")
	parser.add_argument('-t', '--template', metavar="T", nargs=1, type=str, help="template file")
	parser.add_argument('-f', '--file', metavar="F", nargs=1, type=str, help="result file")
	args = parser.parse_args()

	default_path = 'results'

	# Latex resulting files
	if args.file:
		file = args.file[0]
		if 'noisy' in file:
			domains = ['blocks-world-noisy', 'depots-noisy', 'driverlog-noisy', 'dwr-noisy',\
			 			'easy-ipc-grid-noisy', 'ferry-noisy', 'logistics-noisy',\
			 			 'miconic-noisy', 'rovers-noisy', 'satellite-noisy', 'sokoban-noisy', 'zeno-travel-noisy']
	if args.domains:
		domains = args.domains # Domains used

	# Latex template file
	if args.template:
		template = args.template[0]
		if 'previous' in template:
			paths = [default_path] * 7
			approaches = ['delta-h-c', 'delta-h-c-uncertainty', 'planrecognition-ramirezgeffner', 'goal_recognition-yolanda', 'planrecognition-heuristic_completion-0', 'planrecognition-heuristic_uniqueness-0', 'mirroring_landmarks']
		elif 'constraints' in template:
			if 'single' in template:
				paths = ['result/v3_c1'] * 2 + ['result/v3_c2'] * 2 + ['result/v3_c3'] * 2
			else:
				paths = ['result/v3_c4'] * 2 + ['result/v3_c5'] * 2 + ['result/v3_c6'] * 2
		elif 'filters' in template:
			paths = ['result/v4_f0'] * 2 + ['result/v4_f1'] * 2 + ['result/v4_f2'] * 2
	if args.approaches:
		approaches = args.approaches # Approaches in template

	if args.names:
		if len(args.names) == len(approaches):
			names = args.names
		else:
			print("--names parameter requires the same number of names as --approaches")
			names = approaches
	else:
		names = approaches
	if args.paths:
		paths=args.paths
	
	if len(paths) < len(approaches):
		paths += [default_path] * (len(approaches) - len(paths))

	main(template, file, domains, approaches, paths, names)