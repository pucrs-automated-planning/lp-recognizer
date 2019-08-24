#!/usr/bin/env python2

# Code originally developed by Miquel Ramirez
import sys, os, csv, time, math
from options import Program_Options
from operator import attrgetter

from planner_interface import Observations, PRCommand, Hypothesis

class PlanRecognizer:
    
    def __init__(self, options, constraints = False, soft_constraints = False):
        self.options = options
        self.observations = Observations('obs.dat')
        self.constraints = constraints
        self.soft_constraints = soft_constraints
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
            H = Hypothesis(self.constraints,self.soft_constraints)
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
        # return None
        raise NotImplementedError("You need to implement your method to run the recognizer")


class LPRecognizerHValue(PlanRecognizer):

    def __init__(self, options, constraints = False, soft_constraints = False):
        PlanRecognizer.__init__(self,options,constraints,soft_constraints)
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
        LPRecognizerHValue.__init__(self,options, constraints=True, soft_constraints=False)
        self.name = "h-value-c"

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
                if h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h) 


class LPRecognizerHValueCUncertainty(LPRecognizerHValue):
    def __init__(self, options):
        LPRecognizerHValue.__init__(self, options, constraints=True, soft_constraints=False)
        self.name = "h-value-c-uncertainty"

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
            self.hyps[i].evaluate(i, self.observations)

        # Select unique goal
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h

        # Compute presumed uncertainty (score is the operator count)
        # print(self.options.theta)
        uncertainty = self.options.theta*(self.unique_goal.score - len(self.observations))
        # print("Minimum score is %f, observation length is %f, theta is %f, theta param was %f "%(self.unique_goal.score, len(self.observations), theta, self.options.theta))

        # Select other goals
        for h in self.hyps:
            if not h.test_failed:
                # print("H score is %f"%h.score)
                # Select multi goal with tie-breaking
                if h.score - uncertainty <= self.unique_goal.score:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal (I know it's the same check as above)
                if h.score - uncertainty <= self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h)     


class LPRecognizerSoftC(LPRecognizerHValue):

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=False, soft_constraints=True)
        self.name = "soft-c"

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

class LPRecognizerSoftCUncertainty(LPRecognizerHValue):

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=False, soft_constraints=True)
        self.name = "soft-c-uncertainty"

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

        # Compute presumed uncertainty (score is the operator count)
        # print(self.options.theta)
        uncertainty = self.options.theta*(self.unique_goal.score - len(self.observations))

        # Select other goals
        for h in self.hyps:
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score - uncertainty <= self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal
                if h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h)

class LPRecognizerDeltaHC(LPRecognizerHValue):
    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options)
        self.hsoft_recognizer = LPRecognizerSoftC(options)
        self.hvalue_recognizer = LPRecognizerHValue(options)
        self.constraints_recognizer = LPRecognizerHValueC(options)
        self.name = "delta-h-c"

    def get_real_hypothesis(self):
        return self.hsoft_recognizer.get_real_hypothesis()

    def run_recognizer(self):
        self.hvalue_recognizer.run_recognizer()
        self.constraints_recognizer.run_recognizer()
        self.hsoft_recognizer.run_recognizer()

        min_diff = float("inf")
        # Select unique goal
        for i, hv, hc, hs in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.constraints_recognizer.hyps, self.hsoft_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:  
                hs.score = int((hs.score+hs.obs_hits)/10000)
                if not self.unique_goal or (hc.score - hs.score) < min_diff:
                    self.unique_goal = hs
                    min_diff = hc.score - hs.score
                elif hc.score - hs.score == min_diff:
                    if hs.obs_hits > self.unique_goal.obs_hits:
                        self.unique_goal = hs    
                # print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))                        

        # Select multi goal with tie-breaking
        for i, hs, hc in  zip(range(len(self.hvalue_recognizer.hyps)), self.hsoft_recognizer.hyps, self.constraints_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:
                if (hc.score - hs.score) == min_diff and hs.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(hs) 
            # print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))                        
   

        # Select multi goal
        for hs, hc in  zip(self.hsoft_recognizer.hyps, self.constraints_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:
                if (hc.score - hs.score) == min_diff:
                    self.multi_goal_no_tie_breaking.append(hs) 


class LPRecognizerDeltaHCUncertainty(LPRecognizerHValue):
    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options)
        self.hsoft_recognizer = LPRecognizerSoftC(options)
        self.hvalue_recognizer = LPRecognizerHValue(options)
        self.constraints_recognizer = LPRecognizerHValueC(options)
        self.name = "delta-h-c-uncertainty"
        self.min_h_c = None

    def get_real_hypothesis(self):
        return self.hsoft_recognizer.get_real_hypothesis()

    def run_recognizer(self):
        self.hvalue_recognizer.run_recognizer()
        self.constraints_recognizer.run_recognizer()
        self.hsoft_recognizer.run_recognizer()

        min_diff = float("inf")
        # Select unique goal
        for i, hv, hc, hs in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.constraints_recognizer.hyps, self.hsoft_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:  
                hs.score = int((hs.score+hs.obs_hits)/10000)          
                if not self.unique_goal or (hc.score - hs.score) < min_diff:
                    self.unique_goal = hs
                    min_diff = hc.score - hs.score
                elif hc.score - hs.score == min_diff:
                    if hs.obs_hits > self.unique_goal.obs_hits:
                        self.unique_goal = hs    
                print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))                        

        # Select lowest h_c
        for h in self.constraints_recognizer.hyps:
            if not h.test_failed:
                if not self.min_h_c or h.score < self.min_h_c:
                   self.min_h_c = h
        
        uncertainty = self.min_h_c.score - len(self.observations)
        uncertainty_ratio = (1+uncertainty/self.min_h_c.score)
        print("u: {0}, u_ratio: {1}, min_h_c: {2}".format(uncertainty, uncertainty_ratio, self.min_h_c.score))

        # Select multi goal with tie-breaking
        for i, hs, hc in  zip(range(len(self.hvalue_recognizer.hyps)), self.hsoft_recognizer.hyps, self.constraints_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:
                # if (hc.score - hs.score) <= min_diff + uncertainty and hs.obs_hits == self.unique_goal.obs_hits:
                if (hc.score - hs.score) <= (min_diff * uncertainty_ratio) and hs.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(hs) 
            print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))                        
   

        # Select multi goal
        for i, hs, hc in  zip(range(len(self.hvalue_recognizer.hyps)), self.hsoft_recognizer.hyps, self.constraints_recognizer.hyps):
            if not hs.test_failed and not hc.test_failed:
                # if (hc.score - hs.score) <= min_diff + uncertainty:
                if (hc.score - hs.score) <= (min_diff * uncertainty_ratio):
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
    if options.delta_h_c:
        recognizer = LPRecognizerDeltaHC(options)
        run_recognizer(recognizer)
    if options.soft_c:
        recognizer = LPRecognizerSoftC(options)
        run_recognizer(recognizer)
    if options.h_value_c_uncertainty:
        recognizer = LPRecognizerHValueCUncertainty(options)
        run_recognizer(recognizer)
    if options.delta_h_c_uncertainty:
        recognizer = LPRecognizerDeltaHCUncertainty(options)
        run_recognizer(recognizer)

if __name__ == '__main__':
    main()
