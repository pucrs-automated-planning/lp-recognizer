#!/usr/bin/env python3

import os
import shutil
import tempfile
import unittest

import extract_plan
from plan_sequencer import (ALL_OPERATORS, EXACT_COUNTS, sequence,
                            sequence_with_fallback)
from sas_task import Operator, SASTask, parse_sas

EXAMPLE = "experiments/example/example.tar.bz2"


def chain_task(length):
    """A task of `length` operators that must run in order: o_i sets var i."""
    operators = []
    for i in range(length):
        prevail = [(j, 1) for j in range(i)]
        operators.append(Operator("o%d" % i, prevail, [([], i, 0, 1)], 1, i))
    return SASTask(["v%d" % i for i in range(length)],
                   [["false", "true"] for _ in range(length)],
                   tuple(0 for _ in range(length)),
                   [(length - 1, 1)], operators)


class TestSASTask(unittest.TestCase):

    def test_operator_application(self):
        task = chain_task(3)
        self.assertTrue(task.by_name["o0"].applicable(task.init))
        self.assertFalse(task.by_name["o1"].applicable(task.init))
        state = task.by_name["o0"].apply(task.init)
        self.assertEqual(state, (1, 0, 0))
        self.assertTrue(task.by_name["o1"].applicable(state))

    def test_goal_counting(self):
        task = chain_task(3)
        self.assertFalse(task.goal_reached(task.init))
        self.assertEqual(task.unsatisfied_goals(task.init), 1)
        self.assertTrue(task.goal_reached((1, 1, 1)))


class TestSequencer(unittest.TestCase):

    def test_exact_counts(self):
        task = chain_task(4)
        counts = {"o0": 1, "o1": 1, "o2": 1, "o3": 1}
        result = sequence(task, counts, [], EXACT_COUNTS)
        self.assertEqual(result.plan, ["o0", "o1", "o2", "o3"])

    def test_observations_are_respected_in_order(self):
        task = chain_task(4)
        counts = {"o0": 1, "o1": 1, "o2": 1, "o3": 1}
        result = sequence(task, counts, ["o1", "o3"], EXACT_COUNTS)
        self.assertEqual(result.plan, ["o0", "o1", "o2", "o3"])

    def test_unsequenceable_counts_fail_at_rung_zero(self):
        # o2 is missing, so no plan can be built from these counts alone.
        task = chain_task(4)
        counts = {"o0": 1, "o1": 1, "o3": 1}
        self.assertIsNone(sequence(task, counts, [], EXACT_COUNTS).plan)

    def test_fallback_recovers_a_plan(self):
        task = chain_task(4)
        counts = {"o0": 1, "o1": 1, "o3": 1}
        result = sequence_with_fallback(task, counts, [], max_rung=ALL_OPERATORS)
        self.assertEqual(result.plan, ["o0", "o1", "o2", "o3"])
        self.assertEqual(result.rung, ALL_OPERATORS)

    def test_expansion_limit_is_honoured(self):
        task = chain_task(6)
        counts = {"o%d" % i: 1 for i in range(6)}
        self.assertIsNone(sequence(task, counts, [], EXACT_COUNTS,
                                   max_expansions=1).plan)


class TestSubsequence(unittest.TestCase):

    def test_ordered_subsequence(self):
        plan = ["a", "b", "c", "d"]
        self.assertTrue(extract_plan.is_ordered_subsequence(["a", "c"], plan))
        self.assertTrue(extract_plan.is_ordered_subsequence([], plan))
        self.assertFalse(extract_plan.is_ordered_subsequence(["c", "a"], plan))
        self.assertFalse(extract_plan.is_ordered_subsequence(["a", "e"], plan))

    def test_repeated_observations_need_repeated_actions(self):
        self.assertTrue(extract_plan.is_ordered_subsequence(
            ["a", "a"], ["a", "b", "a"]))
        self.assertFalse(extract_plan.is_ordered_subsequence(
            ["a", "a"], ["a", "b", "c"]))


class TestEndToEnd(unittest.TestCase):
    """Runs the LP, so it needs a solver and a compiled Fast Downward."""

    SOLVER = os.environ.get('lpr_solver', 'cplex')

    def setUp(self):
        self.workdir = tempfile.mkdtemp(prefix="extract_plan_test")

    def tearDown(self):
        shutil.rmtree(self.workdir, ignore_errors=True)

    @unittest.skipIf(os.environ.get('lpr_solver', 'cplex') != 'cplex',
                     "integer operator counts require CPLEX; SoPlex has no MIP")
    def test_example_instance(self):
        options = extract_plan.parse_arguments(
            ['-e', EXAMPLE, '-S', TestEndToEnd.SOLVER,
             '--workdir', self.workdir])
        record = extract_plan.extract_plan(EXAMPLE, options)
        self.assertEqual(record['status'], 'SOLVED')
        self.assertTrue(record['obs_is_subsequence'])
        self.assertTrue(record['cost_ge_h_c'])
        self.assertTrue(os.path.exists(os.path.join(self.workdir, 'plan.txt')))

    @unittest.skipIf(os.environ.get('lpr_solver', 'cplex') != 'cplex',
                     "integer operator counts require CPLEX; SoPlex has no MIP")
    def test_sas_task_matches_fast_downward(self):
        """The parsed SAS+ task must execute the plan we extracted from it."""
        options = extract_plan.parse_arguments(
            ['-e', EXAMPLE, '-S', TestEndToEnd.SOLVER,
             '--workdir', self.workdir])
        record = extract_plan.extract_plan(EXAMPLE, options)
        task = parse_sas(os.path.join(self.workdir, 'output.sas'))
        state = task.init
        for action in record['plan']:
            operator = task.by_name[action[1:-1]]
            self.assertTrue(operator.applicable(state), action)
            state = operator.apply(state)
        self.assertTrue(task.goal_reached(state))


if __name__ == '__main__':
    unittest.main()
