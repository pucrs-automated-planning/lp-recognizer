#!/usr/bin/env python2

from plan_recognition import *

def doExperiments(domainName, observability, hvalue, constraints, rg, soft):
    totalProblems = 0
    counterProblems = 0
    experimentTime = time.time()

    fileExperiment = open("experiment.txt",'a')
    fileExperiment.write(domainName+"\n")

    experimentsResult = "Obs  Problems"
    if hvalue:       
        experimentsResult = experimentsResult  + " hvale"
    if constraints:
        experimentsResult = experimentsResult  + " constraints"
    if rg:
        experimentsResult = experimentsResult  + " rg"
    if soft:
        experimentsResult = experimentsResult  + " soft"        
    experimentsResult = experimentsResult + " Time\n"
    for obs in observability:
        startTime = time.time()
        counterProblems = 0
        hvalue_countRecognition = 0
        constraints_countRecognition = 0
        rg_countRecognition = 0
        soft_countRecognition = 0
        
        problems_path = 'experiments/' + domainName + '/' + obs + '/'
        for problem_file in os.listdir(problems_path):
            if problem_file.endswith(".tar.bz2"):
                cmdClean = 'rm -rf *.pddl *.dat *.log'
                os.system(cmdClean)

                print problems_path + problem_file
                cmdUntar = 'tar xvjf ' + problems_path + problem_file
                os.system(cmdUntar)

                counterProblems = counterProblems + 1

                args = ['-e', problems_path + problem_file]

                options = Program_Options(args)
                if hvalue:       
                    recognizer = LPRecognizer(options)       
                    recognizedGoals = recognizer.run_recognizer()                    
                    if recognizedGoals is not None and recognizer.get_real_hypothesis() == recognizedGoals:
                        hvalue_countRecognition = hvalue_countRecognition + 1    
                if constraints:
                    recognizer = LPRecognizerConstraints(options)
                    recognizedGoals = recognizer.run_recognizer()                    
                    if recognizedGoals is not None and recognizer.get_real_hypothesis() == recognizedGoals:
                        constraints_countRecognition = constraints_countRecognition + 1   
                if rg:
                    recognizer = LPRecognizerRG(options)
                    recognizedGoals = recognizer.run_recognizer()                    
                    if recognizedGoals is not None and recognizer.get_real_hypothesis() == recognizedGoals:
                        rg_countRecognition = rg_countRecognition + 1      
                if soft:  
                    recognizer = LPRecognizerSoft(options)
                    recognizedGoals = recognizer.run_recognizer()                    
                    if recognizedGoals is not None and recognizer.get_real_hypothesis() == recognizedGoals:
                        soft_countRecognition = soft_countRecognition + 1                          

        counterProblems = float(counterProblems)
        totalT = (time.time() - startTime)
        totalTime = float(totalT / counterProblems)                

    
        result = "%s \t %d \t "%(obs,counterProblems)    
        if hvalue:       
            result = result + "%d \t "%(hvalue_countRecognition)    
        if constraints:
            result = result + "%d \t "%(constraints_countRecognition)  
        if rg:
            result = result + "%d \t "%(rg_countRecognition)  
        if soft:
            result = result + "%d \t "%(soft_countRecognition)              
        result = result + "%2.4f\n"%(totalTime)    
        
        # result = obsPrint + '\t' + str(accuracy) + '\t' + str(precision) + '\t' + str(recall) + '\t' + str(f1score) + '\t' + str(fallout) + '\t' + str(missrate) + '\t' + str(avgRecognizedGoals) + '\t' + str(totalTime) + '\n';
        experimentsResult = experimentsResult + result
        totalProblems = totalProblems + counterProblems

        fileResult = open(str(domainName) + '-goal_recognition-lp.txt', 'w')
        print(str(domainName) + '-goal_recognition-lp.txt')
        print(experimentsResult)
        fileResult.write(experimentsResult)
        fileResult.close()
        fileExperiment.write(result)
    finalTime = time.time() - experimentTime
    fileExperiment.close()
    print('Experiment Time: {0:3f}'.format(finalTime))

def main():
    domainName = sys.argv[1]
    #Totally unacceptable hack to have this script work with noisy domains
    if domainName.endswith("noisy"):
        observability = ['25', '50', '75', '100']
    else:
        observability = ['10', '30', '50', '70', '100']

    hvalue = False
    constraints = False
    rg = False
    soft = False
    if "-v" in sys.argv:
        hvalue= True
    if "-c" in sys.argv:
        constraints= True
    if "-r" in sys.argv:
        rg= True
    if "-s" in sys.argv:
        soft= True

    doExperiments(domainName, observability, hvalue, constraints, rg, soft)

    # Get rid of the temp files
    cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    os.system(cmdClean)

if __name__ == '__main__':
    main()
