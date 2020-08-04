#!/usr/bin/env python2.7

import sys, os, csv, time, math, subprocess
DEVNULL = open(os.devnull,"r+b")
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory

class Experiment:

    def __init__(self):
        self.unique_correct = 0.0
        self.multi_correct = 0.0
        self.multi_spread  = 0.0
        self.num_goals = 0.0
        self.num_obs = 0.0
        self.num_solutions = 0.0
        self.total_time = 0.0
        self.fpr = 0.0
        self.fnr = 0.0
        self.agreement = 0.0

    def run_experiment(self, options):
        # print(self.recognizer_name)
        recognizer = PlanRecognizerFactory(options).get_recognizer(options.recognizer_name, options)
        self.recognizer_name = options.recognizer_name

        start_time = time.time()
        recognizer.run_recognizer()
        experimentTime = time.time() - start_time
        self.total_time += experimentTime
        self.num_goals += len(recognizer.hyps)
        self.num_obs += len(recognizer.observations)

        solution_set = set([h for h in recognizer.hyps if h.is_solution])
        self.num_solutions += len(solution_set)

        if recognizer.get_real_hypothesis() == recognizer.unique_goal:
            self.unique_correct += 1
        if recognizer.get_real_hypothesis() in recognizer.accepted_hypotheses:
            self.multi_correct += 1
        self.multi_spread += len(recognizer.accepted_hypotheses)

        total = float(len(solution_set | recognizer.accepted_hypotheses))
        fp = float(len(recognizer.accepted_hypotheses - solution_set))
        fn = float(len(solution_set - recognizer.accepted_hypotheses))
        self.fpr += fp / total
        self.fnr += fn / total
        self.agreement += (total - fp - fn) / total
        return not (recognizer.unique_goal is None)

    def __repr__(self):
        return "UC=%d MC=%d MS=%d CG=%d O=%d S=%d"%(self.unique_correct,self.multi_correct,self.multi_spread,self.num_goals,self.num_obs,self.num_solutions)

    def stats(self):
        return "AR=%2.4f FPR=%2.4f FNR=%2.4f MSpread=%2.4f" % (self.agreement, self.fpr, self.fnr, self.multi_spread)


def patch_exp_file(exp_file, domain_path):
    table_file = open(exp_file, 'r')
    header = table_file.readline()
    obs_results = [line.split("\t") for line in table_file.readlines()]
    table_file.close()
    if "|S|" in header:
        return
    file_content = header.replace("AR", "|S|\tAR")
    domain_path = domain_path.replace("-noisy", "")
    for r in obs_results:
        problem_dir = domain_path + '/' + r[1] + '/'
        files = [file for file in os.listdir(problem_dir) if file.endswith(".solution")]
        num_solutions = 0.0
        for solution_file in files:
            with open(problem_dir + solution_file) as f:

                num_solutions += len(f.readlines())
        r.insert(4, str(num_solutions / len(files)))
        file_content += "\t".join(r)
    table_file = open(exp_file, 'w')
    table_file.write(file_content)
    table_file.close()

def do_experiments(base_path, domain_name, observability, recognizer):
    experiment_time = time.time()

    options = Program_Options(['-r', recognizer])
    exp_file = domain_name + "-" + options.recognizer_name + ".txt"
    #if os.path.exists("results/" + exp_file):
    #    patch_exp_file("results/" + exp_file, base_path + '/' + domain_name)
    #    return

    file_failures = open("failed.txt","w")

    file_content = "#P\tO%\t|O|\t|G|\t|S|\tAR\tFPR\tFNR\tAcc\tSpread\tTime\n"
    for obs in observability:
        current_problem = 0
        problem_dir = base_path + '/' + domain_name + '/' + obs + '/'
        files = [file for file in os.listdir(problem_dir) if file.endswith(".tar.bz2")]
        experiment = Experiment()
        for problem_file in files:
            problem_path = problem_dir + problem_file
            current_problem += 1
            os.system('rm -rf *.pddl *.dat *.log')
            options.extract_exp_file(problem_path)
            success = experiment.run_experiment(options)
            if not success:
                file_failures.write(problem_dir + problem_file + "\n")
            print(experiment)
            print(experiment.stats())
            print(options.recognizer_name + ":" + domain_name + ":" + str(obs) + "% - " + str(current_problem) + "/" + str(len(files)))

        num_problems = float(len(files))
        print(experiment.num_solution, num_problems, experiment.num_solution / num_problems)
        file_content += "%s\t%s\t%s\t%s\t%s" % (len(files), obs, experiment.num_obs / num_problems, experiment.num_goals / num_problems, experiment.num_solutions / num_problems)
        file_content += "\t%2.4f" % (experiment.agreement / num_problems)
        file_content += "\t%2.4f" % (experiment.fpr / num_problems)
        file_content += "\t%2.4f" % (experiment.fnr / num_problems)
        file_content += "\t%2.4f" % (experiment.multi_correct / num_problems)
        file_content += "\t%2.4f" % (experiment.multi_spread / num_problems)
        file_content += "\t%2.4f" % (experiment.total_time / num_problems)
        file_content += "\n"

    table_file = open(exp_file, 'w')
    table_file.write(file_content)
    table_file.close()

    final_time = time.time() - experiment_time
    file_failures.close()
    print('Experiment Time: {0:3f}s'.format(final_time))

if __name__ == '__main__':
    observability = ['10', '30', '50', '70', '100']
    base_path = sys.argv[1]
    domain_name = sys.argv[2]
    for approach in sys.argv[3:]:
        do_experiments(base_path, domain_name, observability, approach)
    # Get rid of the temp files
    os.system('rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2')
