#!/usr/bin/env python3
"""Plan recognition: derive a plan consistent with a set of observations.

Where the recognizers in this repository rank *goals*, this derives a *plan*.
Given a domain, an initial state, a known goal and a partial observation
sequence, it returns a plan that is executable from the initial state, achieves
the goal, and contains the observations as an ordered subsequence. Any plan
meeting those conditions is acceptable; it need not be the original one.

The plan comes from the LP itself. The operator-counting heuristic already
solves an LP whose observation constraints force the counts to cover the
observed actions, and already writes the resulting counts to
``ocsingleshot_heuristic_result.dat``. We read those counts, then sequence them
against the grounded SAS+ task (see plan_sequencer for why sequencing is needed).

The observability percentage is never used: only obs.dat is read.

Usage:
    ./extract_plan.py -e experiments/example/example.tar.bz2
    ./extract_plan.py -e <experiment.tar.bz2> --h-obs 1 --json result.json
"""

import argparse
import json
import os
import subprocess
import sys
import tarfile
import time

from plan_sequencer import ALL_OPERATORS, sequence_with_fallback
from sas_task import parse_sas

FD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "../fast-downward")

# State-equation constraints give flow-consistent counts; the delete-relaxation
# constraints with time variables and integer auxiliary variables add an
# ordering and a causal structure over the operators they select.
DEFAULT_HEURISTICS = ("state_equation_constraints(),"
                      "delete_relaxation_constraints(true,1,1,1,1,1,0)")


def find_validator():
    """Locate VAL's Validate binary, or return None if it is not installed."""
    candidates = [os.environ.get("VAL")]
    if os.environ.get("VAL"):
        candidates.append(os.path.join(os.environ["VAL"], "Validate"))
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "../VAL/build/macos64/Release/bin/Validate"))
    for candidate in candidates:
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    from shutil import which
    return which("Validate")


def extract_experiment(archive, workdir):
    """Unpack an experiment archive, tolerating a wrapping directory."""
    os.makedirs(workdir, exist_ok=True)
    with tarfile.open(archive, "r:bz2") as tar:
        members = tar.getmembers()
        strip = all("/" in m.name for m in members if m.isfile())
        for member in members:
            if strip:
                member.name = member.name.split("/", 1)[-1]
        tar.extractall(workdir)


def generate_problem(workdir):
    """Instantiate template.pddl with the true goal from real_hyp.dat.

    This is the same <HYPOTHESIS> substitution Hypothesis.generate_pddl_for_hyp_plan
    performs; hyps.dat is deliberately not read, since the goal is given.
    """
    with open(os.path.join(workdir, 'real_hyp.dat')) as hyp_file:
        hypothesis = hyp_file.read().strip()
    atoms = [atom.strip() for atom in hypothesis.split(',') if atom.strip()]
    lines = []
    with open(os.path.join(workdir, 'template.pddl')) as template:
        for line in template:
            line = line.rstrip('\n')
            lines.extend(atoms if '<HYPOTHESIS>' in line else [line])
    with open(os.path.join(workdir, 'problem.pddl'), 'w') as problem:
        problem.write('\n'.join(lines) + '\n')
    return atoms


def run_lp(workdir, options, h_obs=None):
    """Run the single-shot operator-counting heuristic and parse its output.

    calculate_h_s is off deliberately: output_results extracts the counts from
    h_s if it was computed, h_c otherwise, so leaving soft constraints on would
    silently return counts from an LP with different observation constraints.
    """
    if h_obs is None:
        h_obs = options.h_obs
    search = ('astar(ocsingleshot([%s], calculate_h=true, calculate_h_c=true, '
              'calculate_h_s=false, weights=3, filter=%d, h_obs=%d, '
              'lpsolver=%s, mip=%s))'
              % (options.heuristics, options.filter, h_obs,
                 options.solver, 'false' if options.no_mip else 'true'))
    command = [sys.executable, os.path.join(FD_PATH, 'fast-downward.py'),
               '--keep-sas-file', 'domain.pddl', 'problem.pddl',
               '--translate-options', '--add-implied-preconditions',
               '--keep-unimportant-variables', '--keep-unreachable-facts',
               '--search-options', '--search', search]
    started = time.time()
    with open(os.path.join(workdir, 'fd.log'), 'w') as log:
        returncode = subprocess.call(command, cwd=workdir, stdout=log,
                                     stderr=subprocess.STDOUT,
                                     timeout=options.max_time)
    result = {'returncode': returncode, 'wall_time': time.time() - started,
              'counts': {}, 'h': None, 'h_c': None, 'lp_time': None}

    resultfile = os.path.join(workdir, 'ocsingleshot_heuristic_result.dat')
    if not os.path.exists(resultfile):
        return result
    with open(resultfile) as counts:
        parse_lp_result(counts, result)
    return result


