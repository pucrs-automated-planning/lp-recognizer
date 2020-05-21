#!/usr/bin/env python2.7

from const_plan_recognizer import LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerHValueCUncertainty

class LPRecognizerDeltaHC(LPRecognizerHValue):
    name = "delta-h-c"

    def __init__(self, options, filter = 0):
        # Set to hard constraints.
        # Calculate delta.
        LPRecognizerHValue.__init__(self, options, 2, True, filter)

    def accept_hypothesis(self, h):
        if not h.test_failed:
            # With tie breaking
            # return (h.score[0]) <= (self.unique_goal.score[0] * unc) and h.obs_hits == self.unique_goal.obs_hits
            # Without tie breaking
            return h.score[0] <= (self.unique_goal.score[0] * self.uncertainty_ratio)
        return False


class LPRecognizerDeltaHCUncertainty(LPRecognizerDeltaHC):
    name = "delta-h-c-uncertainty"

    def __init__(self, options, filter = 0):
        LPRecognizerDeltaHC.__init__(self, options, filter)

    def calculate_uncertainty(self):
        if self.unique_goal:
            delta = self.unique_goal.score[0]
            hc = self.unique_goal.score[1]
            hv = hc - delta # score[0] = hc - hv 
            print("Delta: {} | HV: {} | HC: {} | #Obs: {}".format(delta, hv, hc, self.unique_goal.obs_hits))
            uncertainty = (hc - self.unique_goal.obs_hits) / hc
            self.uncertainty_ratio = 1 + uncertainty
            if uncertainty < 0:
                print("Uncertainty below 1 [hc - obs_hits is negative!]")
                print(self.options.exp_file)
            print("Uncertainty: {}".format(self.uncertainty_ratio))
            
            
class LPRecognizerDeltaHS(LPRecognizerHValue):
    name = "delta-h-s"

    def __init__(self, options, filter = 0):
        # Set to soft constraints.
        # Calculate delta.  
        LPRecognizerHValue.__init__(self, options, 1, True, filter)

    def accept_hypothesis(self, h):
        if not h.test_failed:
            # With tie breaking
            # return (h2.score + len(self.hvalue_recognizer.observations) - h.score) <= (self.min_diff * unc) and h2.obs_hits == self.unique_goal.obs_hits
            # Without tie breaking
            return h.score[0] <= (self.unique_goal.score[0] * self.uncertainty_ratio)
        return False


class LPRecognizerDeltaHSUncertainty(LPRecognizerDeltaHS):
    name = "delta-h-s-uncertainty"

    def __init__(self, options, filter = 0):
        LPRecognizerDeltaHS.__init__(self, options, filter)
        
    def calculate_uncertainty(self):
        if self.unique_goal:
            uncertainty_ratio = 1 + self.unique_goal.score[2] / (self.unique_goal.score[2] + len(obs))
            
            