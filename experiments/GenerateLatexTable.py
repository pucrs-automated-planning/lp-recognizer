#!/usr/bin/python
import sys
import os
import math

def main() :
	content_table = ''

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

		path = 'results/' + domain_name + '-' + approaches[0] + '.txt'
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
				path = 'results/' + domain_name + '-' + approach + '.txt'
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
	for approach in approaches:
		latexContent = latexContent.replace('<APPROACH_' + str(index) + '>', approach)
		latexContent = latexContent.replace('<AVG_APPROACH_' + str(index) + '>', str(avg_approaches[approach][0]) + ' & ' + str(avg_approaches[approach][1]) + '\% & ' + str(avg_approaches[approach][2]))
		index += 1

	with open('latex-results/goal_recognition-table.tex', 'w') as latex:
	    latex.write(latexContent)

if __name__ == '__main__' :
	main()