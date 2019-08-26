#!/usr/bin/env python2.7

from plan_recognizer import PlanRecognizer

class LPRecognizerHValue(PlanRecognizer):

    def __init__(self, options, constraints = False, soft_constraints = False):
        PlanRecognizer.__init__(self,options,constraints,soft_constraints)
        self.name = "h-value"

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
           self.hyps[i].evaluate(i, self.observations)

        # Select unique goal (choose the goal with the smallest count)
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h
                elif h.score == self.unique_goal.score and h.obs_hits > self.unique_goal.obs_hits:
                    self.unique_goal = h

        # Select other goals
        for h in self.hyps:
            if not h.test_failed:
                # Select multi goal with tie-breaking
                if h.score == self.unique_goal.score and h.obs_hits == self.unique_goal.obs_hits:
                    self.multi_goal_tie_breaking.append(h)
                # Select multi goal
                if h.score == self.unique_goal.score:
                    self.multi_goal_no_tie_breaking.append(h)
                # Compensate for partial observability (incomplete)
                # missing_obs = h.score - len(self.observations)
                # if h.score = self.unique_goal.score