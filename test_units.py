#!/usr/bin/env python2.7

import unittest

from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory
from const_plan_recognizer import *
from delta_plan_recognizer import *

class TestPlanRecognizerFactory(unittest.TestCase):
    def setUp(self):
        options = Program_Options([])
        self.factory = PlanRecognizerFactory(options)

    def test_factory(self):
        recognizer = self.factory.get_recognizer("h-value")
        self.assertEqual(recognizer.__class__, LPRecognizerHValue)
        recognizer = self.factory.get_recognizer("h-value-c")
        self.assertEqual(recognizer.__class__, LPRecognizerHValueC)
        recognizer = self.factory.get_recognizer("soft-c")
        self.assertEqual(recognizer.__class__, LPRecognizerSoftC)
        recognizer = self.factory.get_recognizer("soft-c-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerSoftCUncertainty)
        recognizer = self.factory.get_recognizer("delta-h-c")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        recognizer = self.factory.get_recognizer("delta-h-c-f2")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        recognizer = self.factory.get_recognizer("delta-h-c-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHCUncertainty)
        recognizer = self.factory.get_recognizer("delta-h-c-f2-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHCUncertainty)

    def test_lmcut(self):
        print("\nTesting h-value with lmcut")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "lmcut_constraints()"]
        options = Program_Options(args)
        recognizer_c = self.factory.get_recognizer("h-value", options)
        recognizer_c.run_recognizer()

    def test_lmcut_obs(self):
        print("\nTesting delta-h-c with lmcut")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "lmcut_constraints()"]
        options = Program_Options(args)
        recognizer_c = self.factory.get_recognizer("delta-h-c", options)
        recognizer_c.run_recognizer()

    def test_lmcut_obs2(self):
        print("\nTesting delta-h-c modified with lmcut")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "lmcut_constraints()", '-o']
        options = Program_Options(args)
        recognizer_c = self.factory.get_recognizer("delta-h-c", options)
        recognizer_c.run_recognizer()

    def test_flow(self):
        print("\nTesting h-value with flow")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "flow_constraints(systematic(2))"]
        #args[1] = "experiments/small-sokoban/100/sokoban_p01_hyp-1_full.tar.bz2" # obs_count = C*
        options = Program_Options(args)
        recognizer_c = self.factory.get_recognizer("h-value", options)
        recognizer_c.run_recognizer()

    def test_flow_obs(self):
        print("\nTesting delta-h-c with flow")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "flow_constraints(systematic(2))"]
        #args[1] = "experiments/small-sokoban/100/sokoban_p01_hyp-1_full.tar.bz2" # obs_count = C*
        options = Program_Options(args)
        recognizer_c = self.factory.get_recognizer("delta-h-c", options)
        recognizer_c.run_recognizer()

    def test_relaxation(self):
        print("\nTesting delta-h-c with delete relaxation")
        args = ["-e", "experiments/example/example.tar.bz2", "-H", "delete_relaxation_constraints()"]
        #args[1] = "experiments/small-sokoban/100/sokoban_p01_hyp-1_full.tar.bz2" # obs_count = C*
        options = Program_Options(args)
        recognizer_c = self.factory.get_recognizer("delta-h-c", options)
        recognizer_c.run_recognizer()

    def test_deltahc_filter_recognizer(self):
        print("\nTesting delta-h-c with filter")
        args = ["-e", "experiments/small-sokoban/50/sokoban_p01_hyp-1_50_1.tar.bz2", "-F", "26"]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta-h-c", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for h in recognizer.accepted_hypotheses:
            self.assertEqual(h.score[0], 0)

    def test_deltahc_uncertainty_recognizer(self):
        print("\nTesting delta-h-c-uncertainty")
        args = ["-e", "experiments/small-sokoban/10/sokoban_p01_hyp-1_10_1.tar.bz2"]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta-h-c-uncertainty", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for h in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(h.score[0], 0)
        self.assertGreater(recognizer.uncertainty_ratio, 1)

    def test_deltahc_recognizer(self):
        print("\nTesting delta-h-c")
        args = ["-e", "experiments/small-sokoban/10/sokoban_p01_hyp-1_10_1.tar.bz2"]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta-h-c", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for h in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(h.score[0], 0)

    def test_hvalue_recognizer(self):
        print("\nTesting h-value")
        args = ["-e", "experiments/small-sokoban/100/sokoban_p01_hyp-1_full.tar.bz2"] # obs_count = C*
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("h-value", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for hyp in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(hyp.num_obs, hyp.h)
            self.assertGreaterEqual(hyp.num_obs, hyp.obs_hits)

if __name__ == '__main__':
    unittest.main()
    