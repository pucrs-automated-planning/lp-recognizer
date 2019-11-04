#!/usr/bin/env python2.7

from plan_recognizer import PlanRecognizer

class LPRecognizerHValue(PlanRecognizer):
    name = "h-value"

    def __init__(self, options, constraints = False, soft_constraints = False, auto_uncertainty = False):
        PlanRecognizer.__init__(self,options,constraints,soft_constraints, auto_uncertainty)

    def accept_hypothesis(self, h, unc=1):
        if not h.test_failed and h.score >= 0 and h.score != 'n/a':
            return h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits
        return False


    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
           self.hyps[i].evaluate(i, self.observations)

        # Select unique goal (choose the goal with the smallest count)
        for h in self.hyps:
            if not h.test_failed and h.score >= 0 and h.score != 'n/a':
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h
                elif h.score == self.unique_goal.score and h.obs_hits > self.unique_goal.obs_hits:
                    self.unique_goal = h

        # Select other goals
        for h in self.hyps:
            if self.accept_hypothesis(h):
                self.accepted_hypotheses.append(h)
