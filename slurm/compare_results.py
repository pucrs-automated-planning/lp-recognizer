#!/usr/bin/env python3
"""
Compare reference outputs/ (from get_results.sh) with new per-instance
slurm-results/ files produced by the Slurm array pipeline.

Usage (from repository root):
    python3 slurm/compare_results.py [--ref <ref-dir>] [--results <results-dir>]

Defaults:
    --ref     tmp/reference-outputs/
    --results slurm-results/

Output: per-instance verdict (MATCH / DIFF / MISSING / TRUNCATED / EXTRA),
        followed by a summary.
"""

import argparse
import os
import sys
from collections import defaultdict


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_merged_file(path):
    """
    Parse a merged .output file (one instance per 'record').
    Returns dict: instance_key -> {'header': str, 'hyps': list-of-str}
    instance_key is the first field of the header line (problem path).
    """
    records = {}
    current_key = None
    current_hyps = []

    with open(path) as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('> '):
                if current_key:
                    current_hyps.append(line)
            elif line:
                # New record header
                if current_key:
                    records[current_key] = current_hyps
                current_key = line.split(':')[0]
                current_hyps = []

    if current_key:
        records[current_key] = current_hyps

    return records


def parse_instance_file(path):
    """
    Parse a single per-instance .output file.
    Returns (instance_key, hyp_lines) or (None, None) if empty/truncated.
    """
    with open(path) as f:
        lines = f.readlines()

    if not lines:
        return None, None

    header = lines[0].rstrip('\n')
    instance_key = header.split(':')[0]
    hyp_lines = [l.rstrip('\n') for l in lines[1:] if l.startswith('> ')]

    return instance_key, hyp_lines


def hyp_accepted(hyp_line):
    """Extract accepted flag from '> idx:True/False:...' """
    parts = hyp_line.split(':')
    return parts[1] if len(parts) > 1 else '?'


def hyp_scores(hyp_line):
    """Extract h,h_c scores from '> idx:accepted:h,h_c:...' """
    parts = hyp_line.split(':')
    return parts[2] if len(parts) > 2 else ''


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare_hyps(ref_hyps, new_hyps):
    """
    Compare two lists of hypothesis lines.
    Returns list of difference strings (empty = match).
    """
    diffs = []
    if len(ref_hyps) != len(new_hyps):
        diffs.append(f"hyp count: ref={len(ref_hyps)} new={len(new_hyps)}")
        return diffs

    for ref_h, new_h in zip(ref_hyps, new_hyps):
        ref_idx = ref_h.split(':')[0].replace('> ', '')
        if hyp_accepted(ref_h) != hyp_accepted(new_h):
            diffs.append(
                f"hyp {ref_idx} accepted: ref={hyp_accepted(ref_h)} "
                f"new={hyp_accepted(new_h)}"
            )
        if hyp_scores(ref_h) != hyp_scores(new_h):
            diffs.append(
                f"hyp {ref_idx} scores: ref={hyp_scores(ref_h)} "
                f"new={hyp_scores(new_h)}"
            )
    return diffs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='tmp/reference-outputs',
                        help='Directory with reference merged .output files')
    parser.add_argument('--results', default='slurm-results',
                        help='Directory with per-instance slurm result files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print MATCH lines too')
    parser.add_argument('--method', default=None,
                        help='Filter to a single method (e.g. delta-cdt)')
    args = parser.parse_args()

    ref_dir = args.ref
    results_dir = args.results

    if not os.path.isdir(ref_dir):
        print(f"ERROR: reference dir not found: {ref_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(results_dir):
        print(f"ERROR: results dir not found: {results_dir}", file=sys.stderr)
        sys.exit(1)

    counts = defaultdict(int)

    for ref_fname in sorted(os.listdir(ref_dir)):
        if not ref_fname.endswith('.output'):
            continue

        # Filename format: domain-type-method.output
        # We need to separate domain-type from method.
        # Methods contain only letters, digits, and hyphens; same for domain-type.
        # Strategy: try each suffix split on '-' until we find a matching results dir.
        stem = ref_fname[:-len('.output')]
        domain_type = None
        method = None

        parts = stem.split('-')
        for i in range(len(parts) - 1, 0, -1):
            candidate_method = '-'.join(parts[i:])
            candidate_domain = '-'.join(parts[:i])
            if os.path.isdir(os.path.join(results_dir, candidate_domain,
                                          candidate_method)):
                domain_type = candidate_domain
                method = candidate_method
                break

        if domain_type is None:
            print(f"SKIP (no results dir): {stem}")
            counts['skip'] += 1
            continue

        if args.method and method != args.method:
            continue

        ref_path = os.path.join(ref_dir, ref_fname)
        ref_records = parse_merged_file(ref_path)

        obs_levels = ['10', '30', '50', '70', '100']

        for instance_key, ref_hyps in sorted(ref_records.items()):
            # instance_key: domain-type/obs/filename.tar.bz2
            key_parts = instance_key.replace('\\', '/').split('/')
            if len(key_parts) < 3:
                print(f"  WARN: unexpected key format: {instance_key}")
                continue
            obs = key_parts[-2]
            fname_base = key_parts[-1].replace('.tar.bz2', '')

            new_path = os.path.join(
                results_dir, domain_type, method,
                f'obs{obs}', f'{fname_base}.output'
            )

            if not os.path.exists(new_path):
                print(f"MISSING  {domain_type}/{method}/obs{obs}/{fname_base}")
                counts['missing'] += 1
                continue

            new_key, new_hyps = parse_instance_file(new_path)

            if new_hyps is None or len(new_hyps) == 0:
                if not ref_hyps:
                    # Both have no hyps — both truncated
                    if args.verbose:
                        print(f"BOTH-TRUNC {domain_type}/{method}/obs{obs}/{fname_base}")
                    counts['both_trunc'] += 1
                else:
                    print(f"TRUNCATED  {domain_type}/{method}/obs{obs}/{fname_base}  "
                          f"(ref has {len(ref_hyps)} hyps)")
                    counts['truncated'] += 1
                continue

            if not ref_hyps:
                # Reference is truncated but new has results
                print(f"NEW-OK     {domain_type}/{method}/obs{obs}/{fname_base}  "
                      f"(ref was truncated, new has {len(new_hyps)} hyps)")
                counts['new_ok'] += 1
                continue

            diffs = compare_hyps(ref_hyps, new_hyps)
            if diffs:
                print(f"DIFF       {domain_type}/{method}/obs{obs}/{fname_base}")
                for d in diffs:
                    print(f"           {d}")
                counts['diff'] += 1
            else:
                if args.verbose:
                    print(f"MATCH      {domain_type}/{method}/obs{obs}/{fname_base}")
                counts['match'] += 1

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    total = sum(counts.values())
    for label, count in sorted(counts.items()):
        print(f"  {label:<14} {count:>6}  ({100*count/total:.1f}%)")
    print(f"  {'TOTAL':<14} {total:>6}")


if __name__ == '__main__':
    main()
