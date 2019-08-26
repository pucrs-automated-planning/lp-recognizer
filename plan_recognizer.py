#!/usr/bin/env python2.7

from planner_interface import Observations, PRCommand, Hypothesis

class PlanRecognizer:
    
    def __init__(self, options, constraints = False, soft_constraints = False):
        self.options = options
        self.observations = Observations('obs.dat')
        self.constraints = constraints
        self.soft_constraints = soft_constraints
        self.hyps = self.load_hypotheses()
        self.unique_goal = None
        self.multi_goal_tie_breaking = []
        self.multi_goal_no_tie_breaking = []
        self.multi_goal_missing_compensation = [] # 
        self.name = None

    def load_hypotheses(self):
        hyps = []
        instream = open('hyps.dat')

        for line in instream:
            line = line.strip()
            H = Hypothesis(self.constraints,self.soft_constraints)
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