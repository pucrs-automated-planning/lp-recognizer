#!/usr/bin/env python2

from h_plan_recognizer import LPRecognizerHValue

class LPRecognizerHValueC(LPRecognizerHValue):
    name = "h-value-c"

    def __init__(self, options):
        # Set to hard constraints.
        # Do not calculate delta.
        LPRecognizerHValue.__init__(self, options, 2, False)


class LPRecognizerHValueCUncertainty(LPRecognizerHValueC):
    name = "h-value-c-uncertainty"

    def __init__(self, options):
        LPRecognizerHValueC.__init__(self, options)
        
    def calculate_uncertainty(self):
        if self.unique_goal:
            score = self.unique_goal.score
            self.uncertainty_ratio = 1 + (score[0] - self.unique_goal.obs_count) / score[0]
            # self.uncertainty_ratio = self.options.theta * (self.unique_goal.score[0] - self.unique_goal.obs_count)
            

class LPRecognizerSoftC(LPRecognizerHValue):
    name = "soft-c"

    def __init__(self, options):
        # Set to soft constraints.
        # Do not calculate delta.
        LPRecognizerHValue.__init__(self, options, 1, False)

    def accept_hypothesis(self, h):
        if not h.test_failed:
            # Select multi goal with tie-breaking
            return h.score[1] <= self.unique_goal.score[1] * self.uncertainty_ratio and h.obs_hits == self.unique_goal.obs_hits
            # Select multi goal
            # return h.obs_hits == self.unique_goal.obs_hits
        return False


class LPRecognizerSoftCUncertainty(LPRecognizerSoftC):
    name = "soft-c-uncertainty"

    def __init__(self, options):
        LPRecognizerSoftC.__init__(self, options)

    def calculate_uncertainty(self):
        if self.unique_goal:
            self.uncertainty_ratio = self.options.theta * (self.unique_goal.score[1] - self.unique_goal.obs_count)


class LPRecognizerWeightedC(LPRecognizerHValue):
    name = "weighted-c"

    def __init__(self, options):
        # Set to soft (weighted) constraints.
        # Do not calculate delta.
        LPRecognizerHValue.__init__(self, options, 3, False)

    def accept_hypothesis(self, h):
        if not h.test_failed:
            return h.score[0] <= self.unique_goal.score[1] * self.uncertainty_ratio
        return False


class LPRecognizerWeightedCUncertainty(LPRecognizerWeightedC):
    name = "weighted-c-uncertainty"

    def __init__(self, options):
        LPRecognizerSoftC.__init__(self, options)

    def calculate_uncertainty(self):
        if self.unique_goal:
            self.uncertainty_ratio = self.options.theta * (self.unique_goal.score[1] - self.unique_goal.obs_count)
