#!/usr/bin/env python3

##
## Generate comparison (best agreement count) tables (data-comparison folder).
##

## Uses:
# For basic (optimal and sub-optimal) data sets:
# ./data_comparison.py lm "delta-cl delta-o-cl1" basic-all
# ./data_comparison.py dr "delta-o-cdt delta-o-cdto" basic-all
# ./data_comparison.py fl "delta-cf1 delta-o-cf17" basic-all
# For noisy data sets:
# ./data_comparison.py lmf2 "delta-cl-f2 delta-o-cl1-f2" noisy-all
# ./data_comparison.py drf2 "delta-o-cdt-f2 delta-o-cdto-f2" noisy-all
# ./data_comparison.py flf2 "delta-cf1-f2 delta-o-cf17-f2" noisy-all
##

import sys, os
import data_output as do
import data_domain as dd

def find_winning_methods(outputs, obs, problem_name):
	precision = 4
	best_agr = 0
	for i in range(len(outputs)):
		problem_output = outputs[i].experiments[obs].problem_outputs[problem_name]
		agr = round(problem_output.agreement, precision)
		if agr > best_agr:
			best_agr = agr
	winning_methods = []
	for i in range(len(outputs)):
		problem_output = outputs[i].experiments[obs].problem_outputs[problem_name]
		agr = round(problem_output.agreement, precision)
		if agr == best_agr:
			winning_methods.append(i)
	return winning_methods

def print_table(base_path, domain_name, methods, observabilities):
	domain_data = dd.DomainData(domain_name, observabilities)
	if os.path.exists("data-domains/" + domain_name + ".txt"):
		domain_data.read("data-domains/")
	else:
		domain_data.load(base_path)

	method_outputs = [do.MethodOutput(method, domain_data, "outputs/" if "delta" in method or "div" in method \
		else "../rg2009/results/" if "rg" in method \
		else "../lm2017/results/" ) for method in methods]
	content = '\t'.join(methods) + '\n'
	for o in range(len(observabilities)):
		score = [0] * len(method_outputs)
		for problem_name in domain_data.data[observabilities[o]].keys():
			winning_methods = find_winning_methods(method_outputs, o, problem_name)
			for i in winning_methods:
				score[i] += 1
		score = [str(s) for s in score]
		content += '\t'.join(score) + '\n'
	return content

if __name__ == '__main__':
	observabilities = ['10', '30', '50', '70', '100']
	base_path = "../goal-plan-recognition-dataset/"
	test = False
	if '-fast' in sys.argv:
		set_filter(True)
		dd.set_filter(True)
		sys.argv.remove('-fast')
	if '-test' in sys.argv:
		test = True
		sys.argv.remove('-test')
		base_path = "experiments/"
	domains = dd.parse_domains(sys.argv[3:], test)
	name = sys.argv[1]
	methods = sys.argv[2].split()
	for domain in domains:
		content = print_table(base_path, domain, methods, observabilities)
		with open("data-comparison/" + name + "-" + domain + ".txt", 'w') as f:
			f.write(content)