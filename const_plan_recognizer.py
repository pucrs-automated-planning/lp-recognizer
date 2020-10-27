#!/usr/bin/env python2

import math
from h_plan_recognizer import LPRecognizerHValue

class LPRecognizerHValueC(LPRecognizerHValue):
    name = "hvaluec"

    def __init__(self, options):
        # Set to hard constraints.
        # Do not calculate delta.
        LPRecognizerHValue.__init__(self, options, h = False, h_c = True, h_s = False)

    def get_score(self, h):
        return [h.h_c, h.obs_misses]

class LPRecognizerHValueCUncertainty(LPRecognizerHValueC):
    name = "hvaluecu"

    def __init__(self, options):
        LPRecognizerHValueC.__init__(self, options)
        
    def calculate_uncertainty(self):
        if self.unique_goal:
            hyp = self.unique_goal
            uncertainty = (hyp.h_c - self.unique_goal.obs_hits) / hyp.h_c
            self.uncertainty_ratio = 1 + uncertainty
            if uncertainty < 0:
                print("Uncertainty below 1 [hc - obs_hits is negative!]")
                print(self.options.exp_file)
            print("Uncertainty: {}".format(self.uncertainty_ratio))
            

class LPRecognizerSoftC(LPRecognizerHValue):
    name = "softc"

    def __init__(self, options):
        # Set to soft constraints.
        # Do not calculate delta.
        LPRecognizerHValue.__init__(self, options, h = False, h_c = False, h_s = True)

    def get_score(self, h):
        h.h_s = math.floor(h.h_s)
        return [h.obs_misses, h.h_s]

    def accept_hypothesis(self, h):
        if not h.test_failed:
            # Select multi goal with tie-breaking
            return h.h_s <= self.unique_goal.h_s * self.uncertainty_ratio and h.obs_hits == self.unique_goal.obs_hits
            # Select multi goal
            # return h.obs_hits == self.unique_goal.obs_hits
        return False

class LPRecognizerSoftCUncertainty(LPRecognizerSoftC):
    name = "softcu"

    def __init__(self, options):
        LPRecognizerSoftC.__init__(self, options)

    def calculate_uncertainty(self):
        if self.unique_goal:
            hyp = self.unique_goal
            self.uncertainty_ratio = 1 + (hyp.h_s - hyp.obs_count) / hyp.h_s


class LPRecognizerWeightedC(LPRecognizerHValue):
    name = "weightedc"

    def __init__(self, options):
        # Set to soft (weighted) constraints.
        # Calculate delta.
        LPRecognizerHValue.__init__(self, options, h = True, h_c = False, h_s = True)

    def get_score(self, h):
        return [h.h_s, h.h_s + h.h]

    def accept_hypothesis(self, h):
        if not h.test_failed:
            return h.score[0] <= self.unique_goal.score[0] * self.uncertainty_ratio
        return False


class LPRecognizerWeightedCUncertainty(LPRecognizerWeightedC):
    name = "weightedcu"

    def __init__(self, options):
        LPRecognizerWeightedC.__init__(self, options)

    def calculate_uncertainty(self):
        if self.unique_goal:
            delta = self.unique_goal.score[0]
            hc = self.unique_goal.score[1]
            uncertainty = (hc - self.unique_goal.obs_hits) / hc
            self.uncertainty_ratio = 1 + uncertainty
            print("Uncertainty: {}".format(self.uncertainty_ratio))