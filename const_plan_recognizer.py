#!/usr/bin/env python2

from h_plan_recognizer import LPRecognizerHValue

class LPRecognizerHValueC(LPRecognizerHValue):
    name = "h-value-c"

    def __init__(self, options, filter = 0):
        # Set to hard constraints.
        # Do not calculate delta.
        LPRecognizerHValue.__init__(self, options, 2, False, filter)


class LPRecognizerHValueCUncertainty(LPRecognizerHValueC):
    name = "h-value-c-uncertainty"

    def __init__(self, options, filter = 0):
        LPRecognizerHValueC.__init__(self, options, filter)
        
    def calculate_uncertainty(self):
        if self.unique_goal:
            score = self.unique_goal.score
            self.uncertainty_ratio = 1 + (score[0] - self.unique_goal.obs_count) / score[0]
            # self.uncertainty_ratio = self.options.theta * (self.unique_goal.score[0] - self.unique_goal.obs_count)
            

class LPRecognizerSoftC(LPRecognizerHValue):
    name = "soft-c"

    def __init__(self, options, filter = 0):
        # Set to soft constraints.
        # Do not calculate delta.
        LPRecognizerHValue.__init__(self, options, 1, False, filter)

    def accept_hypothesis(self, h):
        if not h.test_failed:
            # Select multi goal with tie-breaking
            return h.score[1] <= self.unique_goal.score[1] * self.uncertainty_ratio and h.obs_hits == self.unique_goal.obs_hits
            # Select multi goal
            # return h.obs_hits == self.unique_goal.obs_hits
        return False


class LPRecognizerSoftCUncertainty(LPRecognizerSoftC):
    name = "soft-c-uncertainty"

    def __init__(self, options, filter = 0):
        LPRecognizerSoftC.__init__(self, options, filter)

    def calculate_uncertainty(self):
        if self.unique_goal:
            self.uncertainty_ratio = self.options.theta * (self.unique_goal.score[1] - self.unique_goal.obs_count)

