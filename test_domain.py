#!/usr/bin/env python2.7

import sys, os, csv, time, math, subprocess
DEVNULL = open(os.devnull,"r+b")
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory


def progress(count, total, status=''):
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


class Experiment:
    def __init__(self):
        self.unique_correct = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.totalTime = 0

    def reset(self):
        self.unique_correct = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.totalTime = 0

    def run_experiment(self, options):
        # print(self.recognizer_name)
        recognizer = PlanRecognizerFactory(options).get_recognizer(options.recognizer_name, options)
        self.recognizer_name = options.recognizer_name

        startTime = time.time()
        recognizer.run_recognizer()
        experimentTime = time.time() - startTime
        self.totalTime += experimentTime

        if recognizer.unique_goal is not None and recognizer.get_real_hypothesis() == recognizer.unique_goal:
            self.unique_correct = self.unique_correct + 1
        if recognizer.get_real_hypothesis() in recognizer.accepted_hypotheses:
            self.multi_correct = self.multi_correct + 1
        self.multi_spread = self.multi_spread  + len(recognizer.accepted_hypotheses)
        self.candidate_goals = self.candidate_goals + len(recognizer.hyps)
        return recognizer.unique_goal is not None

    def __repr__(self):
        return "UC=%d MC=%d MS=%d CG=%d"%(self.unique_correct,self.multi_correct,self.multi_spread,self.candidate_goals)


def do_experiments(basePath, domainName, observability, experiment_names):
    experiment_time = time.time()
    totalProblems = 0

    file_failures = open("failed.txt","w")

    print_text = "obs problems"
    experiments_tables = {}
    experiments = {}

    for e in experiment_names:
        print_text = print_text + " " + e
        experiments[e] = Experiment()
        experiments_tables[e] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"

    print_text += print_text + "\n\n"

    for obs in observability:
        problems = 0
        for e in experiment_names:
            experiments[e].reset()
        problems_path = basePath + '/' + domainName + '/' + obs + '/'
        total_problems = len(os.listdir(problems_path))
        for problem_file in os.listdir(problems_path):
            if problem_file.endswith(".tar.bz2"):
                path = problems_path + problem_file
                os.system('rm -rf *.pddl *.dat *.log')
                os.system('tar xvjf ' + path)
                problems = problems + 1
                for e in experiment_names:
                    args = ['-r', e, '-e', problems_path + problem_file]
                    options = Program_Options(args)
                    success = experiments[e].run_experiment(options)
                    if not success:
                        file_failures.write(problems_path + problem_file + "\n")
                    progress(problems, total_problems, experiments[e].recognizer_name + ":" + domainName + ":" + str(obs) + "%")
                    print("")

        print_text_result = "%s %d "%(obs,problems)
        totalProblems += problems
        for e in experiment_names:
            print_text_result = print_text_result + "%d "%(experiments[e].unique_correct)

            experiments_tables[e] += "%s "%(obs)

            truePositives = float(experiments[e].multi_correct)
            trueNegatives = float(experiments[e].candidate_goals - experiments[e].multi_spread)
            falsePositives = float(experiments[e].multi_spread - experiments[e].multi_correct)
            falseNegatives = float(experiments[e].candidate_goals - experiments[e].multi_correct)
            print("TP=%2.4f TN=%2.4f FP=%2.4f FN=%2.4f MSpread=%2.4f"%(truePositives,trueNegatives,falsePositives,falseNegatives,experiments[e].multi_spread))

            accuracy = float(experiments[e].multi_correct)/float(problems)
            precision = truePositives/float(experiments[e].multi_spread) if experiments[e].multi_spread != 0 else 0
            recall = truePositives/float(problems)
            if ((precision + recall) == 0):
                f1score = 0
            else:
                f1score = 2 * ((precision * recall) / (precision + recall))
            fallout = falsePositives / (trueNegatives + falsePositives)
            missrate = falseNegatives / (falseNegatives + truePositives)
            experiments_tables[e] += "%2.4f "%(accuracy)
            experiments_tables[e] += "%2.4f "%(precision)
            experiments_tables[e] += "%2.4f "%(recall)
            experiments_tables[e] += "%2.4f "%(f1score)
            experiments_tables[e] += "%2.4f "%(fallout)
            experiments_tables[e] += "%2.4f "%(missrate)
            experiments_tables[e] += "%2.4f "%(float(experiments[e].multi_spread)/float(problems))
            experiments_tables[e] += "%2.4f "%(float(experiments[e].totalTime)/float(problems))
            experiments_tables[e] += "\n"

        print_text_result += print_text_result + "\n"
        print_text += print_text_result
        print(str(domainName))
        print(print_text)

    for e in experiment_names:
        experiments_tables[e] += '\n$> Total Problems: ' + str(totalProblems)
        table_file = open(str(domainName) + "-" + experiments[e].recognizer_name +'.txt', 'w')
        table_file.write(experiments_tables[e])
        table_file.close()

    final_time = time.time() - experiment_time
    file_failures.close()
    print('Experiment Time: {0:3f}s'.format(final_time))

if __name__ == '__main__':
    basePath = sys.argv[1]
    domainName = sys.argv[2]
    if domainName.endswith("noisy"):
        observability = ['25', '50', '75', '100']
    else:
        observability = ['10', '30', '50', '70', '100']
    do_experiments(basePath, domainName, observability, sys.argv[3:])
    # Get rid of the temp files
    os.system('rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2')
