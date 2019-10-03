#!/usr/bin/env python2.7

import sys, os, csv, time, math, subprocess
DEVNULL = open(os.devnull,"r+b")
from plan_recognition import LPRecognizerDeltaHC, LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerHValueCUncertainty, LPRecognizerDeltaHCUncertainty, LPRecognizerDeltaHS, LPRecognizerDeltaHSUncertainty, Program_Options 
from planner_interface import Hypothesis, custom_partition
from plan_recognizer_factory import PlanRecognizerFactory

def progress(count, total, status=''):
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


class Experiment:
    def __init__(self, recognizer_name):
        self.unique_correct = 0        
        self.multi_tie_breaking_correct = 0
        self.multi_tie_breaking_spread = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.recognizer_name = recognizer_name
        self.totalTime = 0

    def reset(self):
        self.unique_correct = 0        
        self.multi_tie_breaking_correct = 0
        self.multi_tie_breaking_spread = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.totalTime = 0

    def run_experiment(self, options):
        print(self.recognizer_name)
        recognizer = PlanRecognizerFactory().get_recognizer(self.recognizer_name)
        
        startTime = time.time()
        recognizer.run_recognizer()
        experimentTime = time.time() - startTime
        self.totalTime += experimentTime
        
        if recognizer.unique_goal is not None and recognizer.get_real_hypothesis() == recognizer.unique_goal:
            self.unique_correct = self.unique_correct + 1
        if recognizer.get_real_hypothesis() in recognizer.multi_goal_tie_breaking:
            self.multi_tie_breaking_correct = self.multi_tie_breaking_correct + 1              
        if recognizer.get_real_hypothesis() in recognizer.multi_goal_no_tie_breaking:
            self.multi_correct = self.multi_correct + 1  
        self.multi_tie_breaking_spread = self.multi_tie_breaking_spread + len(recognizer.multi_goal_tie_breaking)            
        self.multi_spread = self.multi_spread  + len(recognizer.multi_goal_no_tie_breaking)
        self.candidate_goals = self.candidate_goals + len(recognizer.hyps)
        return recognizer.unique_goal is not None
    
    def __repr__(self):
        return "UC=%d MTBC=%d MTBS=%d MC=%d MS=%d CG=%d"%(self.unique_correct,self.multi_tie_breaking_correct,self.multi_tie_breaking_spread,self.multi_correct,self.multi_spread,self.candidate_goals)

