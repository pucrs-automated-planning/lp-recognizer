#!/usr/bin/env python3.7

import sys, os, csv, time, math, subprocess
DEVNULL = open(os.devnull,"r+b")
from plan_recognition import LPRecognizerDeltaHC, LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerHValueCUncertainty, LPRecognizerDeltaHCUncertainty, LPRecognizerDeltaHS, LPRecognizerDeltaHSUncertainty, Program_Options 
from planner_interface import Hypothesis, custom_partition

def progress(count, total, status=''):
    bar_len = 30
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


class Experiment:
    def __init__(self, h_value = False, h_value_c = False, soft_c = False, delta_h_c = False, h_value_c_uncertainty=False, delta_h_c_uncertainty = False, delta_h_s = False, delta_h_s_uncertainty = False):
        self.unique_correct = 0        
        self.multi_tie_breaking_correct = 0
        self.multi_tie_breaking_spread = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.candidate_goals = 0
        self.h_value = h_value
        self.h_value_c = h_value_c
        self.soft_c = soft_c
        self.delta_h_c = delta_h_c
        self.delta_h_s = delta_h_s
        self.h_value_c_uncertainty = h_value_c_uncertainty
        self.delta_h_c_uncertainty = delta_h_c_uncertainty
        self.delta_h_s_uncertainty = delta_h_s_uncertainty
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
        if self.h_value:
            # print("h_value")
            recognizer = LPRecognizerHValue(options)       
        if self.h_value_c:
            # print("h_value_c")
            recognizer = LPRecognizerHValueC(options)   
        if self.soft_c:  
            # print("soft_c")
            recognizer = LPRecognizerSoftC(options)                   
        if self.delta_h_c:
            # print("delta_h_c")
            recognizer = LPRecognizerDeltaHC(options)
        if self.delta_h_s:
            # print("delta_h_s")
            recognizer = LPRecognizerDeltaHS(options)
        if self.h_value_c_uncertainty:
            # print("h_value_c_uncertainty")
            recognizer = LPRecognizerHValueCUncertainty(options)
        if self.delta_h_c_uncertainty:
            # print("delta_h_c_uncertainty")
            recognizer = LPRecognizerDeltaHCUncertainty(options)
        if self.delta_h_s_uncertainty:
            # print("delta_h_s_uncertainty")
            recognizer = LPRecognizerDeltaHSUncertainty(options)
        
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

