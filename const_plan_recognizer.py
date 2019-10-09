#!/usr/bin/env python2

from h_plan_recognizer import LPRecognizerHValue

class LPRecognizerHValueC(LPRecognizerHValue):

    name = "h-value-c"

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=True, soft_constraints=False)

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed:
            return h.score == self.unique_goal.score
            # return h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits
        return False

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
            if self.accept_hypothesis(h):
                self.accepted_hypotheses.append(h)


class LPRecognizerHValueCUncertainty(LPRecognizerHValue):
    
    name = "h-value-c-uncertainty"

    def __init__(self, options):
        LPRecognizerHValue.__init__(self, options, constraints=True, soft_constraints=False)

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed:
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

        # Compute presumed uncertainty (score is the operator count)
        # print(self.options.theta)
        # uncertainty = self.options.theta*(self.unique_goal.score - len(self.observations))
        uncertainty = (self.unique_goal.score - len(self.observations))
        uncertainty_ratio = (1+uncertainty/self.unique_goal.score)
        # print("Minimum score is %f, observation length is %f, theta is %f, theta param was %f "%(self.unique_goal.score, len(self.observations), theta, self.options.theta))

        # Select other goals
        for h in self.hyps:
            if self.accept_hypothesis(h, unc=uncertainty_ratio):
                self.accepted_hypotheses.append(h)


class LPRecognizerSoftC(LPRecognizerHValue):

    name = "soft-c"

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=False, soft_constraints=True)

    def accept_hypothesis(self, h, unc = 1, h2 = None):
        if not h.test_failed:
            # Select multi goal with tie-breaking
            return h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits
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

        # Select other goals
        for h in self.hyps:
            if self.accept_hypothesis(h):
                self.accepted_hypotheses.append(h)
                

class LPRecognizerSoftCUncertainty(LPRecognizerHValue):
    name = "soft-c-uncertainty"

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=False, soft_constraints=True)

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

        # Compute presumed uncertainty (score is the operator count)
        # print(self.options.theta)
        uncertainty = self.options.theta*(self.unique_goal.score - len(self.observations))

        # Select other goals
        for h in self.hyps:
            if self.accept_hypothesis(h, unc=uncertainty):
                self.accepted_hypotheses.append(h, unc=uncertainty)