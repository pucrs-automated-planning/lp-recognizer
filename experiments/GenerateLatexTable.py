#!/usr/bin/python
import sys
import os
import math
import argparse

def main(domains, approaches, basepath, names):
	print("Tabulating data from %s for domains %s"%(basepath,domains))

	content_table = ''
	
	approaches_metrics = dict()
	for approach in approaches:
		approaches_metrics[approach] = [0, 0, 0]

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

		path = basepath + "/" + domain_name + '-' + str(approaches[0]) + '.txt'
		with open(path) as f:
			printed = False
			for l in f:
				line = l.strip().split('\t')
				if(line[0] == '10' and printed == False):
					avgGoals = float(0)
					printed = True
		
		content_table += '\n\\multirow{' + str(multirow) +'}{*}{\\rotatebox[origin=c]{90}{\\textsc{' + domain_name + '}} \\rotatebox[origin=c]{90}{(' + str((totalProblems * 4)) + ')}} & \\multirow{' + str(multirow) + '}{*}{' + str(round(avgGoals, 1)) + '} '	

		print_metrics = ''
		for obs in observabilities:
			printedObs = False
			for approach in approaches:
				path = basepath + "/" + domain_name + '-' + approach + '.txt'
				with open(path) as f:
					for l in f:
						line = l.strip().split(' ')
						if(line[0] == obs):
							if not printedObs:
								avgObs = float(0)
								print_metrics += '\n\t' + ('\\\\ & & ' if (obs != '25' and obs != '10') else ' & ') + obs + '\t & ' + str(avgObs) + '\n'
								printedObs = True
							
							if len(line) < 9:
								continue
							
							time = float(line[8])
							accuracy = (float(line[1]) * 100)
							spreadG = float(line[7])

							list_metrics = approaches_metrics[approach]
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
		time = (approaches_metrics[approach][0] / 5) / (len(domains))
		accuracy = (approaches_metrics[approach][1] / 5) / (len(domains))
		spread = (approaches_metrics[approach][2] / 5) / (len(domains))
		avg_approaches[approach] = [time, accuracy, spread]

	latexContent = ''
	with open('latex-results/goal_recognition-table-template.tex') as latex:
	    latexContent = latex.read()

	latexContent = latexContent.replace('<TABLE_LP_RESULTS>', content_table)

	index = 0
	for approach, name in zip(approaches, names):
		latexContent = latexContent.replace('<APPROACH_' + str(index) + '>', "$"+name+"$")
		latexContent = latexContent.replace('<AVG_APPROACH_' + str(index) + '>', str(avg_approaches[approach][0]) + ' & ' + str(avg_approaches[approach][1]) + '\% & ' + str(avg_approaches[approach][2]))
		index += 1

	with open('latex-results/goal_recognition-table.tex', 'w') as latex:
	    latex.write(latexContent)

if __name__ == '__main__' :
	# Domains with noisy observations.
	# domains = ['campus-noisy', 'easy-ipc-grid-noisy', 'intrusion-detection-noisy', 'kitchen-noisy']

	# Domains with missing observations.
	domains = ['campus']
	# domains = ['blocks-world-aaai', 'blocks-world', 'campus', 'depots', 'driverlog', 'dwr',\
	#  			'easy-ipc-grid', 'ferry', 'intrusion-detection', 'kitchen', 'logistics',\
	#  			 'miconic', 'rovers', 'satellite', 'sokoban', 'zeno-travel']

	# List of evaluated approaches.
	# approaches = ['diff-h-value-c-tb', 'diff-h-value-c', 'h-value-c-tb']
	approaches = ['h-value-c-uncertainty-tb', 'h-value-c-uncertainty', 'h-value-c']
	# approaches = ['h-value-tb', 'h-value', 'soft-c-tb', 'soft-c']
	path = "./results"
	parser = argparse.ArgumentParser(description="Generates LaTeX tables for plan recognition experiments")
	parser.add_argument('-d', '--domains', metavar="D", nargs='+', type=str, help="list of domains to tabulate data")
	parser.add_argument('-a', '--approaches', metavar="A", nargs='+', type=str, help="approaches to tabulate")
	parser.add_argument('-p', '--path', metavar="P", nargs=1, type=str, help="base path of data result files")
	parser.add_argument('-n', '--names', metavar="N", nargs='+', type=str, help="approach names to put in table")
	args = parser.parse_args()
	if args.domains:
		domains = args.domains
	if args.approaches:
		approaches = args.approaches
	if args.path:
		path=args.path[0]
	if args.names:
		if len(args.names) == len(approaches):
			names = args.names
		else:
			print("--names parameter requires the same number of names as --approaches")
			names = approaches
	else:
		names = approaches

	if len(approaches) > 3:
		print("The current implementation is limited to 3 approaches per table")
		exit(0)
	main(domains, approaches, path, names)