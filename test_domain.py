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
        self.accuracy = 0.0
        self.spread  = 0.0
        self.num_goals = 0.0
        self.num_obs = 0.0
        self.num_solutions = 0.0
        self.total_time = 0.0
        self.lp_time = 0.0
        self.fd_time = 0.0
        self.max_time = 0.0
        self.fpr = 0.0
        self.fnr = 0.0
        self.agreement = 0.0
        self.perfect_agr = 0

    def run_experiment(self, options):
        # print(self.recognizer_name)
        recognizer = PlanRecognizerFactory(options).get_recognizer(options.recognizer_name, options)
        self.recognizer_name = options.recognizer_name

        start_time = time.time()
        recognizer.run_recognizer()
        experiment_time = time.time() - start_time
        self.total_time += experiment_time
        self.lp_time += recognizer.lp_time
        self.fd_time += recognizer.fd_time
        self.max_time = max(self.max_time, experiment_time)

        solution_set = frozenset([h.atoms for h in recognizer.accepted_hypotheses])
        exact_solution_set = frozenset([h.atoms for h in recognizer.hyps if h.is_solution])

        self.num_obs += len(recognizer.observations)
        self.num_goals += len(frozenset([h.atoms for h in recognizer.hyps]))
        self.num_solutions += len(exact_solution_set)

        if recognizer.get_real_hypothesis().atoms in solution_set:
            self.accuracy += 1
        self.spread += len(solution_set)

        total = float(len(exact_solution_set | solution_set))
        fp = float(len(solution_set - exact_solution_set))
        fn = float(len(exact_solution_set - solution_set))
        self.fpr += fp / total
        self.fnr += fn / total
        self.agreement += (total - fp - fn) / total
        if total == len(exact_solution_set) and total == len(solution_set):
            self.perfect_agr += 1

        print("=> LP-Solving Time: " + str(recognizer.lp_time))
        print("=> Fast Downward Time: " + str(recognizer.fd_time))
        print("=> Total Time: " + str(experiment_time))
        print("=> Recognized: " + str(exact_solution_set))

        accepted = [','.join(h) for h in solution_set]
        return recognizer.unique_goal is None, accepted, experiment_time, recognizer.lp_time, recognizer.fd_time

    def __repr__(self):
        return "MC=%d MS=%d CG=%d O=%d S=%d" % (
            self.accuracy,
            self.spread,
            self.num_goals,
            self.num_obs,
            self.num_solutions)

    def stats(self):
        return "AR=%2.4f FPR=%2.4f FNR=%2.4f PA=%s" % (
            self.agreement, 
            self.fpr, 
            self.fnr, 
            self.perfect_agr)


def do_experiments(base_path, domain_name, observability, recognizer, opt):
    experiment_time = time.time()

    options = Program_Options(['-r', recognizer] + opt)
    results_file = domain_name + "-" + options.recognizer_name

    file_outputs = open(results_file + ".success", "w")
    file_failures = open(results_file + ".fail", "w")

    file_content = "#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tPER\tTime\tTimeLP\tTimeFD\n"
    for obs in observability:
        current_problem = 0
        exp_dir = domain_name + '/' + obs + '/'
        files = [file for file in os.listdir(base_path + exp_dir) if file.endswith(".tar.bz2") and not filter(file)]
        experiment = Experiment()
        for file_name in files:
            exp_file = exp_dir + file_name
            current_problem += 1
            os.system('rm -rf *.pddl *.dat *.log')
            options.extract_exp_file(base_path + exp_file)
            failed, output, time1, time2, time3 = experiment.run_experiment(options)
            if failed:
                file_failures.write(exp_file + "\n")
            file_outputs.write(exp_file + ":" + str(time1) + ":" + str(time2) + ":" + str(time3) + "\n")
            for h in output:
                file_outputs.write("> " + h + "\n")
            print(experiment)
            print(experiment.stats())
            print(options.recognizer_name + ":" + domain_name + ":" + str(obs) + "% - " + str(current_problem) + "/" + str(len(files)))
        print("=> Max Time " + obs + "%: " + str(experiment.max_time))

        num_problems = float(len(files))
        file_content += "%s\t%s" % (len(files), obs)

        file_content += "\t%2.1f" % (experiment.num_obs / num_problems)
        file_content += "\t%2.1f" % (experiment.num_goals / num_problems)
        file_content += "\t%2.1f" % (experiment.num_solutions / num_problems)

        file_content += "\t%2.2f" % (experiment.agreement / num_problems)
        file_content += "\t%2.2f" % (experiment.fpr / num_problems)
        file_content += "\t%2.2f" % (experiment.fnr / num_problems)
        file_content += "\t%2.2f" % (experiment.accuracy / num_problems)
        file_content += "\t%2.2f" % (experiment.spread / num_problems)
        file_content += "\t%s" % (experiment.perfect_agr)

        file_content += "\t%2.4f" % (experiment.total_time / num_problems)
        file_content += "\t%2.4f" % (experiment.lp_time / num_problems)
        file_content += "\t%2.4f" % (experiment.fd_time / num_problems)
        file_content += "\n"

    table_file = open(results_file + ".txt", 'w')
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
