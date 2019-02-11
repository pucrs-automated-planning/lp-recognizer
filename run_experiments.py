#!/usr/bin/env python2

from plan_recognition import *

class Experiment:
    def __init__(self, h_value, h_value_c, soft_c, diff_h_value_c):
        self.unique_correct = 0        
        self.multi_tie_breaking_correct = 0
        self.multi_tie_breaking_spread = 0
        self.multi_correct = 0
        self.multi_spread  = 0
        self.h_value = h_value
        self.h_value_c = h_value_c
        self.soft_c = soft_c
        self.diff_h_value_c = diff_h_value_c

    def reset(self):
        self.unique_correct = 0        
        self.multi_tie_breaking_correct = 0
        self.multi_tie_breaking_spread = 0
        self.multi_correct = 0
        self.multi_spread  = 0

    def run_experiment(self, options):
        if self.h_value:
            recognizer = LPRecognizerHValue(options)       
        if self.h_value_c:
            recognizer = LPRecognizerHValueC(options)   
        if self.soft_c:  
            recognizer = LPRecognizerSoftC(options)                   
        if self.diff_h_value_c:
            recognizer = LPRecognizerDiffHValueC(options) 
        recognizer.run_recognizer()                   
                    
        if recognizer.unique_goal is not None and recognizer.get_real_hypothesis() == recognizer.unique_goal:
            self.unique_correct = self.unique_correct + 1
        if recognizer.get_real_hypothesis() in recognizer.multi_goal_tie_breaking:
            self.multi_tie_breaking_correct = self.multi_tie_breaking_correct + 1              
        if recognizer.get_real_hypothesis() in recognizer.multi_goal_no_tie_breaking:
            self.multi_correct = self.multi_correct + 1  
        self.multi_tie_breaking_spread = self.multi_tie_breaking_spread + len(recognizer.multi_goal_tie_breaking)            
        self.multi_spread = self.multi_spread  + len(recognizer.multi_goal_no_tie_breaking)

def doExperiments(domainName, observability, h_value, h_value_c, soft_c, diff_h_value_c):
    experiment_time = time.time()

    file_experiment = open("experiment.txt",'a')
    file_experiment.write(domainName+"\n")

    print_text = "obs problems"
    experiments_result = "obs,problems"
    experiments = []    
    if h_value:       
        print_text = print_text + " h-value"
        experiments_result = experiments_result  + ",h-value"        
        experiments.append(Experiment(True, False, False, False))        
    if h_value_c:
        print_text = print_text  + " h-value-c"          
        experiments_result = experiments_result  + ",h-value-c"          
        experiments.append(Experiment(False, True, False, False))        
    if soft_c:
        print_text = print_text  + " soft-c"     
        experiments_result = experiments_result  + ",soft-c"     
        experiments.append(Experiment(False, False, True, False))                
    if diff_h_value_c:
        print_text = print_text  + " diff-h-value-c"           
        experiments_result = experiments_result  + ",diff-h-value-c"           
        experiments.append(Experiment(False, False, False, True))
    print_text = print_text + "\n"
    experiments_result = experiments_result + "\n"

    if h_value:       
        experiments_result = experiments_result + ",,U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    if h_value_c:
        experiments_result = experiments_result + ",U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    if soft_c:
        experiments_result = experiments_result + ",U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    if diff_h_value_c:
        experiments_result = experiments_result + ",U,UA,MY,MYA,MYS,MN,MNA,MNS"    
    print_text = print_text + "\n"
    experiments_result = experiments_result + "\n"


    for obs in observability:
        problems = 0   
        for experiment in experiments:
            experiment.reset()       
        
        problems_path = 'experiments/' + domainName + '/' + obs + '/'
        for problem_file in os.listdir(problems_path):
            if problem_file.endswith(".tar.bz2"):
                cmd_clean = 'rm -rf *.pddl *.dat *.log'
                os.system(cmd_clean)

                print problems_path + problem_file
                cmd_untar = 'tar xvjf ' + problems_path + problem_file
                os.system(cmd_untar)

                problems = problems + 1

                args = ['-e', problems_path + problem_file]

                options = Program_Options(args)
                for experiment in experiments:
                    experiment.run_experiment(options)                         

        print_text_result = "%s %d "%(obs,problems)             
        result = "%s,%d"%(obs,problems) 
        for experiment in experiments:
            print_text_result = print_text_result + "%d "%(experiment.unique_correct)   
            
            result = result + ",%2.4f"%(experiment.unique_correct)    
            result = result + ",%2.4f"%(float(experiment.unique_correct)/float(problems))                
            result = result + ",%2.4f"%(experiment.multi_tie_breaking_correct)    
            result = result + ",%2.4f"%(float(experiment.multi_tie_breaking_correct)/float(problems))                
            result = result + ",%2.4f"%(float(experiment.multi_tie_breaking_spread)/float(problems))    
            result = result + ",%2.4f"%(experiment.multi_correct)    
            result = result + ",%2.4f"%(float(experiment.multi_correct)/float(problems))                
            result = result + ",%2.4f"%(float(experiment.multi_spread)/float(problems))                             

        print_text_result = print_text_result + "\n"
        result = result + "\n"    
        
        print_text = print_text + print_text_result
        experiments_result = experiments_result + result

        file_result = open(str(domainName) + '-goal_recognition.txt', 'w')
        print(str(domainName))
        print(print_text)
        file_result.write(experiments_result)
        file_result.close()
    file_experiment.write(experiments_result)
    final_time = time.time() - experiment_time
    file_experiment.close()
    print('Experiment Time: {0:3f}'.format(final_time))

def main():
    domainName = sys.argv[1]
    #Totally unacceptable hack to have this script work with noisy domains
    if domainName.endswith("noisy"):
        observability = ['25', '50', '75', '100']
    else:
        observability = ['10', '30', '50', '70', '100']

    h_value = False
    h_value_c = False
    diff_h_value_c = False
    soft_c = False
    if "-v" in sys.argv:
        h_value = True
    if "-c" in sys.argv:
        h_value_c = True
    if "-s" in sys.argv:
        soft_c = True        
    if "-d" in sys.argv:
        diff_h_value_c = True

    doExperiments(domainName, observability, h_value, h_value_c, soft_c, diff_h_value_c)

    # Get rid of the temp files
    cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    os.system(cmdClean)

if __name__ == '__main__':
    main()
