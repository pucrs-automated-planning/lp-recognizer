#!/usr/bin/env python2.7

# Code originally developed by Miquel Ramirez
import sys, os, csv, time, math
from options import Program_Options
from operator import attrgetter

from planner_interface import Observations, PRCommand, Hypothesis
from delta_plan_recognizer import LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerOverlap, LPRecognizerDeltaHC, LPRecognizerDeltaHCUncertainty, LPRecognizerHValueCUncertainty, LPRecognizerDeltaHS, LPRecognizerDeltaHSUncertainty
from const_plan_recognizer import LPRecognizerSoftCUncertainty, LPRecognizerSoftC

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

    if options.h_value:
        recognizer = LPRecognizerHValue(options)
        run_recognizer(recognizer)
    if options.h_value_c:
        recognizer = LPRecognizerHValueC(options)
        run_recognizer(recognizer)
    if options.delta_h_c:
        recognizer = LPRecognizerDeltaHC(options)
        run_recognizer(recognizer)
    if options.delta_h_s:
        recognizer = LPRecognizerDeltaHS(options)
        run_recognizer(recognizer)
    if options.overlap:
        run_recognizer(LPRecognizerOverlap(options))
    if options.soft_c:
        recognizer = LPRecognizerSoftC(options)
        run_recognizer(recognizer)
    if options.h_value_c_uncertainty:
        recognizer = LPRecognizerHValueCUncertainty(options)
        run_recognizer(recognizer)
    if options.delta_h_c_uncertainty:
        recognizer = LPRecognizerDeltaHCUncertainty(options)
        run_recognizer(recognizer)
    if options.delta_h_s_uncertainty:
        recognizer = LPRecognizerDeltaHSUncertainty(options)
        run_recognizer(recognizer)

if __name__ == '__main__':
    main()
