#!/usr/bin/env python3

import unittest, os

from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory
from const_plan_recognizer import *
from delta_plan_recognizer import *

class TestPlanRecognizer(unittest.TestCase):
    SOLVER = "cplex"

    def setUp(self):
        options = Program_Options(["-e", "experiments/example/example.tar.bz2", "-S", TestPlanRecognizer.SOLVER])
        self.factory = PlanRecognizerFactory(options)

    def test_factory(self):
        recognizer = self.factory.get_recognizer("hvalue")
        self.assertEqual(recognizer.__class__, LPRecognizerHValue)
        recognizer = self.factory.get_recognizer("hvaluec")
        self.assertEqual(recognizer.__class__, LPRecognizerHValueC)
        recognizer = self.factory.get_recognizer("delta")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        recognizer = self.factory.get_recognizer("delta-f2")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        self.assertEqual(recognizer.options.filter, 2)
        recognizer = self.factory.get_recognizer("deltau")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHCUncertainty)
        recognizer = self.factory.get_recognizer("deltau-f2")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHCUncertainty)
        self.assertEqual(recognizer.options.filter, 2)
        recognizer = self.factory.get_recognizer("delta-o")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        self.assertTrue(recognizer.options.h_obs)
        recognizer = self.factory.get_recognizer("delta-cp")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        self.assertEqual(recognizer.options.heuristics[0], "pho_constraints()")
        recognizer = self.factory.get_recognizer("delta-clpdf1")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        self.assertEqual(len(recognizer.options.heuristics), 4)

    def test_h_flow(self):
        print("\nTesting hvalue with flow")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "flow_constraints(systematic(2))", "-S", TestPlanRecognizer.SOLVER]
        #args[1] = "experiments/small-sokoban-optimal/100/sokoban_p01_hyp-1_full.tar.bz2" # obs_count = C*
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("hvalue", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")

    def test_h_flow_obs(self):
        print("\nTesting delta with flow")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "flow_constraints(systematic(2))", "-S", TestPlanRecognizer.SOLVER]
        #args[1] = "experiments/small-sokoban-optimal/100/sokoban_p01_hyp-1_full.tar.bz2" # obs_count = C*
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")

    def test_h_lmcut(self):
        print("\nTesting hvalue with lmcut")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "lmcut_constraints()", "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("hvalue", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")

    def test_h_lmcut_obs(self):
        print("\nTesting delta with lmcut")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "lmcut_constraints()", "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")

    def test_h_lmcut_obs2(self):
        print("\nTesting delta modified with lmcut")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "lmcut_constraints()", '-o', "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")

    def test_h_relaxation(self):
        print("\nTesting delta with delete relaxation")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "delete_relaxation_constraints()", "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")

    def test_h_relaxation_obs(self):
        print("\nTesting delta modified with delete relaxation")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "delete_relaxation_constraints()", '-o', "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")

    def test_r_hvalue(self):
        print("\nTesting hvalue")
        args = ["-e", "experiments/small-sokoban-optimal/100/sokoban_p01_hyp-1_full.tar.bz2", "-S", TestPlanRecognizer.SOLVER] # obs_count = C*
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("hvalue", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses)
        for hyp in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(hyp.num_obs, hyp.h)
            self.assertGreaterEqual(hyp.num_obs, hyp.obs_hits)

    def test_r_delta(self):
        print("\nTesting delta")
        args = ["-e", "experiments/small-sokoban-optimal/10/sokoban_p01_hyp-1_10_1.tar.bz2", "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses)
        for h in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(h.score[0], 0)

    def test_r_deltau(self):
        print("\nTesting deltau")
        args = ["-e", "experiments/small-sokoban-optimal/10/sokoban_p01_hyp-1_10_1.tar.bz2", "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("deltau", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses)
        for h in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(h.score[0], 0)
        self.assertGreater(recognizer.uncertainty_ratio, 1)

    def test_r_delta_filter(self):
        print("\nTesting delta with filter")
        args = ["-e", "experiments/small-sokoban-optimal/50/sokoban_p01_hyp-1_50_1.tar.bz2", "-F", "26", "-S", TestPlanRecognizer.SOLVER]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta", options)
        recognizer.run_recognizer()
        if recognizer.unique_goal is None:
            self.fail("All hypotheses failed.")
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses)
        for h in recognizer.accepted_hypotheses:
            self.assertEqual(h.score[0], 0)


if __name__ == '__main__':
    TestPlanRecognizer.SOLVER = os.environ.get('lpr_solver', TestPlanRecognizer.SOLVER)
    unittest.main()
