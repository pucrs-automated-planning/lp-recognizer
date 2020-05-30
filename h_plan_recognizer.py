#!/usr/bin/env python2.7

from plan_recognizer import PlanRecognizer

class LPRecognizerHValue(PlanRecognizer):
    name = "h-value"

    def __init__(self, options, constraints = 0, delta = False):
        PlanRecognizer.__init__(self, options, constraints, delta)
        self.uncertainty_ratio = 1

    def accept_hypothesis(self, h):
        if not h.test_failed:
            return h.score[0] <= self.unique_goal.score[0] * self.uncertainty_ratio and h.obs_hits == self.unique_goal.obs_hits
        return False

    def verify_hypothesis(self):
        if self.unique_goal:
            for h in self.hyps:
                if self.accept_hypothesis(h):
                    self.accepted_hypotheses.append(h)
        else: 
            for h in self.hyps:
                self.accepted_hypotheses.append(h)
            print("All hypotheses failed.")
            print(self.options.exp_file)

    def calculate_uncertainty(self):
        self.uncertainty_ratio = 1

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
           self.hyps[i].evaluate(i, self.observations)
        # Select unique goal (choose the goal with the smallest count)
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h
        # Select other goals
        self.calculate_uncertainty()
        self.verify_hypothesis()
