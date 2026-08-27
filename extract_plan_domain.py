#!/usr/bin/env python3
"""Batch plan extraction over a domain, mirroring test_domain.py.

Writes one JSON record per instance plus a summary. The headline figure is the
share of instances solved at rung 0, where the LP counts sequence directly into
a valid plan with no relaxation.

Usage:
    ./extract_plan_domain.py <base_path> <domain_name> [options]
    ./extract_plan_domain.py ../goal-plan-recognition-dataset ferry-optimal -o 1
"""

import json
import os
import sys
import time
from collections import Counter

import extract_plan

OBSERVABILITY = ['10', '30', '50', '70', '100']


def summarise(records):
    solved = [r for r in records if r['status'] == 'SOLVED']
    summary = {
        'instances': len(records),
        'status': dict(Counter(r['status'] for r in records)),
        'rung': dict(Counter(r['fallback_rung'] for r in solved)),
        'rung_0': sum(1 for r in solved if r['fallback_rung'] == 0),
        'val_valid': sum(1 for r in solved if r['val_valid']),
        'val_unavailable': sum(1 for r in solved if r['val_valid'] is None),
        'obs_is_subsequence': sum(1 for r in solved if r['obs_is_subsequence']),
        'cost_ge_h_c': sum(1 for r in solved if r['cost_ge_h_c']),
        'certified_optimal': sum(1 for r in solved if r['certified_optimal']),
        'h_obs_fallbacks': sum(1 for r in records
                               if r.get('h_obs_used') != r.get('h_obs')),
        'solved': len(solved),
    }
    return summary


def do_experiments(base_path, domain_name, observability, options):
    started = time.time()
    os.makedirs('plan-output', exist_ok=True)
    records = []
    for obs in observability:
        directory = os.path.join(base_path, domain_name, obs)
        if not os.path.isdir(directory):
            print("Skipping missing directory: " + directory)
            continue
        files = sorted(f for f in os.listdir(directory) if f.endswith('.tar.bz2'))
        for number, filename in enumerate(files, start=1):
            print("%s:%s%% - %d/%d" % (domain_name, obs, number, len(files)))
            options.workdir = os.path.join('plan-output', domain_name, obs,
                                           filename.replace('.tar.bz2', ''))
            try:
                record = extract_plan.extract_plan(
                    os.path.join(directory, filename), options)
            except Exception as error:                    # keep the batch going
                record = {'instance': filename, 'status': 'ERROR',
                          'error': str(error)}
            record.update(domain=domain_name, observability=obs)
            records.append(record)
            print("=> %s rung=%s length=%s h_c=%s valid=%s"
                  % (record['status'], record.get('fallback_rung', '-'),
                     record.get('plan_length', '-'), record.get('h_c', '-'),
                     record.get('val_valid', '-')))

    summary = summarise(records)
    with open(os.path.join('plan-output', domain_name + '.json'), 'w') as out:
        json.dump({'summary': summary, 'records': records}, out, indent=1)
    print("\n=> Summary for %s: %s" % (domain_name, json.dumps(summary)))
    print('Experiment Time: {0:3f}s'.format(time.time() - started))
    return summary


if __name__ == '__main__':
    base_path = sys.argv[1]
    domain_name = sys.argv[2]
    options = extract_plan.parse_arguments(
        ['-e', 'unused'] + sys.argv[3:])
    do_experiments(base_path, domain_name, OBSERVABILITY, options)
