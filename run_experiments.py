#!/usr/bin/env python2

from plan_recognition import *


def doExperiments(domainName, observability, constraints):
    totalProblems = 0
    counterProblems = 0
    counterTruePositiveProblems = 0
    counterFalsePositiveProblems = 0
    candidateGoals = 0

    startTime = time.time()
    experimentsResult = "Obs  Accuracy  Precision  Recall  F1score  Fallout  Missrate  AvgRecG \t Total Time\n"

    for obs in observability:
        startTime = time.time()
        counterProblems = 0
        counterTruePositiveProblems = 0
        counterFalsePositiveProblems = 0
        candidateGoals = 0

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
                if constraints:
                    recognizer = LPRecognizerConstraints(options)
                else:
                    recognizer = LPRecognizer(options)

                goals = recognizer.hyps
                recognizedGoals = recognizer.run_recognizer()
                realGoal = recognizer.get_real_hypothesis()

                candidateGoals = candidateGoals + len(goals)

            if recognizedGoals is not None and realGoal in recognizedGoals:
                counterTruePositiveProblems = counterTruePositiveProblems + 1
                counterFalsePositiveProblems = counterFalsePositiveProblems + (len(recognizedGoals) - 1)
            else:
                counterTruePositiveProblems = counterTruePositiveProblems + 1
                counterFalsePositiveProblems = counterFalsePositiveProblems + (len(goals))

        totalCandidateGoals = float(candidateGoals / counterProblems)
        counterProblems = float(counterProblems)
        counterTruePositiveProblems = float(counterTruePositiveProblems)
        trueNegativeCounter = float((counterProblems * (candidateGoals / counterProblems)) - counterFalsePositiveProblems)
        trueNegativeCounter = float(trueNegativeCounter)
        falseNegativeCounter = float(counterProblems - counterTruePositiveProblems)
        accuracy = float(counterTruePositiveProblems / counterProblems)
        precision = float(counterTruePositiveProblems / (counterTruePositiveProblems + counterFalsePositiveProblems))
        recall = float(counterTruePositiveProblems / (counterTruePositiveProblems + falseNegativeCounter))
        if ((precision + recall) == 0):
            f1score = 0
        else:
            f1score = 2 * ((precision * recall) / (precision + recall))
        fallout = counterFalsePositiveProblems / (trueNegativeCounter + counterFalsePositiveProblems)
        missrate = float(falseNegativeCounter / (falseNegativeCounter + counterTruePositiveProblems))
        totalT = (time.time() - startTime)
        totalTime = float(totalT / counterProblems)
        avgRecognizedGoals = float((counterFalsePositiveProblems + counterTruePositiveProblems) / counterProblems)
        obsPrint = obs
        if obs == 'full':
            obsPrint = '100'
        
        result = "%s \t %2.4f  \t  %2.4f  \t %2.4f \t %2.4f \t %2.4f \t %2.4f \t %2.4f \t %6.4f\n"%(obsPrint,accuracy,precision,recall,f1score,fallout,missrate,avgRecognizedGoals,totalTime)
        # result = obsPrint + '\t' + str(accuracy) + '\t' + str(precision) + '\t' + str(recall) + '\t' + str(f1score) + '\t' + str(fallout) + '\t' + str(missrate) + '\t' + str(avgRecognizedGoals) + '\t' + str(totalTime) + '\n';
        experimentsResult = experimentsResult + result
        totalProblems = totalProblems + counterProblems

        fileResult = open(str(domainName) + '-goal_recognition-lp.txt', 'w')
        print(str(domainName) + '-goal_recognition-lp.txt')
        print(experimentsResult)
        print( '$> Total Problems: ' + str(totalProblems))
        fileResult.write(experimentsResult)
        fileResult.close()


def main():
    domainName = sys.argv[1]
    if len(sys.argv) > 2:
        constraints = (sys.argv[2]=="-c")
    else:
        constraints = False
    #Totally unacceptable hack to have this script work with noisy domains
    if domainName.endswith("noisy"):
        observability = ['25', '50', '75', '100']
    else:
        observability = ['10', '30', '50', '70', '100']

    doExperiments(domainName, observability, constraints)

    # Get rid of the temp files
    cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    os.system(cmdClean)

if __name__ == '__main__':
    main()
