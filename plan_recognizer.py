#!/usr/bin/env python2.7

from planner_interface import Hypothesis
import re

class PlanRecognizer:
    name = None

    def __init__(self, options, h, h_c, h_s):
        self.options = options
        self.observations = self.load_observations('obs.dat')
        self.hyps = self.load_hypotheses([options.hyp_max_time, options.max_memory, options.heuristics, \
            str(h).lower(), str(h_c).lower(), str(h_s).lower(), \
            options.weight, options.filter, options.h_obs, options.solver, options.mip])
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
        # Read true hyp
        real_hyp = None
        instream = open('real_hyp.dat')
        for line in instream:
            real_hyp = frozenset([tok.strip().lower() for tok in line.split(',')])
            break
        instream.close()
        # Read correct solution
        solution = set()
        instream = open('solution.dat')
        for line in instream:
            atoms = frozenset([tok.strip().lower() for tok in re.findall("\(.*?\)", line)])
            solution.add(atoms)
        instream.close()
        # Read all hyps
        hyps = []
        instream = open('hyps.dat')
        for line in instream:
            atoms = frozenset([tok.strip().lower() for tok in line.split(',')])
            h = Hypothesis(opts, atoms)
            h.is_true = atoms == real_hyp
            h.is_solution = atoms in solution
            hyps.append(h)
        instream.close()
        print("Hypothesis: %s" % hyps)
        print("Real hypothesis: %s" % real_hyp)
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
