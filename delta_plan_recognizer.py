#!/usr/bin/env python2.7

from const_plan_recognizer import LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerHValueCUncertainty

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