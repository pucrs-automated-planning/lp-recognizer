#!/usr/bin/env python3

from plan_recognizer import PlanRecognizer
import time

class LPRecognizerHValue(PlanRecognizer):
    name = "hvalue"

    def __init__(self, options, h = True, h_c = False, h_s = False):
        PlanRecognizer.__init__(self, options, h, h_c, h_s)
        self.uncertainty_ratio = 1

    def accept_hypothesis(self, h):
        if not h.test_failed:
            return h.score[0] <= self.unique_goal.score[0] * self.uncertainty_ratio and h.obs_hits == self.unique_goal.obs_hits
        return False

    def get_score(self, h):
        return [h.h, h.obs_misses]

    def verify_hypotheses(self):
        if self.unique_goal:
            for h in self.hyps:
                if self.accept_hypothesis(h):
                    self.accepted_hypotheses.add(h)
        else: 
            for h in self.hyps:
                self.accepted_hypotheses.add(h)
            print("All hypotheses failed.")
            print(self.options.exp_file)

    def calculate_uncertainty(self):
        self.uncertainty_ratio = 1

    def run_recognizer(self):
        self.total_time = time.time()
        self.fd_time = 0.0
        self.lp_time = 0.0
        for hyp in self.hyps:
            hyp.evaluate(self.observations)
            self.fd_time += hyp.fd_time
            self.lp_time += hyp.lp_time
            if hyp.test_failed:
                print("Score %s %s: Failed" % (hyp.index, ' '.join(hyp.atoms)))
            else:
                hyp.score = self.get_score(hyp)
                print("Score %s %s: %s" % (hyp.index, ' '.join(hyp.atoms), hyp.score))
        # Select unique goal (choose the goal with the smallest score)
        for h in self.hyps:
            if not h.test_failed:
                if not self.unique_goal or h.score < self.unique_goal.score:
                   self.unique_goal = h
        # Select other goals
        self.calculate_uncertainty()
        self.verify_hypotheses()
        self.total_time = time.time() - self.total_time
