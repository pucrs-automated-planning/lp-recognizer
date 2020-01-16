#!/usr/bin/env python2

from h_plan_recognizer import LPRecognizerHValue

class LPRecognizerHValueC(LPRecognizerHValue):

    name = "h-value-c"

    def __init__(self, options, auto_uncertainty = False):
        LPRecognizerHValue.__init__(self,options, constraints=True, soft_constraints=False, auto_uncertainty = auto_uncertainty)

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed:
            # return h.score == self.unique_goal.score
            # return h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits
            return h.score <= self.unique_goal.score*unc
        return False

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
            self.hyps[i].evaluate(i, self.observations)

        # Select unique goal
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h

        if self.auto_uncertainty:
            # Compute presumed uncertainty (score is the operator count)
            # print(self.options.theta)
            # uncertainty = self.options.theta*(self.unique_goal.score - len(self.observations))
            if not self.unique_goal:
                uncertainty = 0
                uncertainty_ratio = 1
            else:
                uncertainty = (self.unique_goal.score - len(self.observations))
                uncertainty_ratio = (1+uncertainty/self.unique_goal.score)
                # print("Minimum score is %f, observation length is %f, theta is %f, theta param was %f "%(self.unique_goal.score, len(self.observations), theta, self.options.theta))
        else:
            uncertainty_ratio = 1

        # Select other goals
        for h in self.hyps:
            if self.accept_hypothesis(h, unc=uncertainty_ratio):
                self.accepted_hypotheses.append(h)


class LPRecognizerHValueCUncertainty(LPRecognizerHValueC):

    name = "h-value-c-uncertainty"

    def __init__(self, options):
        LPRecognizerHValueC.__init__(self, options, auto_uncertainty = True)

class LPRecognizerSoftC(LPRecognizerHValue):

    name = "soft-c"

    def __init__(self, options, auto_uncertainty = False):
        LPRecognizerHValue.__init__(self,options, constraints=False, soft_constraints=True, auto_uncertainty = auto_uncertainty)

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed:
            # Select multi goal with tie-breaking
            return h.score <= self.unique_goal.score*unc and h.obs_hits == self.unique_goal.obs_hits
            # Select multi goal
            # return h.obs_hits == self.unique_goal.obs_hits
        return False

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

        if self.auto_uncertainty:
            # Compute presumed uncertainty (score is the operator count)
            # print(self.options.theta)
            if not self.unique_goal:
                uncertainty_ratio = 1
            else:
                uncertainty_ratio = self.options.theta*(self.unique_goal.score - len(self.observations))
        else:
            uncertainty_ratio = 1


        # Select other goals
        for h in self.hyps:
            if self.accept_hypothesis(h, unc=uncertainty_ratio):
                self.accepted_hypotheses.append(h)


class LPRecognizerSoftCUncertainty(LPRecognizerSoftC):
    name = "soft-c-uncertainty"

    def __init__(self, options):
        LPRecognizerSoftC.__init__(self,options, constraints=False, soft_constraints=True, auto_uncertainty = True)
