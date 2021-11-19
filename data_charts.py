#!/usr/bin/env python2.7

##
## Generate .dat files for charts (data-charts folder).
##

## Uses:
# For especific domains:
# ./data_charts.py "delta-cl delta-o-cl1" blocks-world-optimal depots-optimal -stats [-fast]
# For all domains:
# ./data_charts.py "delta-cl delta-o-cl1" all -stats [-fast]
# For method groups:
# ./data_charts.py lm optimal -scatter -stats [-fast]
# ./data_charts.py fl optimal -scatter -stats [-fast]
# ./data_charts.py dr optimal -stats [-fast]
##

import os, sys
import data_domain as dd
import data_output as do

class ObsStats:

	#
	# The results for the set of goal recognition tasks for a single observatility level.
	#

	def __init__(self, obs):
		self.level = obs
		self.points = dict()
		self.win = [0, 0, 0]  # better, worse, draw
		self.quads = [0, 0, 0, 0] # Q1, Q2, Q3, Q4
		self.axis = [0, 0, 0, 0, 0] # Origin, X left, X right, Y bottom, Y right

	def count_hvalues(self, problem, experiments):
		for h in range(len(problem.hyps)):
			hc = [m.problem_outputs[problem.name].scores[h][1] \
				if h in m.problem_outputs[problem.name].scores else 100 \
				for m in experiments]
			line = ' '.join([str(x) for x in hc])
			if line in self.points:
				self.points[line] += 1
			else:
				self.points[line] = 1
			agr = [m.problem_outputs[problem.name].agreement for m in experiments]
			if hc[0] > hc[1]:
				self.win[0] += 1
				if agr[0] > agr[1]:
					self.quads[2] += 1
				elif agr[1] > agr[0]:
					self.quads[1] += 1
				else:
					self.axis[1] += 1
			elif hc[1] > hc[0]:
				self.win[1] += 1
				if agr[0] > agr[1]:
					self.quads[3] += 1
				elif agr[1] > agr[0]:
					self.quads[0] += 1
				else:
					self.axis[2] += 1
			else:
				self.win[2] += 1
				if agr[0] > agr[1]:
					self.axis[3] += 1
				elif agr[1] > agr[0]:
					self.axis[4] += 1
				else:
					self.axis[0] += 1

	def print_points(self):
		return '\n'.join([line + " " + str(c) for line, c in self.points.items()])

	def print_stats(self, methods):
		content = methods[0] + " vs " + methods[1] + '\n'
		content += methods[0] + " higher than " + methods[1] + ": %.2f" % self.win[0] + "%\n"
		content += methods[1] + " higher than " + methods[0] + ": %.2f" % self.win[1] + "%\n"
		content += methods[0] + " equal to " + methods[1] + ": %.2f" % self.win[2] + "%\n"
		for i in range(0, 4):
			content += "Q%s: %s" % (i + 1, self.quads[i]) + '\n'
		content += "Axis X (left): %s" % self.axis[1] + '\n'
		content += "Axis X (right): %s" % self.axis[2] + '\n'
		content += "Axis Y (bottom): %s" % self.axis[3] + '\n'
		content += "Axis Y (top): %s" % self.axis[4] + '\n'
		content += "Origin: %s" % self.axis[0] + '\n'
		return content

	def count_sums(self, problem, experiments):
		ref = frozenset(problem.get_solution_indexes())
		nonref = frozenset(problem.get_hyp_indexes()) - ref
		# (\sum h1(s_0,s*_i) > h2(s_0,s*_i) for i in \Gamma*) / |\Gamma*|
		sums_ref = []
		# (\sum h1(s_0,s*_i) > h2(s_0,s*_i) for i in \Gamma* - \Gamma) / |\Gamma* - \Gamma|
		sums_nonref = []
		for exp in experiments:
			sums_ref.append(sum([ 1 for hyp in ref if \
				exp.problem_outputs[problem.name].scores[hyp][1] > \
				exp.problem_outputs[problem.name].scores[hyp][0] ]))
			sums_nonref.append(sum([ 1 for hyp in nonref if \
				hyp not in exp.problem_outputs[problem.name].scores or \
				exp.problem_outputs[problem.name].scores[hyp][1] > \
				exp.problem_outputs[problem.name].scores[hyp][0] ]))
		sums_ref.append(sum([ 1 for hyp in ref if \
			experiments[1].problem_outputs[problem.name].scores[hyp][1] > \
			experiments[0].problem_outputs[problem.name].scores[hyp][1] ]))
		sums_nonref.append(sum([ 1 for hyp in nonref if \
			hyp not in experiments[1].problem_outputs[problem.name].scores or \
			hyp in experiments[0].problem_outputs[problem.name].scores and \
			experiments[1].problem_outputs[problem.name].scores[hyp][1] > \
			experiments[0].problem_outputs[problem.name].scores[hyp][1] ]))
		return sums_ref, sums_nonref

	def compute_sum_points(self, problems, experiments):
		self.sum_points = [[], [], []]
		for p in problems:
			sums_ref, sums_nonref = self.count_sums(p, experiments)
			self.sum_points[0].append((sums_ref[0], sums_ref[1]))
			self.sum_points[1].append((sums_nonref[0], sums_nonref[1]))
			self.sum_points[2].append((sums_nonref[2], sums_ref[2]))

	def print_sum_points(self, i):
		return '\n'.join(["%s\t%s" % p for p in self.sum_points[i]])


