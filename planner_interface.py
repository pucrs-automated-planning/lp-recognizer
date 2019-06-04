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

    def __init__(self, domain, problem, max_time=120, max_mem=2048):
        self.domain = domain
        self.problem = problem
        self.noext_problem = os.path.basename(self.problem).replace('.pddl', '')
        self.max_time = max_time
        self.max_mem = max_mem
        self.num_accounted_obs = 'n/a'
        #
        self.h_value = 'n/a'
        self.op_counts = {}
        self.planner_string = fd_path + '/fast-downward %s %s --translate-options --add-implied-preconditions --keep-unimportant-variables --keep-unreachable-facts --search-options --search \"astar(ocsingleshot([lmcut_constraints(), pho_constraints(), state_equation_constraints()],enforce_observations=false, soft_constraints=false))\"'

    def execute(self):
        cmd_string = self.planner_string % (self.domain, self.problem)
        self.log = benchmark.Log('%s.log' % self.noext_problem)
        self.signal, self.time = benchmark.run(cmd_string, self.max_time, self.max_mem, self.log, False)
        self.gather_data()

    def gather_data(self):
        if self.signal == 0 and os.path.exists('ocsingleshot_heuristic_result.dat'):
            instream = open('ocsingleshot_heuristic_result.dat')
            for line in instream:
                line = line.strip()
                if not '--' in line:
                    if self.h_value == 'n/a':
                        self.h_value = float(line)
                        # print("value for %s is %d\n"%(self.problem,self.h_value))
                    else: # Gather operator counts
                        operator,count = line.split('=')
                        self.op_counts[operator.strip()] = float(count.strip())
            instream.close()

    def write_result(self, filename):
        res = csv.writer(open('%s' % filename, 'w'))
        res.writerow([os.path.basename(self.domain), os.path.basename(self.problem), self.signal, self.time,
                      self.num_accounted_obs])

class PRCommandConstraints(PRCommand):

    def __init__(self, domain, problem, max_time=120, max_mem=2048):
        PRCommand.__init__(self,domain,problem,max_time,max_mem)
        self.planner_string = fd_path + '/fast-downward %s %s --translate-options --add-implied-preconditions --keep-unimportant-variables --keep-unreachable-facts --search-options --search \"astar(ocsingleshot([lmcut_constraints(), pho_constraints(), state_equation_constraints()],enforce_observations=true, soft_constraints=false))\"'

class PRCommandSoft(PRCommand):

    def __init__(self, domain, problem, max_time=120, max_mem=2048):
        PRCommand.__init__(self,domain,problem,max_time,max_mem)
        self.planner_string = fd_path + '/fast-downward %s %s --translate-options --add-implied-preconditions --keep-unimportant-variables --keep-unreachable-facts --search-options --search \"astar(ocsingleshot([lmcut_constraints(), pho_constraints(), state_equation_constraints()],enforce_observations=false, soft_constraints=true))\"'

class Hypothesis:

    def __init__(self, constraints = False, soft_constraints = False):
        self.atoms = []
        self.Delta = 0.0
        self.plan = []
        self.is_true = True
        self.test_failed = False

        self.plan_time = 0
        self.total_time = 0

        self.score = None
        self.obs_hits = None
        self.obs_misses = None
        self.enforce_constraints = constraints
        self.soft_constraints = soft_constraints


    def evaluate(self, index, observations):
        # generate the problem with G=H
        hyp_problem = 'hyp_%d_problem.pddl' % index
        self.generate_pddl_for_hyp_plan(hyp_problem)
        if self.enforce_constraints:
            pr_cmd = PRCommandConstraints('domain.pddl', 'hyp_%d_problem.pddl' % index)
        elif self.soft_constraints:
            pr_cmd = PRCommandSoft('domain.pddl', 'hyp_%d_problem.pddl' % index)
        else:
            pr_cmd = PRCommand('domain.pddl', 'hyp_%d_problem.pddl' % index)
        pr_cmd.execute()
        self.plan_time = pr_cmd.time
        self.total_time = pr_cmd.time
        pr_cmd.write_result('hyp_%d_planning_H.csv' % index)

        if pr_cmd.signal == 0:
            # self.score = float( plan_for_H_cmd.num_obs_accounted)
            # self.load_plan( 'pr-problem-hyp-%d.soln'%index )
            self.obs_hits, self.obs_misses = observations.compute_count_intersection(pr_cmd.op_counts)
            # print("Hits=%d Misses=%d"%(self.obs_hits, self.obs_misses))
            self.score = float(pr_cmd.h_value)

            # self.score = float(hits)/float(hits+misses)
        else:
            self.test_failed = True

    def load_plan(self, plan_name):
        instream = open(plan_name)
        self.plan = []
        for line in instream:
            line = line.strip()
            if line[0] == ';': continue
            # _, _, stuff = line.partition(':')
            # op, _, _ = stuff.partition('[')
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

class Observations:

    def __init__(self, obs):
        self.observations = []
        instream = open(obs)
        for line in instream:
            self.observations.append(line.strip().lower())

    def __len__(self):
        return len(self.observations)

    def compute_count_intersection(self, opcounts):
        counts = dict(opcounts)
        hitcount = 0
        misscount = 0
        for obs in self.observations:
            if obs in counts.keys():
                if counts[obs] > 0:
                    hitcount +=1
                    counts[obs]-=1
                else:
                    misscount +=1
            else:
                misscount+=1
        misscount += sum([v for v in counts.values()])
        return hitcount,misscount