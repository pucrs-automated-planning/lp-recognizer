#!/usr/bin/env python2.7

from planner_interface import Hypothesis

class PlanRecognizer:
    name = None

    def __init__(self, options, constraints = 0, delta = False):
        self.options = options
        self.observations = self.load_observations('obs.dat')
        self.hyps = self.load_hypotheses([options.hyp_max_time, options.max_memory, options.heuristics, \
            constraints, str(delta).lower(), options.filter])
        self.unique_goal = None
        self.accepted_hypotheses = []

    def load_observations(self, file):
        observations = []
        instream = open(file)
        for line in instream:
            observations.append(line.strip().lower())
        return observations

    def load_hypotheses(self, opts):
        hyps = []
        instream = open('hyps.dat')
        for line in instream:
            line = line.strip()
            H = Hypothesis(opts)
            H.atoms = [tok.strip() for tok in line.split(',')]
            H.check_if_actual()
            hyps.append(H)
        instream.close()
        return hyps

    def get_real_hypothesis(self):
        for h in self.hyps:
            if h.is_true:
                realHyp = h
                return realHyp

    def write_report(self, experiment, hyps):
        outstream = open('report.txt', 'w')
        # Convert this to Python 3
        # print(s,end="", file=outstream)
        print >> outstream, "Experiment=%s" % experiment
        print >> outstream, "Num_Hyp=%d" % len(hyps)
        for hyp in hyps:
            print >> outstream, "Hyp_Atoms=%s" % ",".join(hyp.atoms)
            if hyp.test_failed:
                print >> outstream, "Hyp_Score=unknown"
                print >> outstream, "Hyp_Plan_Len=unknown"
            else:
                print >> outstream, "Hyp_Score=%f" % hyp.score
                print >> outstream, "Hyp_Plan_Len=%d" % len(hyp.plan)
            print >> outstream, "Hyp_Trans_Time=%f" % hyp.trans_time
            print >> outstream, "Hyp_Plan_Time=%f" % hyp.plan_time
            print >> outstream, "Hyp_Test_Time=%f" % hyp.total_time
            print >> outstream, "Hyp_Is_True=%s" % hyp.is_true
        outstream.close()
        print(max(hyps))

    def run_recognizer(self):
        # return None
        raise NotImplementedError("You need to implement your method to run the recognizer")

    def accept_hypothesis(self, h):
        """ Tests whether or not to accept hypothesis h as a likely one, under an unc uncertainty in the range [1,2]"""
        # TODO I still need to refactor this function to something more elegant in terms of how we access it
        # return None
        raise NotImplementedError("You need to implement your method to run the recognizer")
