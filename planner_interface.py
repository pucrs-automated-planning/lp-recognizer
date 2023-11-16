
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

class FDCommand:

    def __init__(self, domain, problem, opts):
        self.domain = domain
        self.problem = problem
        self.opts = opts
        self.noext_problem = os.path.basename(self.problem).replace('.pddl', '')
        self.log = None
        self.h_values = None
        self.obs_report = None
        self.lp_time = 0
        self.op_counts = {}
        self.planner_string = self.make_planner_string()

    def make_planner_string(self):
        translate_options = '--translate-options --add-implied-preconditions --keep-unimportant-variables --keep-unreachable-facts '
        search_options_template = '--search-options --search "astar(ocsingleshot([{h}], ' + \
            'calculate_h={h_v}, calculate_h_c={h_c}, calculate_h_s={h_s}, ' + \
            'weights={w}, filter={f}, h_obs={o}, lpsolver={s}, mip={i}))"'
        string = fd_path + 'fast-downward.py %s %s ' + translate_options
        string += search_options_template.format(h=",".join(self.opts[2]), \
            h_v = self.opts[3], \
            h_c = self.opts[4], \
            h_s = self.opts[5], \
            w = self.opts[6], \
            f = self.opts[7], \
            o = self.opts[8], \
            s = self.opts[9], \
            i = self.opts[10])
        return string

    def execute(self):
        cmd_string = self.planner_string % (self.domain, self.problem)
        self.log = benchmark.Log('%s.log' % self.noext_problem)
        self.signal, self.time = 0, 0.0
        self.signal, self.time = benchmark.run(cmd_string, self.opts[0], self.opts[1], self.log, False)
        self.gather_data()

    def gather_data(self):
        if self.signal == 0 and os.path.exists('ocsingleshot_heuristic_result.dat'):
            instream = open('ocsingleshot_heuristic_result.dat')
            for line in instream:
                line = line.strip()
                if 'obs-report' in line:
                    self.obs_report = [int(w) for w in line.split()[1:]]
                elif 'time-report' in line:
                    self.lp_time = float(line.split()[1].replace('s', ''))
                elif 'h-values' in line:
                    self.h_values = [float(w) for w in line.split()[1:]]
                elif 'lp-info' in line:
                    self.lp_info = [float(w) for w in line.split()[1:]]
                else:
                    operator,count = line.split('=')
                    self.op_counts[operator.strip()] = float(count.strip())
            instream.close()

    def write_result(self, filename):
        f = open('%s' % filename, 'w');
        res = csv.writer(f)
        res.writerow([os.path.basename(self.domain), os.path.basename(self.problem), self.signal, self.time])
        f.close()


class Hypothesis:

    def __init__(self, index, opts, atoms):
        self.index = index
        self.atoms = atoms
        self.plan = []
        self.is_true = True
        self.is_solution = False
        self.test_failed = False
        self.fd_time = 0
        self.lp_time = 0
        self.opts = opts

    def evaluate(self, observations):
        hyp_problem = 'hyp_%d_problem.pddl' % self.index
        self.generate_pddl_for_hyp_plan(hyp_problem)
        fd_cmd = FDCommand('domain.pddl', 'hyp_%d_problem.pddl' % self.index, self.opts)
        fd_cmd.execute()
        self.fd_time = fd_cmd.time
        self.lp_time = fd_cmd.lp_time
        fd_cmd.write_result('hyp_%d_planning_H.csv' % self.index)
        if fd_cmd.signal != 0:
            print("signal error: %d" % fd_cmd.signal)
            #exit()
            self.test_failed = True
            return
        if fd_cmd.h_values == None:
            print("No h value. Failed.")
            self.test_failed = True
            return
        if fd_cmd.obs_report == None:
            print("No observation report. Failed.")
            self.test_failed = True
            return
        for x in fd_cmd.h_values:
            if x < 0:
                print("Negative h value. Failed.")
                self.test_failed = True
                return
            if x != x:
                print("h value not a number. Failed.")
                self.test_failed = True
                return
        # LP size
        self.num_lp_vars = fd_cmd.lp_info[0]
        self.num_lp_consts = fd_cmd.lp_info[1]
        self.lp_info = fd_cmd.lp_info
        # obs
        self.num_obs = fd_cmd.obs_report[0] - fd_cmd.obs_report[1]
        self.num_invalid_obs = fd_cmd.obs_report[1]
        self.obs_hits = fd_cmd.obs_report[2]
        self.obs_misses = fd_cmd.obs_report[3]
        self.op_counts = fd_cmd.op_counts
        self.last_obs = len(observations) - 1
        while self.op_counts.get(observations[self.last_obs].strip(), 0) == 0:
            self.last_obs -= 1
            if self.last_obs < 0:
                break
        # h values
        self.h = fd_cmd.h_values[0]
        self.h_c = fd_cmd.h_values[1]
        self.h_s = fd_cmd.h_values[2]

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
                print(line, file=outstream)
            else:
                for atom in self.atoms:
                    print(atom, file=outstream)
        outstream.close()
        instream.close()

    def __str__(self):
        res = ""
        for a in self.atoms:
            res += a
        return res

    def __repr__(self):
        return str(self)