def parse_lp_result(lines, result):
    """Parse ocsingleshot_heuristic_result.dat into the result record."""
    for line in lines:
        line = line.strip()
        if line.startswith('h-values:'):
            values = [float(v) for v in line.split()[1:]]
            result['h'], result['h_c'] = values[0], values[1]
        elif line.startswith('obs-report:'):
            result['obs_report'] = [int(float(v)) for v in line.split()[1:]]
        elif line.startswith('time-report:'):
            result['lp_time'] = float(line.split()[1].replace('s', ''))
        elif line.startswith('lp-info:'):
            result['lp_info'] = [float(v) for v in line.split()[1:]]
        elif '=' in line:
            name, count = line.rsplit('=', 1)
            result['counts'][name.strip()[1:-1].strip().lower()] = float(count)


def load_observations(workdir, task, filename='obs.dat'):
    """Read obs.dat as SAS+ operator names.

    Observations that match no grounded operator are separated out rather than
    dropped silently, mirroring OCSingleShotHeuristic::prune_observations.
    """
    observations, unmappable = [], []
    with open(os.path.join(workdir, filename)) as obs_file:
        for line in obs_file:
            line = line.strip().lower()
            if not line or line.startswith(';'):
                continue
            name = line[1:-1].strip() if line.startswith('(') else line
            (observations if name in task.by_name else unmappable).append(name)
    return observations, unmappable


def is_ordered_subsequence(observations, plan):
    remaining = iter(plan)
    return all(any(action == observation for action in remaining)
               for observation in observations)


def write_plan(workdir, plan, cost):
    """Write the plan in IPC format, plus the numbered form VAL requires."""
    with open(os.path.join(workdir, 'plan.txt'), 'w') as out:
        for action in plan:
            out.write('(%s)\n' % action)
        out.write('; cost = %d\n' % cost)
    with open(os.path.join(workdir, 'val_plan.txt'), 'w') as out:
        for step, action in enumerate(plan):
            out.write('%d: (%s)\n' % (step, action))


def validate(workdir):
    """Check the plan with VAL. Returns (valid, message); valid is None if VAL
    is unavailable, which is not treated as a failure."""
    validator = find_validator()
    if validator is None:
        return None, "VAL not found (set $VAL to enable validation)"
    completed = subprocess.run(
        [validator, 'domain.pddl', 'problem.pddl', 'val_plan.txt'],
        cwd=workdir, capture_output=True, text=True)
    output = completed.stdout.strip()
    if 'Successful plans:' in output:
        valid = True
    elif 'Failed plans:' in output:
        valid = False
    else:
        # VAL could not read the domain or problem at all, which says nothing
        # about the plan. Report it as unknown rather than as invalid.
        valid = None
    return valid, output.splitlines()[-1] if output else completed.stderr.strip()


