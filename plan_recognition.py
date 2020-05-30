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
    recognizer.run_recognizer()
    realHyp = recognizer.get_real_hypothesis()
    print("Real Goal is: %s\n\nRecognized: %s"%(str(realHyp),str(recognizer.unique_goal)))
    if recognizer.unique_goal is not None and realHyp == recognizer.unique_goal:
        print('True!')
    else:
        print('False!')
    print(recognizer.name)        
