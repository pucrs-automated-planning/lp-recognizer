#!/usr/bin/env python2.7

import sys, os
import output_format as of
import domain_data as dd

def find_winning_methods(experiments, obs, problem_name):
    precision = 3
    best_agr = 0
    for i in range(len(experiments)):
        problem_output = experiments[i][obs].problem_outputs[problem_name]
        agr = round(problem_output.agreement, precision)
        if agr > best_agr:
            best_agr = agr
    winning_methods = []
    for i in range(len(experiments)):
        problem_output = experiments[i][obs].problem_outputs[problem_name]
        agr = round(problem_output.agreement, precision)
        if agr == best_agr:
            winning_methods.append(i)
    return winning_methods

def print_table(base_path, domain_name, methods, observabilities):
    domain_data = dd.DomainData(domain_name, observabilities)
    if os.path.exists(domain_name + ".txt"):
        domain_data.read()
    else:
        domain_data.load(base_path)
    experiments = []
    for method in methods:
        experiments.append(of.read_output(base_path, domain_data, method))
    content = '\t'.join(methods) + '\n'
    for o in range(len(observabilities)):
        score = [0] * len(experiments)
        for problem_name in domain_data.data[observabilities[o]].keys():
            winning_methods = find_winning_methods(experiments, o, problem_name)
            for i in winning_methods:
                score[i] += 1
        score = [str(s) for s in score]
        content += '\t'.join(score) + '\n'
    return content

if __name__ == '__main__':
    observabilities = ['10', '30', '50', '70', '100']
    base_path = '../goal-plan-recognition-dataset/'
    # Domains
    fast = False
    if '-fast' in sys.argv:
        fast = True
        sys.argv.remove('-fast')
    if fast:
        domains = [
        'blocks-world-optimal', 
        'depots-optimal', 
        'driverlog-optimal', 
        'dwr-optimal', 
        'rovers-optimal', 
        'sokoban-optimal'
        ]
    else:
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
    name = sys.argv[1]
    methods = sys.argv[2:]
    for domain in domains:
        content = print_table(base_path, domain, methods, observabilities)
        with open("data-comparison/" + name + "-" + domain_name + ".txt", 'w') as f:
            f.write(content)