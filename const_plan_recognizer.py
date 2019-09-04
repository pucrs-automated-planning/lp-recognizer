#!/usr/bin/env python2

from h_plan_recognizer import LPRecognizerHValue

class LPRecognizerHValueC(LPRecognizerHValue):

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=True, soft_constraints=False)
        self.name = "h-value-c"

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
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score == self.unique_goal.score:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal (I know it's the same check as above)
                if h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h) 


class LPRecognizerHValueCUncertainty(LPRecognizerHValue):
    def __init__(self, options):
        LPRecognizerHValue.__init__(self, options, constraints=True, soft_constraints=False)
        self.name = "h-value-c-uncertainty"

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
            if not h.test_failed:
                # print("H score is %f"%h.score)
                # Select multi goal with tie-breaking
                if h.score <= self.unique_goal.score*uncertainty_ratio:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal (I know it's the same check as above)
                if h.score <= self.unique_goal.score*uncertainty_ratio and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h)     


class LPRecognizerSoftC(LPRecognizerHValue):

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=False, soft_constraints=True)
        self.name = "soft-c"

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
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal
                if h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h)

class LPRecognizerSoftCUncertainty(LPRecognizerHValue):

    def __init__(self, options):
        LPRecognizerHValue.__init__(self,options, constraints=False, soft_constraints=True)
        self.name = "soft-c-uncertainty"

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
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score - uncertainty <= self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal
                if h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_no_tie_breaking.append(h)