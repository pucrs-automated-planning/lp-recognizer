#!/usr/bin/env python3
"""Sequence LP operator counts into a valid, observation-respecting plan.

The operator-counting heuristic returns a *multiset* of operators: how often
each operator appears in some solution of the LP. Operator-counting constraints
are necessary but not sufficient, so a count vector need not be sequenceable
into an executable plan -- the classic failure is a disconnected cycle in the
state-equation flow. Validity therefore comes from this search, not from the LP.

We search over triples (state, observation_pointer, remaining_budget):

* applicable actions are those with budget left whose preconditions hold in
  ``state``;
* applying the action at ``observations[pointer]`` may advance the pointer. We
  branch on advancing so that a repeated action can serve either as the
  observation or as an ordinary step;
* a state is a goal when the SAS+ goal holds *and* the pointer has consumed
  every observation.

Order-consistency is thus enforced by construction in the search state. Nothing
is added to the domain and no compilation is involved.

When the counts do not sequence we relax them in rungs, reporting which rung
produced the plan so that callers can tell an LP-derived plan from a fallback.
"""

import heapq
from dataclasses import dataclass

# Rungs of the relaxation ladder, in the order they are tried.
EXACT_COUNTS = 0
COUNTS_PLUS_ONE = 1
SUPPORT_UNBOUNDED = 2
ALL_OPERATORS = 3

RUNG_NAMES = {
    EXACT_COUNTS: "exact-counts",
    COUNTS_PLUS_ONE: "counts+1",
    SUPPORT_UNBOUNDED: "support-unbounded",
    ALL_OPERATORS: "all-operators",
}

# Weight on the goal-distance estimate. The search is deliberately greedy: any
# valid plan is acceptable, and h_c already certifies optimality when it is met.
HEURISTIC_WEIGHT = 3


@dataclass
class SequencingResult:
    plan: list                  # list of operator names, or None on failure
    rung: int
    expanded: int
    generated: int

    @property
    def rung_name(self):
        return RUNG_NAMES[self.rung]


def budget_and_action_set(task, counts, rung):
    """Return (budget, allowed_operator_indexes) for a rung of the ladder.

    A budget of None means operators may be applied without limit.
    """
    support = {}
    for name, count in counts.items():
        operator = task.by_name.get(name)
        if operator is not None:
            support[operator.index] = int(round(count))
    if rung == EXACT_COUNTS:
        return support, set(support)
    if rung == COUNTS_PLUS_ONE:
        return {i: c + 1 for i, c in support.items()}, set(support)
    if rung == SUPPORT_UNBOUNDED:
        return None, set(support)
    return None, set(op.index for op in task.operators)


def sequence(task, counts, observations, rung, max_expansions=200000,
             greedy_match=False):
    """Best-first search for a valid plan explaining the observations in order.

    ``observations`` are SAS+ operator names; unmappable observations must be
    filtered out by the caller, mirroring the heuristic's own pruning.
    """
    budget, allowed = budget_and_action_set(task, counts, rung)
    operators = [op for op in task.operators if op.index in allowed]
    num_observations = len(observations)

    def estimate(state, pointer):
        return task.unsatisfied_goals(state) + (num_observations - pointer)

    initial_budget = tuple(sorted(budget.items())) if budget is not None else None
    initial = (task.init, 0, initial_budget)
    queue = [(estimate(task.init, 0), 0, initial, [])]
    best_cost = {initial: 0}
    expanded = generated = 0

    while queue and expanded < max_expansions:
        _, cost, node, plan = heapq.heappop(queue)
        state, pointer, budget_key = node
        if best_cost.get(node, float('inf')) < cost:
            continue
        expanded += 1
        if pointer == num_observations and task.goal_reached(state):
            return SequencingResult(plan, rung, expanded, generated)

        remaining = dict(budget_key) if budget_key is not None else None
        for operator in operators:
            if remaining is not None and remaining.get(operator.index, 0) <= 0:
                continue
            if not operator.applicable(state):
                continue
            successor = operator.apply(state)
            if remaining is None:
                successor_budget = None
            else:
                updated = dict(remaining)
                updated[operator.index] -= 1
                successor_budget = tuple(sorted(updated.items()))

            explains = (pointer < num_observations
                        and operator.name == observations[pointer])
            if explains:
                pointers = [pointer + 1] if greedy_match else [pointer + 1, pointer]
            else:
                pointers = [pointer]

            for next_pointer in pointers:
                successor_node = (successor, next_pointer, successor_budget)
                successor_cost = cost + operator.cost
                if best_cost.get(successor_node, float('inf')) <= successor_cost:
                    continue
                best_cost[successor_node] = successor_cost
                generated += 1
                heapq.heappush(queue, (
                    successor_cost
                    + HEURISTIC_WEIGHT * estimate(successor, next_pointer),
                    successor_cost, successor_node, plan + [operator.name]))

    return SequencingResult(None, rung, expanded, generated)


def sequence_with_fallback(task, counts, observations,
                           max_rung=ALL_OPERATORS, **kwargs):
    """Try each rung of the relaxation ladder until one yields a plan."""
    for rung in range(EXACT_COUNTS, max_rung + 1):
        result = sequence(task, counts, observations, rung, **kwargs)
        if result.plan is not None:
            return result
    return result
