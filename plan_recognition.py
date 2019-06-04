#!/usr/bin/env python2

# Code originally developed by Miquel Ramirez
import sys, os, csv, time, math
from options import Program_Options
from operator import attrgetter

from planner_interface import Observations, PRCommand, Hypothesis

class PlanRecognizer:
    
    def __init__(self, options):
        self.options = options
        self.observations = Observations('obs.dat')
        self.hyps = self.load_hypotheses()
        self.unique_goal = None
        self.multi_goal_tie_breaking = []
        self.multi_goal_no_tie_breaking = []
        self.multi_goal_missing_compensation = [] # 
        self.name = None

    def load_hypotheses(self):
        hyps = []
        instream = open('hyps.dat')

        for line in instream:
            line = line.strip()
            H = Hypothesis()
            H.atoms = [tok.strip() for tok in line.split(',')]
            H.check_if_actual()
            hyps.append(H)

        instream.close()

        return hyps

    def get_real_hypothesis(self):
        for h in self.hyps:
            if h.is_true:
                realHyp = h
                return realHyp

    def write_report(self, experiment, hyps):
        outstream = open('report.txt', 'w')

        print >> outstream, "Experiment=%s" % experiment
        print >> outstream, "Num_Hyp=%d" % len(hyps)
        for hyp in hyps:
            print >> outstream, "Hyp_Atoms=%s" % ",".join(hyp.atoms)
            if hyp.test_failed:
                print >> outstream, "Hyp_Score=unknown"
                print >> outstream, "Hyp_Plan_Len=unknown"
            else:
                print >> outstream, "Hyp_Score=%f" % hyp.score
                print >> outstream, "Hyp_Plan_Len=%d" % len(hyp.plan)
            print >> outstream, "Hyp_Trans_Time=%f" % hyp.trans_time
            print >> outstream, "Hyp_Plan_Time=%f" % hyp.plan_time
            print >> outstream, "Hyp_Test_Time=%f" % hyp.total_time
            print >> outstream, "Hyp_Is_True=%s" % hyp.is_true

        outstream.close()
        print(max(hyps))

    def run_recognizer(self):
        return None


class LPRecognizerHValue(PlanRecognizer):

    def __init__(self, options):
        PlanRecognizer.__init__(self,options)
        self.name = "h-value"

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
           self.hyps[i].evaluate(i, self.observations)

        # Select unique goal (choose the goal with the smallest count)
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h
                elif h.score == self.unique_goal.score and h.obs_hits > self.unique_goal.obs_hits:
                    self.unique_goal = h

        # Select other goals
        for h in self.hyps:
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal
                if h.score == self.unique_goal.score:
                    self.multi_goal_no_tie_breaking.append(h)
                # Compensate for partial observability (incomplete)
                # missing_obs = h.score - len(self.observations)
                # if h.score = self.unique_goal.score
                
        
class LPRecognizerHValueC(LPRecognizerHValue):

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options)
        self.name = "h-value-c"

    def load_hypotheses(self):
        hyps = []
        instream = open('hyps.dat')

        for line in instream:
            line = line.strip()
            H = Hypothesis(True, False)
            H.atoms = [tok.strip() for tok in line.split(',')]
            H.check_if_actual()
            hyps.append(H)

        instream.close()

        return hyps

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
            self.hyps[i].evaluate(i, self.observations)

        # Select unique goal
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h

        # Select other goals
        for h in self.hyps:
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score == self.unique_goal.score:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal (I know it's the same check as above)
                if h.score == self.unique_goal.score:
                    self.multi_goal_no_tie_breaking.append(h) 


class LPRecognizerSoftC(LPRecognizerHValue):

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options)
        self.name = "soft-c"

    def load_hypotheses(self):
        hyps = []
        instream = open('hyps.dat')

        for line in instream:
            line = line.strip()
            H = Hypothesis(False, True)
            H.atoms = [tok.strip() for tok in line.split(',')]
            H.check_if_actual()
            hyps.append(H)

        instream.close()

        return hyps

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
            self.hyps[i].evaluate(i, self.observations)
        
        # Select unique goal (Goal with the maximum number of hits)
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.obs_hits > self.unique_goal.obs_hits:
                    self.unique_goal  = h
                elif h.obs_hits == self.unique_goal.obs_hits and h.score < self.unique_goal.score:
                    self.unique_goal  = h

        # Select other goals
        for h in self.hyps:
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal
                if h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h)
                

class LPRecognizerDiffHValueC(LPRecognizerHValue):
    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options)
        self.hsoft_recognizer = LPRecognizerSoftC(options)
        self.hvalue_recognizer = LPRecognizerHValue(options)
        self.constraints_recognizer = LPRecognizerHValueC(options)
        self.name = "diff-h-value-c"

    def get_real_hypothesis(self):
        return self.hsoft_recognizer.get_real_hypothesis()

    def run_recognizer(self):
        self.hvalue_recognizer.run_recognizer()
        self.constraints_recognizer.run_recognizer()
        self.hsoft_recognizer.run_recognizer()

        hyp_diff = float("inf")
        i = 0
        # Select unique goal
        for hv, hc, hs in  zip(self.hvalue_recognizer.hyps, self.constraints_recognizer.hyps, self.hsoft_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:  
                hs.score = int((hs.score+hs.obs_hits)/10000)          
                if not self.unique_goal or (hc.score - hs.score) < hyp_diff:
                    self.unique_goal = hs
                    hyp_diff = hc.score - hs.score
                elif hc.score - hs.score == hyp_diff:
                    if hs.obs_hits > self.unique_goal.obs_hits:
                        self.unique_goal = hs    
                #print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, hyp_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))                        
            i = i + 1

        # Select multi goal with tie-breaking
        for hs, hc in  zip(self.hsoft_recognizer.hyps, self.constraints_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:
                if (hc.score - hs.score) == hyp_diff and hs.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(hs) 
            #print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, hyp_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))                        
   

        # Select multi goal
        for hs, hc in  zip(self.hsoft_recognizer.hyps, self.constraints_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:
                if (hc.score - hs.score) == hyp_diff:
                    self.multi_goal_no_tie_breaking.append(hs)    


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
    if options.diff_h_value_c:
        recognizer = LPRecognizerDiffHValueC(options)
        run_recognizer(recognizer)
    if options.soft_c:
        recognizer = LPRecognizerSoftC(options)
        run_recognizer(recognizer)
   
    #cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'

if __name__ == '__main__':
    main()
