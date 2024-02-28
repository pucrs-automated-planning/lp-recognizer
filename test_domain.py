#!/usr/bin/env python3

import sys, os, time
DEVNULL = open(os.devnull,"r+b")
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory
import data_output as do

EXP_FILTER = False
def filter(name):
    if EXP_FILTER:
        return ("_2.tar" in name) or ("_3.tar" in name) or ("hyp-4" in name) or ("hyp-3" in name)
    else:
        return False


def do_experiments(base_path, domain_name, observability, recognizer, opt):
    experiment_time = time.time()
    options = Program_Options(['-r', recognizer] + opt)
    base_filename = domain_name + "-" + options.recognizer_name
    file_outputs = open("outputs/" + base_filename + ".output", "w")
    file_charts = open("data-charts/" + base_filename + ".txt", "w")
    file_latex = open("data-tables/" + base_filename + ".txt", 'w')
    file_latex.write("#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tPER\tTime\tTimeLP\tTimeFD\tVars\tConsts\tH\tHC\n")
    for obs in observability:
        current_problem = 0
        exp_dir = domain_name + '/' + obs + '/'
        files = [exp_dir + file for file in os.listdir(base_path + exp_dir) if file.endswith(".tar.bz2") and not filter(file)]
        files.sort()
        experiment = do.ExperimentOutput(obs)
        for exp_file in files:
            current_problem += 1
            print(options.recognizer_name + ":" + domain_name + ":" + str(obs) + "% - " + str(current_problem) + "/" + str(len(files)))
            # Run
            os.system('rm -rf ./*.pddl ./*.dat ./*.log')
            options.extract_exp_file(base_path + exp_file)
            recognizer = PlanRecognizerFactory(options).get_recognizer(options.recognizer_name, options)
            recognizer.run_recognizer()
            # Log
            print("=> LP-Solving Time: " + str(recognizer.lp_time))
            print("=> Fast Downward Time: " + str(recognizer.fd_time))
            print("=> Total Time: " + str(recognizer.total_time))
            output = do.ProblemOutput(exp_file, recognizer)
            experiment.add_problem(output)
            file_outputs.write(output.print_content())
        print("=> Max Time " + obs + "%: " + str(experiment.max_time))
        file_latex.write(experiment.print_stats())
        file_charts.write(experiment.print_hdata())
    file_latex.close()
    file_charts.close()
    file_outputs.close()
    final_time = time.time() - experiment_time
    print('Experiment Time: {0:3f}s'.format(final_time))


if __name__ == '__main__':
    observability = ['10', '30', '50', '70', '100']
    base_path = sys.argv[1]
    domain_name = sys.argv[2]
    approaches = sys.argv[3]
    options = sys.argv[4:]
    if '-fast' in options:
        EXP_FILTER = True
        options.remove('-fast')
    if '-full' in options:
        EXP_FILTER = False
        options.remove('-full')
    if '-test' in options:
        options.remove('-test')
    for approach in approaches.split():
        do_experiments(base_path, domain_name, observability, approach, options)
    # Get rid of the temp files
    #os.system('bash cleanup.sh')