def write_dat_files(all_domain_data, methods, observabilities, chart_name = None, scatter = True, stats = True, sums = True):
	obs_stats = [ObsStats(o) for o in range(len(observabilities))]
	for domain_data in all_domain_data.values():
		method_outputs = [do.MethodOutput(method, domain_data) for method in methods]
		for o in range(len(observabilities)):
			method_experiments = [m.experiments[o] for m in method_outputs]
			problems = domain_data.data[observabilities[o]].values()
			for p in problems:
				obs_stats[o].count_hvalues(p, method_experiments)
			obs_stats[o].compute_sum_points(problems, method_experiments)
	if not chart_name:
		chart_name = ' vs '.join(methods) 
	header = ' '.join(["x%s" % i for i in range(len(methods))]) + " w \n"
	for o in range(len(observabilities)):
		if scatter:
			content = obs_stats[o].print_points()
			with open("data-charts/" + chart_name + "-" + observabilities[o] + "-scatter-all.dat", 'w') as f:
				f.write(header + content)
		if stats: 
			content = obs_stats[o].print_stats(methods)
			with open("data-charts/" + chart_name + "-" + observabilities[o] + "-stats.dat", 'w') as f:
				f.write(content)
		if sums:
			for i in range(0, 3):
				content = obs_stats[o].print_sum_points(i)
				with open("data-charts/" + chart_name + "-" + observabilities[o] + "-sums%d.dat" % i, 'w') as f:
					f.write(content)

if __name__ == '__main__':
	observabilities = ['10', '30', '50', '70']
	base_path = '../goal-plan-recognition-dataset/'

	# Flags
	test = False
	scatter = False
	stats = False
	sums = False
	if '-fast' in sys.argv:
		set_filter(True)
		dd.set_filter(True)
		sys.argv.remove('-fast')
	if '-test' in sys.argv:
		test = True
		sys.argv.remove('-test')
		base_path = 'experiments/'

	# Domains
	domains = dd.parse_domains(sys.argv[2:], test)
	all_domain_data = {}
	for d in domains:
		domain_data = dd.DomainData(d, observabilities)
		if os.path.exists("data-domains/" + d + ".txt"):
			domain_data.read("data-domains/")
		else:
			domain_data.load(base_path)
		all_domain_data[d] = domain_data

	# Methods
	methods = sys.argv[1]
	chart_name = None
	if methods == 'lm':
		methods = ["delta-cl", "delta-o-cl1"]
		chart_name = "LMC-vs-LMC+soft"
	elif methods == 'dr':
		methods = ["delta-o-cdt", "delta-o-cdto"]
		chart_name = "DEL+1-vs-DEL+2"
	elif methods == 'fl':
		methods = ["delta-cf1", "delta-o-cf17"]
		chart_name = "F1-vs-FOPxEIntra"
	else:
		methods = methods.split()

	write_dat_files(all_domain_data, methods, observabilities, \
		chart_name, scatter, stats, sums)