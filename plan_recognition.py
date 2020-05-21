#!/usr/bin/env python2.7

# Code originally developed by Miquel Ramirez
import sys, os, csv, time, math
from options import Program_Options

from delta_plan_recognizer import LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerDeltaHC, LPRecognizerDeltaHCUncertainty, LPRecognizerHValueCUncertainty, LPRecognizerDeltaHS, LPRecognizerDeltaHSUncertainty
from const_plan_recognizer import LPRecognizerSoftCUncertainty

def run_recognizer(recognizer):
    recognizer.run_recognizer()
    realHyp = recognizer.get_real_hypothesis()
    print("Real Goal is: %s\n\nRecognized: %s"%(str(realHyp),str(recognizer.unique_goal)))
    if recognizer.unique_goal is not None and realHyp == recognizer.unique_goal:
        print('True!')
    else:
        print('False!')
    print(recognizer.name)        

def main():
    cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    os.system(cmdClean)

    print(sys.argv)
    options = Program_Options(sys.argv[1:])

    recognizer = None
    if options.h_value:       
        recognizer = LPRecognizerHValue(options)          
    if options.h_value_c:
        recognizer = LPRecognizerHValueC(options)
    if options.delta_h_c:
        recognizer = LPRecognizerDeltaHC(options)
    if options.delta_h_s:
        recognizer = LPRecognizerDeltaHS(options)
    if options.soft_c:
        recognizer = LPRecognizerSoftC(options)
    if options.h_value_c_uncertainty:
        recognizer = LPRecognizerHValueCUncertainty(options)
    if options.delta_h_c_uncertainty:
        recognizer = LPRecognizerDeltaHCUncertainty(options)
    if options.delta_h_s_uncertainty:
        recognizer = LPRecognizerDeltaHSUncertainty(options)

    if recognizer != None:
        run_recognizer(recognizer)

if __name__ == '__main__':
    main()