def doExperiments(domainName, observability, recognizer_name):
    experiment_time = time.time()
    totalProblems = 0

    file_experiment = open("experiment.txt",'a')
    file_experiment.write(domainName+"\n")

    file_failures = open("failed.txt","w")

    print_text = "obs problems"
    experiments_result = "obs,problems"
    experiment_names = []
    experiments_tables = {}
    experiments_tables_tb = {}
    experiments = {}
    
    print_text = print_text + " " + recognizer_name
    experiments_result = experiments_result  + ","+recognizer_name
    experiment_names.append(recognizer_name)
    experiments[recognizer_name] = Experiment(recognizer_name) 
    experiments_tables[recognizer_name] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    experiments_tables_tb[recognizer_name] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    
    print_text = print_text + "\n"
    experiments_result = experiments_result + "\n"

    print_text = print_text + "\n"
    experiments_result = experiments_result + "\n"


    for obs in observability:
        problems = 0   
        for e in experiment_names:
            experiments[e].reset()       
        
        problems_path = 'experiments/' + domainName + '/' + obs + '/'
        total_problems = len(os.listdir(problems_path))
        for problem_file in os.listdir(problems_path):
            progress(problems, total_problems, e+":"+domainName+":"+str(obs)+"%")
            # progress(problems,total_problems,experiments[e].recognizer.name+":"+str(obs)+"%")
            if problem_file.endswith(".tar.bz2"):
                cmd_clean = 'rm -rf *.pddl *.dat *.log'
                os.system(cmd_clean)

                # print(problems_path + problem_file)
                cmd_untar = 'tar xvjf ' + problems_path + problem_file
                # cmd_untar = 'tar xjf ' + problems_path + problem_file
                os.system(cmd_untar)
                # cmd_untar = ['tar', 'xjf', problems_path + problem_file]
                # subprocess.call(cmd_untar,stdout=DEVNULL,stderr=DEVNULL)

                problems = problems + 1

                args = ['-e', problems_path + problem_file]

                options = Program_Options(args)
                for e in experiment_names:
                    success = experiments[e].run_experiment(options)
                    if not success:
                        file_failures.write(problems_path + problem_file + "\n")
                    # print("%s %r"%(e,experiments[e]))

        print_text_result = "%s %d "%(obs,problems)             
        totalProblems += problems
        for e in experiment_names:
            print_text_result = print_text_result + "%d "%(experiments[e].unique_correct)   
            
            experiments_tables[e] += "%s "%(obs)
            experiments_tables_tb[e] += "%s "%(obs)

            truePositives = float(experiments[e].multi_correct)
            trueNegatives = float(experiments[e].candidate_goals - experiments[e].multi_spread)
            falsePositives = float(experiments[e].multi_spread - experiments[e].multi_correct)
            falseNegatives = float(experiments[e].candidate_goals - experiments[e].multi_correct)
            # print("TP=%2.4f TN=%2.4f FP=%2.4f FN=%2.4f"%(truePositives,trueNegatives,falsePositives,falseNegatives))
            # print("TP=%2.4f TN=%2.4f FP=%2.4f FN=%2.4f MSpread=%2.4f MTBSpread=%2.4f"%(truePositives,trueNegatives,falsePositives,falseNegatives,experiments[e].multi_spread, experiments[e].multi_tie_breaking_spread))

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

            truePositives = float(experiments[e].multi_tie_breaking_correct)
            trueNegatives = float(experiments[e].candidate_goals - experiments[e].multi_tie_breaking_spread)
            falsePositives = float(experiments[e].multi_tie_breaking_spread - experiments[e].multi_tie_breaking_correct)
            falseNegatives = float(experiments[e].candidate_goals - experiments[e].multi_tie_breaking_correct)
            print("TP=%2.4f TN=%2.4f FP=%2.4f FN=%2.4f MSpread=%2.4f MTBSpread=%2.4f"%(truePositives,trueNegatives,falsePositives,falseNegatives,experiments[e].multi_spread, experiments[e].multi_tie_breaking_spread))

            accuracy = float(experiments[e].multi_tie_breaking_correct)/float(problems)
            precision = truePositives/float(experiments[e].multi_tie_breaking_spread) if experiments[e].multi_tie_breaking_spread != 0 else 0
            recall = truePositives/float(problems)
            if ((precision + recall) == 0):
                f1score = 0
            else:
                f1score = 2 * ((precision * recall) / (precision + recall))
            fallout = falsePositives / (trueNegatives + falsePositives)
            missrate = falseNegatives / (falseNegatives + truePositives)
            experiments_tables_tb[e] += "%2.4f "%(accuracy)
            experiments_tables_tb[e] += "%2.4f "%(precision)
            experiments_tables_tb[e] += "%2.4f "%(recall)
            experiments_tables_tb[e] += "%2.4f "%(f1score)
            experiments_tables_tb[e] += "%2.4f "%(fallout)
            experiments_tables_tb[e] += "%2.4f "%(missrate)
            experiments_tables_tb[e] += "%2.4f "%(float(experiments[e].multi_tie_breaking_spread)/float(problems))
            experiments_tables_tb[e] += "%2.4f "%(float(experiments[e].totalTime)/float(problems))
            experiments_tables_tb[e] += "\n"


        print_text_result = print_text_result + "\n"
        
        print_text = print_text + print_text_result

        print(str(domainName))
        print(print_text)
    
    for e in experiment_names:
        experiments_tables[e] += '\n$> Total Problems: ' + str(totalProblems)
        experiments_tables_tb[e] += '\n$> Total Problems: ' + str(totalProblems)
        table_file = open(str(domainName) + "-" + e +'.txt', 'w')
        table_file_tb = open(str(domainName) + "-" + e +'-tb.txt', 'w')
        table_file.write(experiments_tables[e])
        table_file_tb.write(experiments_tables_tb[e])
        table_file.close()
        table_file_tb.close()

    file_experiment.write(experiments_result)
    final_time = time.time() - experiment_time
    file_experiment.close()
    file_failures.close()
    print('Experiment Time: {0:3f}s'.format(final_time))


def main():
    domainName = sys.argv[1]
    #Totally unacceptable hack to have this script work with noisy domains
    if domainName.endswith("noisy"):
        observability = ['25', '50', '75', '100']
    else:
        observability = ['10', '30', '50', '70', '100']

    recognizer_name = None
    
    if "-v" in sys.argv:
        recognizer_name = "h-value"
    if "-c" in sys.argv:
        recognizer_name = "h-value-c"
    if "-s" in sys.argv:
        recognizer_name = "soft_c"
    if "-d" in sys.argv:
        recognizer_name = "delta-h-c"
    if "-f" in sys.argv:
        recognizer_name = "delta-h-s"
    if "-u" in sys.argv:
        recognizer_name = "h-value-c-uncertainty"
    if "-n" in sys.argv:
        recognizer_name = "delta-h-c-uncertainty"
    if "-k" in sys.argv:
        recognizer_name = "delta-h-s-uncertainty"

    doExperiments(domainName, observability, recognizer_name)

    # Get rid of the temp files
    cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    os.system(cmdClean)

if __name__ == '__main__':
    main()
