#!/usr/bin/env python2.7

from const_plan_recognizer import LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerOverlap, LPRecognizerHValueCUncertainty

class LPRecognizerDeltaHS(LPRecognizerHValue):

    name = "delta-h-s"

    def __init__(self, options, auto_uncertainty=False):
        LPRecognizerHValue.__init__(self,options, auto_uncertainty=auto_uncertainty)
        self.overlap_recognizer = LPRecognizerOverlap(options)
        self.hvalue_recognizer = LPRecognizerHValue(options)

    def get_real_hypothesis(self):
        return self.overlap_recognizer.get_real_hypothesis()

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed and not h2.test_failed:
            # With tie breaking
            # return (h2.score + len(self.hvalue_recognizer.observations) - h.score) <= (self.min_diff * unc) and h2.obs_hits == self.unique_goal.obs_hits
            # Without tie breaking
            return (h2.score + len(self.hvalue_recognizer.observations) - h.score) <= (self.min_diff * unc)
        return False

    def run_recognizer(self):
        self.hvalue_recognizer.run_recognizer()
        self.overlap_recognizer.run_recognizer()

        self.min_diff = float("inf")
        # Select unique goal (formula is delta_soft = h_s + k - h)
        # U = delta_soft * (1+ k / (h_s + k ))
        for i, hv, hs in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.overlap_recognizer.hyps):
            if not hs.test_failed and not hv.test_failed:
                hs.score = int((hs.score+hs.obs_hits)/10000)
                if not self.unique_goal or (hs.score + len(self.hvalue_recognizer.observations) - hv.score) < self.min_diff:
                    self.unique_goal = hs
                    self.min_diff = (hs.score + len(self.hvalue_recognizer.observations) - hv.score)
                elif (hs.score + len(self.hvalue_recognizer.observations) - hv.score) == self.min_diff:
                    if hs.obs_hits > self.unique_goal.obs_hits:
                        self.unique_goal = hs
                # print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))

        if self.auto_uncertainty:
            uncertainty_ratio = (1+ self.unique_goal.score/(self.unique_goal.score + len(self.hvalue_recognizer.observations)))
        else:
            uncertainty_ratio = 1

        # Select multi goal
        for i, hv, hs in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.overlap_recognizer.hyps):
            if self.accept_hypothesis(hv, unc=uncertainty_ratio, h2=hs):
                self.accepted_hypotheses.append(hs)
            # print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, self.min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))


class LPRecognizerDeltaHSUncertainty(LPRecognizerDeltaHS):

    name = "delta-h-s-uncertainty"

    def __init__(self, options):
        LPRecognizerDeltaHS.__init__(self,options,auto_uncertainty=True)

class LPRecognizerDeltaHC(LPRecognizerHValue):

    name = "delta-h-c"

    def __init__(self, options, auto_uncertainty=False):
        LPRecognizerHValue.__init__(self,options, auto_uncertainty=auto_uncertainty)
        self.hvalue_recognizer = LPRecognizerHValue(options)
        self.constraints_recognizer = LPRecognizerHValueC(options)
        self.min_h_c = None

    def get_real_hypothesis(self):
        return self.hvalue_recognizer.get_real_hypothesis()

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed and not h2.test_failed:
            # With tie breaking
            # return (h2.score - h.score) <= (self.min_diff * unc) and h.obs_hits == self.unique_goal.obs_hits
            # Without tie breaking
            return (h2.score - h.score) <= (self.min_diff * unc)
        return False

    def run_recognizer(self):
        self.hvalue_recognizer.run_recognizer()
        self.constraints_recognizer.run_recognizer()

        self.min_diff = float("inf")
        # Select unique goal
        for i, hv, hc in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.constraints_recognizer.hyps):
            if not hv.test_failed and not hc.test_failed:
                if not self.unique_goal or (hc.score - hv.score) < self.min_diff:
                    self.unique_goal = hv
                    self.min_diff = hc.score - hv.score
                elif hc.score - hv.score == self.min_diff:
                    if hv.obs_hits > self.unique_goal.obs_hits:
                        self.unique_goal = hv
                # print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))

        if self.auto_uncertainty:
            # Select lowest h_c
            for h in self.constraints_recognizer.hyps:
                if not h.test_failed:
                    if not self.min_h_c or (h.score < self.min_h_c.score):
                        self.min_h_c = h

            uncertainty = self.min_h_c.score - len(self.observations)
            uncertainty_ratio = (1+uncertainty/self.min_h_c.score)
            # print("u: {0}, u_ratio: {1}, min_h_c: {2}".format(uncertainty, uncertainty_ratio, self.min_h_c.score))
        else:
            uncertainty_ratio = 1
            # print("Not using uncertainty")

        # Select multi goal
        for i, hv, hc in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.constraints_recognizer.hyps):
            if self.accept_hypothesis(hv,unc=uncertainty_ratio,h2=hc):
                self.accepted_hypotheses.append(hv)


class LPRecognizerDeltaHCUncertainty(LPRecognizerDeltaHC):

    name = "delta-h-c-uncertainty"

    def __init__(self, options):
        LPRecognizerDeltaHC.__init__(self, options, auto_uncertainty=True)