def doExperiments(domainName, observability, h_value, h_value_c, soft_c, delta_h_c, h_value_c_uncertainty, delta_h_c_uncertainty, delta_h_s, delta_h_s_uncertainty):
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
    if h_value:
        print_text = print_text + " h-value"
        experiments_result = experiments_result  + ",h-value"
        experiment_names.append("h-value")
        experiments["h-value"] = Experiment(h_value=True) 
        experiments_tables["h-value"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["h-value"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    if h_value_c:
        print_text = print_text  + " h-value-c"          
        experiments_result = experiments_result  + ",h-value-c"
        experiment_names.append("h-value-c")
        experiments["h-value-c"] = Experiment(h_value_c=True)
        experiments_tables["h-value-c"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["h-value-c"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    if soft_c:
        print_text = print_text  + " soft-c"     
        experiments_result = experiments_result  + ",soft-c"
        experiment_names.append("soft-c")
        experiments["soft-c"] = Experiment(soft_c=True)
        experiments_tables["soft-c"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["soft-c"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    if delta_h_c:
        print_text = print_text  + " delta-h-c"
        experiments_result = experiments_result  + ",delta-h-c"
        experiment_names.append("delta-h-c")
        experiments["delta-h-c"] = Experiment(delta_h_c=True)
        experiments_tables["delta-h-c"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["delta-h-c"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    if delta_h_s:
        print_text = print_text  + " delta-h-s"
        experiments_result = experiments_result  + ",delta-h-s"
        experiment_names.append("delta-h-s")
        experiments["delta-h-s"] = Experiment(delta_h_s=True)
        experiments_tables["delta-h-s"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["delta-h-s"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    if h_value_c_uncertainty:
        print_text = print_text  + " h-value-c-uncertainty"
        experiments_result = experiments_result  + ",h-value-c-uncertainty"
        experiment_names.append("h-value-c-uncertainty")
        experiments["h-value-c-uncertainty"] = Experiment(h_value_c_uncertainty=True)
        experiments_tables["h-value-c-uncertainty"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["h-value-c-uncertainty"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    if delta_h_c_uncertainty:
        print_text = print_text  + " delta-h-c-uncertainty"
        experiments_result = experiments_result  + ",delta-h-c-uncertainty"
        experiment_names.append("delta-h-c-uncertainty")
        experiments["delta-h-c-uncertainty"] = Experiment(delta_h_c_uncertainty=True)
        experiments_tables["delta-h-c-uncertainty"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["delta-h-c-uncertainty"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
    if delta_h_s_uncertainty:
        print_text = print_text  + " delta-h-s-uncertainty"
        experiments_result = experiments_result  + ",delta-h-s-uncertainty"
        experiment_names.append("delta-h-s-uncertainty")
        experiments["delta-h-s-uncertainty"] = Experiment(delta_h_s_uncertainty=True)
        experiments_tables["delta-h-s-uncertainty"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"
        experiments_tables_tb["delta-h-s-uncertainty"] = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG Total Time\n"

    print_text = print_text + "\n"
    experiments_result = experiments_result + "\n"

    if h_value:
        experiments_result = experiments_result + ",,U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    if h_value_c:
        experiments_result = experiments_result + ",U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    if soft_c:
        experiments_result = experiments_result + ",U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    if delta_h_c:
        experiments_result = experiments_result + ",U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    if h_value_c_uncertainty:
        experiments_result = experiments_result + ",U,UA,MY,MYA,MYS,MN,MNA,MNS"    
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
        result = "%s,%d"%(obs,problems) 
        totalProblems += problems
        for e in experiment_names:
            print_text_result = print_text_result + "%d "%(experiments[e].unique_correct)   
            
            result = result + ",%2.4f"%(experiments[e].unique_correct)    
            result = result + ",%2.4f"%(float(experiments[e].unique_correct)/float(problems))                
            result = result + ",%2.4f"%(experiments[e].multi_tie_breaking_correct)    
            result = result + ",%2.4f"%(float(experiments[e].multi_tie_breaking_correct)/float(problems)) 
            result = result + ",%2.4f"%(float(experiments[e].multi_tie_breaking_spread)/float(problems))
            result = result + ",%2.4f"%(experiments[e].multi_correct)
            result = result + ",%2.4f"%(float(experiments[e].multi_correct)/float(problems))                
            result = result + ",%2.4f"%(float(experiments[e].multi_spread)/float(problems))

            experiments_tables[e] += "%s "%(obs)
            experiments_tables_tb[e] += "%s "%(obs)

            truePositives = float(experiments[e].multi_correct)
            trueNegatives = float(experiments[e].candidate_goals - experiments[e].multi_spread)
            falsePositives = float(experiments[e].multi_spread - experiments[e].multi_correct)
            falseNegatives = float(experiments[e].candidate_goals - experiments[e].multi_correct)
            # print("TP=%2.4f TN=%2.4f FP=%2.4f FN=%2.4f"%(truePositives,trueNegatives,falsePositives,falseNegatives))
            print("TP=%2.4f TN=%2.4f FP=%2.4f FN=%2.4f MSpread=%2.4f MTBSpread=%2.4f"%(truePositives,trueNegatives,falsePositives,falseNegatives,experiments[e].multi_spread, experiments[e].multi_tie_breaking_spread))

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
        result = result + "\n"    
        
        print_text = print_text + print_text_result
        experiments_result = experiments_result + result

        file_result = open(str(domainName) + '-goal_recognition.txt', 'w')
        print(str(domainName))
        print(print_text)
        file_result.write(experiments_result)
        file_result.close()
    
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

    h_value = False
    h_value_c = False
    soft_c = False
    delta_h_c = False
    delta_h_s = False
    h_value_c_uncertainty = False
    delta_h_c_uncertainty = False
    delta_h_s_uncertainty = False
    
    if "-v" in sys.argv:
        h_value = True
    if "-c" in sys.argv:
        h_value_c = True
    if "-s" in sys.argv:
        soft_c = True        
    if "-d" in sys.argv:
        delta_h_c = True
    if "-f" in sys.argv:
        delta_h_s = True
    if "-u" in sys.argv:
        h_value_c_uncertainty = True
    if "-n" in sys.argv:
        delta_h_c_uncertainty = True
    if "-k" in sys.argv:
        delta_h_s_uncertainty = True

    doExperiments(domainName, observability, h_value, h_value_c, soft_c, delta_h_c, h_value_c_uncertainty, delta_h_c_uncertainty, delta_h_s, delta_h_s_uncertainty)

    # Get rid of the temp files
    cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    os.system(cmdClean)

if __name__ == '__main__':
    main()
