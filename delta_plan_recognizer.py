#!/usr/bin/env python2.7

from const_plan_recognizer import LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerHValueCUncertainty

class LPRecognizerDeltaHS(LPRecognizerHValue):

    name = "delta-h-s"

    def __init__(self, options, auto_uncertainty=False):
        LPRecognizerHValue.__init__(self,options, auto_uncertainty=auto_uncertainty)
        self.hsoft_recognizer = LPRecognizerSoftC(options)
        self.hvalue_recognizer = LPRecognizerHValue(options)

    def get_real_hypothesis(self):
        return self.hsoft_recognizer.get_real_hypothesis()

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed and not h2.test_failed:
            # With tie breaking
            # return (h2.score + len(self.hvalue_recognizer.observations) - h.score) <= (self.min_diff * unc) and h2.obs_hits == self.unique_goal.obs_hits
            # Without tie breaking
            return (h2.score + len(self.hvalue_recognizer.observations) - h.score) <= (self.min_diff * unc)
        return False

    def run_recognizer(self):
        self.hvalue_recognizer.run_recognizer()
        self.hsoft_recognizer.run_recognizer()


        obs = self.hvalue_recognizer.observations
        self.min_diff = float("inf")
        # Select unique goal (formula is delta_soft = h_s + k - h)
        # U = delta_soft * (1+ k / (h_s + k ))
        for i, hv, hs in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.hsoft_recognizer.hyps):
            if not hs.test_failed and not hv.test_failed:
                hs.score = int((hs.score+hs.obs_hits)/10000)
                diff = hs.score + len(obs) - hv.score
                print(hv.score, hs.score, hs.obs_hits, len(obs))
                if not self.unique_goal or diff < self.min_diff:
                    self.unique_goal = hs
                    self.min_diff = diff
                elif diff == self.min_diff:
                    if hs.obs_hits > self.unique_goal.obs_hits:
                        self.unique_goal = hs
                # print('{0} - c: {1}, h: {2}, s: {3}, diff-current: {4}, obs-current: {7}, obs-hits-by-h: {5}, obs-hits-by-h: {6}'.format(i, hc.score, hv.score, hs.score, min_diff, hv.obs_hits, hs.obs_hits, self.unique_goal.obs_hits))

        if self.auto_uncertainty:
            if not self.unique_goal:
                uncertainty_ratio = 1
            else:
                uncertainty_ratio = (1+ self.unique_goal.score/(self.unique_goal.score + len(obs)))
        else:
            uncertainty_ratio = 1

        # Select multi goal
        for i, hv, hs in  zip(range(len(self.hvalue_recognizer.hyps)), self.hvalue_recognizer.hyps, self.hsoft_recognizer.hyps):
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
        self.delta_recognizer = LPRecognizerHValueC(options, delta=True)

    def get_real_hypothesis(self):
        return self.delta_recognizer.get_real_hypothesis()

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed:
            # With tie breaking
            # return (h.score[0]) <= (self.min_diff * unc) and h.obs_hits == self.delta_recognizer.unique_goal.obs_hits
            # Without tie breaking
            return h.score[0] <= (self.min_diff * unc)
        return False

    def run_recognizer(self):
        self.delta_recognizer.run_recognizer()
        unique_goal = self.delta_recognizer.unique_goal
        if unique_goal:
            self.min_diff = unique_goal.score[0]
            hc = unique_goal.score[1]
            hv = unique_goal.score[1] - unique_goal.score[0] # score[0] = hc - hv 
            print("Delta: {} | HV: {} | HC: {} | #Obs: {}".format(self.min_diff, hv, hc, unique_goal.obs_hits))
            if self.auto_uncertainty:
                uncertainty = (hc - unique_goal.obs_hits) / hc
                uncertainty_ratio = 1 + uncertainty
                if uncertainty_ratio < 1:
                    print("Uncertainty below 1 [hc - len(obs) is negative!]")
                    print(self.options.exp_file)
            else:
                uncertainty_ratio = 1
            # Select multi goal
            print("Undercainty: %d" % uncertainty_ratio)
            for h in self.delta_recognizer.hyps:
                if self.accept_hypothesis(h,unc=uncertainty_ratio):
                    self.accepted_hypotheses.append(h)
        else:
            for h in self.delta_recognizer.hyps:
                self.accepted_hypotheses.append(h)
            print("All hypotheses failed.")
            print(self.options.exp_file)


class LPRecognizerDeltaHCUncertainty(LPRecognizerDeltaHC):

    name = "delta-h-c-uncertainty"

    def __init__(self, options):
        LPRecognizerDeltaHC.__init__(self, options, auto_uncertainty=True)
