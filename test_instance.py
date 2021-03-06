#!/usr/bin/env python2.7

# Code originally developed by Miquel Ramirez
import sys, os, csv, time, math
from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory

if __name__ == '__main__':
    os.system('rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2')
    print(sys.argv)
    options = Program_Options(sys.argv[1:])
    recognizer = PlanRecognizerFactory(options).get_recognizer(options.recognizer_name)
    start_time = time.time()
    recognizer.run_recognizer()
    experiment_time = time.time() - start_time
    realHyp = recognizer.get_real_hypothesis()
    print("Real Goal is: %s" % str(realHyp))
    print("Recognized: %s" % str(recognizer.unique_goal))
    print("Spread: %s" % len(recognizer.accepted_hypotheses))
    print("Total time: %s" % experiment_time)
    if recognizer.unique_goal == None:
        print("No goal recognized!")
    elif realHyp == recognizer.unique_goal:
        print("Recognized true hypothesis!")
    elif realHyp in recognizer.accepted_hypotheses:
        print("Accepted true hypothesis!")
    else:
        print("Rejected true hypothesis.")
    print(recognizer.name)        
