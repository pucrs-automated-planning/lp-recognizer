#!/usr/bin/env python2.7

import unittest

from options import Program_Options
from plan_recognizer_factory import PlanRecognizerFactory
from const_plan_recognizer import *
from delta_plan_recognizer import *

class TestPlanRecognizerFactory(unittest.TestCase):
    def setUp(self):
        args = ["-e", "experiments/sokoban/10/sokoban_p07_hyp-4_10_3.tar.bz2"]
        options = Program_Options(args)
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
        recognizer = self.factory.get_recognizer("delta-h-s")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHS)
        recognizer = self.factory.get_recognizer("delta-h-s-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHSUncertainty)
        recognizer = self.factory.get_recognizer("delta-h-c")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        recognizer = self.factory.get_recognizer("delta-h-c-f2")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        recognizer = self.factory.get_recognizer("delta-h-c-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHCUncertainty)
        recognizer = self.factory.get_recognizer("delta-h-c-f2-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHCUncertainty)

    def test_hvalue_recognizer(self):
        print("Testing h-value")
        args = ["-e", "experiments/sokoban/100/sokoban_p01_hyp-1_full.tar.bz2"] # obs_count = C*
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("h-value", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for h in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(h.obs_count, h.score[0])
            self.assertGreaterEqual(h.obs_count, h.score[1])

    def test_deltahc_recognizer(self):
        print("Testing delta-h-c")
        args = ["-e", "experiments/sokoban/10/sokoban_p07_hyp-4_10_3.tar.bz2"]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta-h-c", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for h in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(h.score[0], 0)

    def test_deltahc_uncertainty_recognizer(self):
        print("Testing delta-h-c-uncertainty")
        args = ["-e", "experiments/sokoban/10/sokoban_p07_hyp-4_10_3.tar.bz2"]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta-h-c-uncertainty", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for h in recognizer.accepted_hypotheses:
            self.assertGreaterEqual(h.score[0], 0)
        self.assertGreater(recognizer.uncertainty_ratio, 1)

    def test_deltahc_filter_recognizer(self):
        print("Testing delta-h-c with filter")
        args = ["-e", "experiments/sokoban/50/sokoban_p01_hyp-1_50_1.tar.bz2", "-F", "26"]
        options = Program_Options(args)
        recognizer = self.factory.get_recognizer("delta-h-c", options)
        recognizer.run_recognizer()
        self.assertTrue(recognizer.unique_goal in recognizer.accepted_hypotheses) 
        for h in recognizer.accepted_hypotheses:
            self.assertEqual(h.score[0], 0)

if __name__ == '__main__':
    unittest.main()
    