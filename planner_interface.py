#!/usr/bin/env python2
import sys, os, csv, time, math
import benchmark

fd_path = "../fast-downward/"

def custom_partition(s, sep):
    i = 0
    while i < len(s):
        if s[i] == sep: break
        i = i + 1
    if i == len(s): return (None, None, None)
    if i == 0: return (None, s[i], s[i + 1:])
    return (s[:i - 1], s[i], s[i + 1:])

class PRCommand:

    def __init__(self, domain, problem, opts):
        self.domain = domain
        self.problem = problem
        self.opts = opts
        self.noext_problem = os.path.basename(self.problem).replace('.pddl', '')
        self.h_values = None
        self.obs_report = None
        self.op_counts = {}
        self.planner_string = self.make_planner_string()

    def make_planner_string(self):
        translate_options = ' --translate-options --add-implied-preconditions --keep-unimportant-variables --keep-unreachable-facts '
        search_options_template = ' --search-options --search \"astar(ocsingleshot([{h}],' + \
            'calculate_h={h_v},calculate_h_c={h_c},calculate_h_s={h_s},' + \
            'weights={w},filter={f},lpsolver=SOPLEX))\"'
        string = fd_path + '/fast-downward.py %s %s ' + translate_options
        string += search_options_template.format(h=",".join(self.opts[2]), \
            h_v = self.opts[3], \
            h_c = self.opts[4], \
            h_s = self.opts[5], \
            w = self.opts[6], \
            f = self.opts[7])
        return string

    def execute(self):
        cmd_string = self.planner_string % (self.domain, self.problem)
        self.log = benchmark.Log('%s.log' % self.noext_problem)
        self.signal, self.time = benchmark.run(cmd_string, self.opts[0], self.opts[1], self.log, False)
        self.gather_data()

    def gather_data(self):
        if self.signal == 0 and os.path.exists('ocsingleshot_heuristic_result.dat'):
            instream = open('ocsingleshot_heuristic_result.dat')
            for line in instream:
                line = line.strip()
                if 'obs-report' in line:
                    self.obs_report = [int(w) for w in line.split()[1:]]
                elif 'h-values' in line:
                    self.h_values = [float(w) for w in line.split()[1:]]
                else:
                    operator,count = line.split('=')
                    self.op_counts[operator.strip()] = float(count.strip())
            instream.close()

    def write_result(self, filename):
        res = csv.writer(open('%s' % filename, 'w'))
        res.writerow([os.path.basename(self.domain), os.path.basename(self.problem), self.signal, self.time])


class Hypothesis:

    def __init__(self, opts, atoms):
        self.atoms = atoms
        self.plan = []
        self.is_true = True
        self.test_failed = False
        self.plan_time = 0
        self.total_time = 0
        self.opts = opts

    def evaluate(self, index, observations):
        hyp_problem = 'hyp_%d_problem.pddl' % index
        self.generate_pddl_for_hyp_plan(hyp_problem)
        pr_cmd = PRCommand('domain.pddl', 'hyp_%d_problem.pddl' % index, self.opts)
        pr_cmd.execute()
        self.plan_time = pr_cmd.time
        self.total_time = pr_cmd.time
        pr_cmd.write_result('hyp_%d_planning_H.csv' % index)
        if pr_cmd.signal != 0:
            print("signal error: %d" % pr_cmd.signal)
            exit()
            self.test_failed = True
            return
        if pr_cmd.h_values == None:
            print("No h value. Failed.")
            self.test_failed = True
            return
        if pr_cmd.obs_report == None:
            print("No observation report. Failed.")
            self.test_failed = True
            return
        for x in pr_cmd.h_values:
            if x < 0:
                print("Negative h value. Failed.")
                self.test_failed = True
                return
            if x != x:
                print("h value not a number. Failed.")
                self.test_failed = True
                return
        # obs
        self.num_obs = pr_cmd.obs_report[0] - pr_cmd.obs_report[1]
        self.num_invalid_obs = pr_cmd.obs_report[1]
        self.obs_hits = pr_cmd.obs_report[2]
        self.obs_misses = pr_cmd.obs_report[3]
        self.op_counts = pr_cmd.op_counts
        self.last_obs = len(observations) - 1
        while self.op_counts.get(observations[self.last_obs].strip(), 0) == 0:
            self.last_obs -= 1
            if self.last_obs < 0:
                break
        # h values
        self.h = pr_cmd.h_values[0]
        self.h_c = pr_cmd.h_values[1]
        self.h_s = pr_cmd.h_values[2]

    def load_plan(self, plan_name):
        instream = open(plan_name)
        self.plan = []
        for line in instream:
            line = line.strip()
            if line[0] == ';': 
                continue
            _, _, stuff = custom_partition(line, ':')
            op, _, _ = custom_partition(stuff, '[')
            self.plan.append(op.strip().upper())
        instream.close()

    def generate_pddl_for_hyp_plan(self, out_name):
        instream = open('template.pddl')
        outstream = open(out_name, 'w')
        for line in instream:
            line = line.strip()
            if '<HYPOTHESIS>' not in line:
                print >> outstream, line
            else:
                for atom in self.atoms:
                    print >> outstream, atom
        outstream.close()
        instream.close()

    def check_if_actual(self):
        real_hyp_atoms = []
        instream = open('real_hyp.dat')
        for line in instream:
            real_hyp_atoms = [tok.strip() for tok in line.split(',')]
        instream.close()
        for atom in real_hyp_atoms:
            if not atom in self.atoms:
                self.is_true = False
                break

    def __str__(self):
        res = ""
        for a in self.atoms:
            res += a
        return res

    def __repr__(self):
        return str(self)

