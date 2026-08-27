#!/usr/bin/env python3
"""Parser and simulator for Fast Downward's grounded SAS+ task (``output.sas``).

Plan extraction needs to *execute* candidate action sequences, which means a
model of the grounded task. We read the SAS+ file FD itself produced rather
than grounding the PDDL again: operator names in ``output.sas`` are exactly the
names the operator-counting heuristic writes to
``ocsingleshot_heuristic_result.dat``, so counts and operators line up by
construction. An independent grounder would desynchronise the two.
"""

from dataclasses import dataclass, field


@dataclass
class Operator:
    """A grounded SAS+ operator."""

    name: str           # e.g. "board c0 l0" (no surrounding parentheses)
    prevail: list       # [(var, value)] conditions that must hold and persist
    effects: list       # [(conditions, var, precondition_value, new_value)]
    cost: int
    index: int

    def applicable(self, state):
        for var, value in self.prevail:
            if state[var] != value:
                return False
        for conditions, var, pre, _ in self.effects:
            if pre != -1 and state[var] != pre:
                return False
            for cond_var, cond_value in conditions:
                if state[cond_var] != cond_value:
                    return False
        return True

    def apply(self, state):
        successor = list(state)
        for conditions, var, _, post in self.effects:
            if all(state[v] == value for v, value in conditions):
                successor[var] = post
        return tuple(successor)


@dataclass
class SASTask:
    """A grounded SAS+ planning task."""

    var_names: list
    fact_names: list        # fact_names[var][value] -> "Atom at(c0, l0)"
    init: tuple
    goal: list              # [(var, value)]
    operators: list
    by_name: dict = field(default_factory=dict)

    def __post_init__(self):
        self.by_name = {op.name: op for op in self.operators}

    def goal_reached(self, state):
        return all(state[var] == value for var, value in self.goal)

    def unsatisfied_goals(self, state):
        return sum(1 for var, value in self.goal if state[var] != value)


class SASReader:
    """Line-oriented reader for the SAS+ format."""

    def __init__(self, text):
        self.lines = text.splitlines()
        self.index = 0

    def next(self):
        line = self.lines[self.index]
        self.index += 1
        return line

    def expect(self, token):
        line = self.next()
        if line != token:
            raise ValueError("expected %r but found %r on line %d"
                             % (token, line, self.index))

    def next_int(self):
        return int(self.next())


def parse_sas(filename):
    """Parse ``output.sas`` into a SASTask."""
    with open(filename) as sas_file:
        reader = SASReader(sas_file.read())

    reader.expect('begin_version')
    version = reader.next_int()
    if version != 3:
        raise ValueError("unsupported SAS+ version %d" % version)
    reader.expect('end_version')

    reader.expect('begin_metric')
    uses_action_costs = reader.next_int()
    reader.expect('end_metric')

    num_variables = reader.next_int()
    var_names, fact_names = [], []
    for _ in range(num_variables):
        reader.expect('begin_variable')
        var_names.append(reader.next())
        reader.next_int()                     # axiom layer, unused here
        domain_size = reader.next_int()
        fact_names.append([reader.next() for _ in range(domain_size)])
        reader.expect('end_variable')

    for _ in range(reader.next_int()):        # mutex groups, unused here
        reader.expect('begin_mutex_group')
        for _ in range(reader.next_int()):
            reader.next()
        reader.expect('end_mutex_group')

    reader.expect('begin_state')
    init = tuple(reader.next_int() for _ in range(num_variables))
    reader.expect('end_state')

    reader.expect('begin_goal')
    goal = []
    for _ in range(reader.next_int()):
        var, value = reader.next().split()
        goal.append((int(var), int(value)))
    reader.expect('end_goal')

    operators = []
    for index in range(reader.next_int()):
        reader.expect('begin_operator')
        # Zero-arity operators are named with a trailing space ("o3 "), so
        # names are stripped here and observations are stripped to match.
        name = reader.next().strip()
        prevail = []
        for _ in range(reader.next_int()):
            var, value = reader.next().split()
            prevail.append((int(var), int(value)))
        effects = []
        for _ in range(reader.next_int()):
            tokens = [int(t) for t in reader.next().split()]
            num_conditions = tokens[0]
            conditions = [(tokens[1 + 2 * i], tokens[2 + 2 * i])
                          for i in range(num_conditions)]
            var, pre, post = tokens[1 + 2 * num_conditions:4 + 2 * num_conditions]
            effects.append((conditions, var, pre, post))
        cost = reader.next_int()
        reader.expect('end_operator')
        operators.append(Operator(name, prevail, effects,
                                  cost if uses_action_costs else 1, index))

    return SASTask(var_names, fact_names, init, goal, operators)
