#!/usr/bin/env python2.7

import sys, os, csv, time, math, subprocess
DEVNULL = open(os.devnull,"r+b")
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory


EXP_FILTER = False
def filter(name):
    if EXP_FILTER:
        return ("_2.tar" in name) or ("_3.tar" in name) or ("hyp-4" in name) or ("hyp-3" in name)
    else:
        return False


class Experiment:

    def __init__(self):
        self.num_goals = 0.0
        self.num_obs = 0.0
        self.num_solutions = 0.0
        self.agreement = []
        self.fpr = []
        self.fnr = []
        self.spread  = []
        self.accuracy = 0.0
        self.perfect_agr = 0
        self.lp_time = []
        self.fd_time = 0.0
        self.total_time = 0.0
        self.max_time = 0.0
        self.real_h_values = []
        self.h_values = []
        self.real_hc_values = []
        self.hc_values = []

    def run_experiment(self, options):
        # print(self.recognizer_name)
        recognizer = PlanRecognizerFactory(options).get_recognizer(options.recognizer_name, options)
        self.recognizer_name = options.recognizer_name

        # Run
        start_time = time.time()
        recognizer.run_recognizer()
        experiment_time = time.time() - start_time

        solution_set = frozenset([h.atoms for h in recognizer.accepted_hypotheses])
        exact_solution_set = frozenset([h.atoms for h in recognizer.hyps if h.is_solution])
        real_hyp = recognizer.get_real_hypothesis()
        hyp = recognizer.unique_goal

        # Time results
        self.lp_time.append(recognizer.lp_time)
        self.fd_time += recognizer.fd_time
        self.total_time += experiment_time
        self.max_time = max(self.max_time, experiment_time)

        # Domain info
        self.num_obs += len(recognizer.observations)
        self.num_goals += len(frozenset([h.atoms for h in recognizer.hyps]))
        self.num_solutions += len(exact_solution_set)

        # Results
        total = float(len(exact_solution_set | solution_set))
        fp = float(len(solution_set - exact_solution_set))
        fn = float(len(exact_solution_set - solution_set))
        agr = (total - fp - fn) / total
        self.fpr.append(fp / total)
        self.fnr.append(fn / total)
        self.agreement.append(agr)
        self.spread.append(len(solution_set))

        if agr == 1:
            self.perfect_agr += 1
        if recognizer.get_real_hypothesis().atoms in solution_set:
            self.accuracy += 1

        print("=> LP-Solving Time: " + str(recognizer.lp_time))
        print("=> Fast Downward Time: " + str(recognizer.fd_time))
        print("=> Total Time: " + str(experiment_time))
        print("=> Recognized: " + str(exact_solution_set))

        # Constraints data
        self.real_h_values.append(real_hyp.h)
        self.h_values.append(hyp.h)
        self.real_hc_values.append(real_hyp.h_c)
        self.hc_values.append(hyp.h_c)

        return recognizer.unique_goal is None, [','.join(h) for h in solution_set], experiment_time, recognizer.lp_time, recognizer.fd_time


def do_experiments(base_path, domain_name, observability, recognizer, opt):
    experiment_time = time.time()

    options = Program_Options(['-r', recognizer] + opt)
    base_filename = domain_name + "-" + options.recognizer_name

    file_outputs = open(base_filename + ".success", "w")
    file_failures = open(base_filename + ".fail", "w")

    file_content = "#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tPER\tTime\tTimeLP\tTimeFD\n"
    for obs in observability:
        current_problem = 1
        exp_dir = domain_name + '/' + obs + '/'
        files = [exp_dir + file for file in os.listdir(base_path + exp_dir) if file.endswith(".tar.bz2") and not filter(file)]
        files.sort()
        experiment = Experiment()
        for exp_file in files:
            # Run
            os.system('rm -rf *.pddl *.dat *.log')
            options.extract_exp_file(base_path + exp_file)
            failed, output, time1, time2, time3 = experiment.run_experiment(options)
            # Output
            if failed:
                file_failures.write(exp_file + "\n")
            file_outputs.write(exp_file + ":" + str(time1) + ":" + str(time2) + ":" + str(time3) + "\n")
            for h in output:
                file_outputs.write("> " + h + "\n")
            print(options.recognizer_name + ":" + domain_name + ":" + str(obs) + "% - " + str(current_problem) + "/" + str(len(files)))
            current_problem += 1
        print("=> Max Time " + obs + "%: " + str(experiment.max_time))

        num_problems = float(len(files))
        file_content += "%s\t%s" % (len(files), obs)

        file_content += "\t%2.1f" % (experiment.num_obs / num_problems)
        file_content += "\t%2.1f" % (experiment.num_goals / num_problems)
        file_content += "\t%2.1f" % (experiment.num_solutions / num_problems)

        file_content += "\t%2.2f" % (sum(experiment.agreement) / num_problems)
        file_content += "\t%2.2f" % (sum(experiment.fpr) / num_problems)
        file_content += "\t%2.2f" % (sum(experiment.fnr) / num_problems)
        file_content += "\t%2.2f" % (experiment.accuracy / num_problems)
        file_content += "\t%2.2f" % (sum(experiment.spread) / num_problems)
        file_content += "\t%s" % experiment.perfect_agr

        file_content += "\t%2.4f" % (experiment.total_time / num_problems)
        file_content += "\t%2.4f" % (sum(experiment.lp_time) / num_problems)
        file_content += "\t%2.4f" % (experiment.fd_time / num_problems)
        file_content += "\n"

        file_hvalues = open("constraint-values/" + base_filename + "-" + obs + ".txt", "w")
        file_hvalues.write(str(experiment.real_h_values) + '\n')
        file_hvalues.write(str(experiment.h_values) + '\n')
        file_hvalues.write(str(experiment.spread) + '\n')
        file_hvalues.write(str(experiment.real_hc_values) + '\n')
        file_hvalues.write(str(experiment.hc_values) + '\n')
        file_hvalues.write(str(experiment.fpr) + '\n')
        file_hvalues.write(str(experiment.fnr) + '\n')
        file_hvalues.write(str(experiment.agreement) + '\n')
        file_hvalues.write(str(experiment.lp_time) + '\n')
        file_hvalues.close()


    table_file = open(base_filename + ".txt", 'w')
    table_file.write(file_content)
    table_file.close()

    final_time = time.time() - experiment_time
    file_failures.close()
    file_outputs.close()
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
    for approach in approaches.split():
        do_experiments(base_path + '/', domain_name, observability, approach, options)
    # Get rid of the temp files
    os.system('rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2')