def extract_plan(archive, options):
    """Run the whole pipeline on one experiment; returns the result record."""
    name = os.path.basename(archive).replace('.tar.bz2', '')
    workdir = options.workdir or os.path.join(os.getcwd(), 'plan-output', name)
    extract_experiment(archive, workdir)
    goal_atoms = generate_problem(workdir)

    lp = run_lp(workdir, options)
    h_obs_used = options.h_obs
    if not lp['counts'] and options.h_obs > 0:
        # Putting observations inside the constraint generators can make the
        # MIP infeasible: observed operators are forced to be used, and the
        # delete relaxation cannot always place them. Fall back rather than
        # returning nothing, and record which level actually produced the counts.
        lp = run_lp(workdir, options, h_obs=0)
        h_obs_used = 0
    record = {'instance': name, 'goal_atoms': goal_atoms, 'h': lp['h'],
              'h_c': lp['h_c'], 'lp_time': lp['lp_time'],
              'lp_wall_time': lp['wall_time'],
              'lp_returncode': lp['returncode'],
              'lp_count_total': sum(lp['counts'].values()),
              'h_obs': options.h_obs, 'h_obs_used': h_obs_used,
              'workdir': workdir}
    if not lp['counts']:
        record['status'] = 'LP_FAILED'
        return record

    task = parse_sas(os.path.join(workdir, 'output.sas'))
    observations, unmappable = load_observations(workdir, task)
    record.update(num_observations=len(observations) + len(unmappable),
                  num_unmappable_observations=len(unmappable),
                  unmappable_observations=unmappable)

    started = time.time()
    result = sequence_with_fallback(task, lp['counts'], observations,
                                    max_rung=options.max_rung,
                                    max_expansions=options.max_expansions)
    record['sequencing_time'] = time.time() - started
    record['expanded'] = result.expanded
    if result.plan is None:
        record['status'] = 'SEQUENCING_FAILED'
        return record

    cost = sum(task.by_name[action].cost for action in result.plan)
    write_plan(workdir, result.plan, cost)
    valid, message = validate(workdir)
    record.update(status='SOLVED', fallback_rung=result.rung,
                  fallback_rung_name=result.rung_name,
                  plan_length=len(result.plan), plan_cost=cost,
                  obs_is_subsequence=is_ordered_subsequence(observations,
                                                            result.plan),
                  val_valid=valid, val_message=message,
                  # h_c lower-bounds any observation-respecting plan, so a
                  # cheaper plan would mean the LP or the sequencer is wrong.
                  cost_ge_h_c=(lp['h_c'] is None or cost >= lp['h_c']),
                  certified_optimal=(cost == lp['h_c']
                                     and result.rung == 0),
                  plan=['(%s)' % action for action in result.plan])
    return record


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('-e', '--experiment', required=True,
                        help="plan recognition experiment file (tar.bz2)")
    parser.add_argument('-H', '--heuristics', default=DEFAULT_HEURISTICS,
                        help="comma-separated operator-counting constraints")
    parser.add_argument('-S', '--solver', default='cplex',
                        help="LP solver; MIP counts require CPLEX")
    parser.add_argument('-F', '--filter', type=int, default=0,
                        help="observation filter F, ignoring F*10%% of observations")
    parser.add_argument('-o', '--h-obs', type=int, default=0,
                        help="observations inside heuristic constraints: "
                             "0 none, 1 as a set, 2 soft order, 3 hard order. "
                             "Levels above 0 tighten the counts but can make "
                             "the MIP infeasible, in which case level 0 is "
                             "retried automatically")
    parser.add_argument('--no-mip', action='store_true',
                        help="solve the LP relaxation instead of the MIP; "
                             "counts may then be fractional")
    parser.add_argument('-t', '--max-time', type=int, default=1800,
                        help="time limit in seconds for the LP")
    parser.add_argument('--max-rung', type=int, default=ALL_OPERATORS,
                        help="highest relaxation rung the sequencer may use")
    parser.add_argument('--max-expansions', type=int, default=200000,
                        help="node limit per sequencing attempt")
    parser.add_argument('--workdir', default=None,
                        help="working directory (default plan-output/<instance>)")
    parser.add_argument('--json', default=None, help="write the result record here")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="print a one-line summary instead of the record")
    return parser.parse_args(argv)


def main(argv):
    options = parse_arguments(argv)
    record = extract_plan(options.experiment, options)
    if options.json:
        with open(options.json, 'w') as out:
            json.dump(record, out, indent=1)
    if options.quiet:
        print("%s %s rung=%s length=%s h_c=%s valid=%s"
              % (record['instance'], record['status'],
                 record.get('fallback_rung', '-'),
                 record.get('plan_length', '-'), record.get('h_c', '-'),
                 record.get('val_valid', '-')))
    else:
        print(json.dumps(record, indent=1))
    return 0 if record['status'] == 'SOLVED' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
