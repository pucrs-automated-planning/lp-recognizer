#!/usr/bin/env python3

from const_plan_recognizer import LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerHValueCUncertainty

class LPRecognizerDeltaHC(LPRecognizerHValue):
    name = "delta"

    def __init__(self, options):
        # Set to hard constraints.
        # Calculate delta.
        LPRecognizerHValue.__init__(self, options, h = True, h_c = True, h_s = False)

    def get_score(self, h):
        if h.h_c < h.h or h.h_c == 0:
            h.test_failed = True
        return [h.h_c - h.h, h.h_c, h.obs_misses]

    def accept_hypothesis(self, h):
        if not h.test_failed:
            # With tie breaking
            # return (h.score[0]) <= (self.unique_goal.score[0] * unc) and h.obs_hits == self.unique_goal.obs_hits
            # Without tie breaking
            return h.score[0] <= (self.unique_goal.score[0] * self.uncertainty_ratio)
        return False


class LPRecognizerDeltaHCUncertainty(LPRecognizerDeltaHC):
    name = "deltau"

    def __init__(self, options):
        LPRecognizerDeltaHC.__init__(self, options)

    def calculate_uncertainty(self):
        if self.unique_goal:
            delta = self.unique_goal.score[0]
            hc = self.unique_goal.h_c
            hv = self.unique_goal.h
            uncertainty = (hc - self.unique_goal.obs_hits) / hc
            self.uncertainty_ratio = 1 + uncertainty
            if uncertainty < 0:
                print("Uncertainty below 1 [hc - obs_hits is negative!]")
                print(self.options.exp_file)
            print("Uncertainty: {}".format(self.uncertainty_ratio))


class LPRecognizerDeltaHCUncertaintyMax(LPRecognizerDeltaHCUncertainty):
    name = "deltaum"

    def __init__(self, options):
        LPRecognizerDeltaHCUncertainty.__init__(self, options)

    def get_score(self, h):
        if h.h_c < h.h or h.h_c == 0:
            h.test_failed = True
        return [h.h_c - h.h, -h.h_c, h.obs_misses]

class LPRecognizerWeightedDeltaHC(LPRecognizerDeltaHC):
    name = "deltaw"

    def __init__(self, options):
        # Set to hard constraints.
        # Calculate delta.
        LPRecognizerDeltaHC.__init__(self, options)

    def accept_hypothesis(self, h):
        if h.test_failed:
            return False
        if h.last_obs < self.last_obs / self.uncertainty_ratio:
            return False
        return h.score[0] <= (self.unique_goal.score[0] * self.uncertainty_ratio)

    def calculate_uncertainty(self):
        self.last_obs = -1
        if self.unique_goal:
            for h in self.hyps:
                if not h.test_failed and (h.last_obs > self.last_obs):
                    self.last_obs = h.last_obs

class LPRecognizerWeightedDeltaHUncertainty(LPRecognizerDeltaHCUncertainty, LPRecognizerWeightedDeltaHC):
    name = "deltawu"

    def __init__(self, options):
        LPRecognizerWeightedDeltaHC.__init__(self, options)

    def accept_hypothesis(self, h):
        return LPRecognizerWeightedDeltaHC.accept_hypothesis(self, h)

    def calculate_uncertainty(self):
        LPRecognizerWeightedDeltaHC.calculate_uncertainty(self)
        LPRecognizerDeltaHCUncertainty.calculate_uncertainty(self)