#!/usr/bin/env python2.7

from planner_interface import Hypothesis

class PlanRecognizer:
    name = None

    def __init__(self, options, h, h_c, h_s):
        self.options = options
        self.observations = self.load_observations('obs.dat')
        self.hyps = self.load_hypotheses([options.hyp_max_time, options.max_memory, options.heuristics, \
            str(h).lower(), str(h_c).lower(), str(h_s).lower(), \
            options.weight, options.filter, options.h_obs, options.solver])
        self.unique_goal = None
        self.accepted_hypotheses = set()

    def load_observations(self, file):
        observations = []
        instream = open(file)
        for line in instream:
            observations.append(line.strip().lower())
        print("Observations: %s" % observations)
        return observations

    def load_hypotheses(self, opts):
        hyps = []
        instream = open('hyps.dat')
        for line in instream:
            line = line.strip()
            atoms = [tok.strip().lower() for tok in line.split(',')]
            H = Hypothesis(opts, atoms)
            H.check_if_actual()
            hyps.append(H)
        print("Hypothesis: %s" % hyps)
        print("Real hypothesis: %s" % [hyp for hyp in hyps if hyp.is_solution])
        instream.close()
        return hyps

    def get_real_hypothesis(self):
        for h in self.hyps:
            if h.is_true:
                return h

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
        raise NotImplementedError("You need to implement your method to run the recognizer")

    def accept_hypothesis(self, h):
        raise NotImplementedError("You need to implement your method to run the recognizer")
