#!/usr/bin/env python2

# Code originally developed by Miquel Ramirez
import sys, os, csv, time
from options import Program_Options
import benchmark
from operator import attrgetter

fd_path = "../fast-downward/"


def custom_partition(s, sep):
    i = 0
    while i < len(s):
        if s[i] == sep: break
        i = i + 1
    if i == len(s): return (None, None, None)
    if i == 0: return (None, s[i], s[i + 1:])
    return (s[:i - 1], s[i], s[i + 1:])


class PR_Command:

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
        self.planner_string = fd_path + '/fast-downward %s %s --search \"astar(ocsingleshot([lmcut_constraints(), pho_constraints(), state_equation_constraints()],enforce_observations=false))\"'

    def execute(self):
        cmd_string = self.planner_string % (self.domain, self.problem)
        self.log = benchmark.Log('%s.log' % self.noext_problem)
        self.signal, self.time = benchmark.run(cmd_string, self.max_time, self.max_mem, self.log)
        self.gather_data()

    def gather_data(self):

        if self.signal == 0 and os.path.exists('h_result.txt'):
            instream = open('h_result.txt')
            for line in instream:
                line = line.strip()
                if not '--' in line:
                    if self.h_value == 'n/a':
                        # self.num_obs_accounted = int(line)
                        self.h_value = float(line)
                        print("h_value for %s is %d"%(self.problem,self.h_value))
                    else: # Gather operator counts
                        operator,count = line.split('=')
                        self.op_counts[operator.strip()] = float(count.strip())
            # print("Opcounts: ",self.op_counts)
            instream.close()

    def write_result(self, filename):
        res = csv.writer(open('%s' % filename, 'w'))
        res.writerow([os.path.basename(self.domain), os.path.basename(self.problem), self.signal, self.time,
                      self.num_accounted_obs])


class Hypothesis:

    def __init__(self):
        self.atoms = []
        self.Delta = 0.0
        self.plan = []
        self.is_true = True
        self.test_failed = False

    def evaluate(self, index, observations):
        # generate the problem with G=H
        hyp_problem = 'hyp_%d_problem.pddl' % index
        self.generate_pddl_for_hyp_plan(hyp_problem)
        pr_cmd = PR_Command('domain.pddl', 'hyp_%d_problem.pddl' % index)
        pr_cmd.execute()
        self.plan_time = pr_cmd.time
        self.total_time = pr_cmd.time
        pr_cmd.write_result('hyp_%d_planning_H.csv' % index)

        if pr_cmd.signal == 0:
            # self.score = float( plan_for_H_cmd.num_obs_accounted)
            # self.load_plan( 'pr-problem-hyp-%d.soln'%index )
            hits, misses = observations.compute_count_intersection(pr_cmd.op_counts)
            # self.score = float(pr_cmd.h_value)
            # self.score = int(pr_cmd.h_value)
            self.score = hits
            self.hits = hits
            self.misses = misses
            # self.score = float(hits)/float(hits+misses)
            print("Opcounts: hits=%d misses=%d"%(hits,misses))
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


class Observations:

    def __init__(self, obs):
        self.observations = []
        instream = open(obs)
        for line in instream:
            self.observations.append(line.strip().lower())

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

class PlanRecognizer:
    
    def __init__(self, options):
        self.options = options
        self.observations = Observations('obs.dat')
        self.hyps = self.load_hypotheses()

    def load_hypotheses(self):
        hyps = []

        instream = open('hyps.dat')

        for line in instream:
            line = line.strip()
            H = Hypothesis()
            H.atoms = [tok.strip() for tok in line.split(',')]
            H.check_if_actual()
            hyps.append(H)

        instream.close()

        return hyps

    def get_real_hypothesis(self):
        for h in self.hyps:
            if h.is_true:
                realHyp = h
                return realHyp

    def write_report(self, experiment, hyps):
        outstream = open('report.txt', 'w')

        print >> outstream, "Experiment=%s" % experiment
        print >> outstream, "Num_Hyp=%d" % len(hyps)
        for hyp in hyps:
            print >> outstream, "Hyp_Atoms=%s" % ",".join(hyp.atoms)
            if hyp.test_failed:
                print >> outstream, "Hyp_Score=unknown"
                print >> outstream, "Hyp_Plan_Len=unknown"
            else:
                print >> outstream, "Hyp_Score=%f" % hyp.score
                print >> outstream, "Hyp_Plan_Len=%d" % len(hyp.plan)
            print >> outstream, "Hyp_Trans_Time=%f" % hyp.trans_time
            print >> outstream, "Hyp_Plan_Time=%f" % hyp.plan_time
            print >> outstream, "Hyp_Test_Time=%f" % hyp.total_time
            print >> outstream, "Hyp_Is_True=%s" % hyp.is_true

        outstream.close()
        print(max(hyps))

    def run_recognizer(self):
        return None


class LPRecognizer(PlanRecognizer):

    def __init__(self, options):
        PlanRecognizer.__init__(self,options)

    def run_recognizer(self):
        for i in range(0, len(self.hyps)):
            self.hyps[i].evaluate(i, self.observations)

        hyp = None
        for h in self.hyps:
            if not h.test_failed:
                if not hyp or h.score > hyp.score:
                    hyp = h
                    
        return hyp
        
    def print_scores(self):
        i = 0
        for h in self.hyps:
            if not h.test_failed:
                print("h_%s=%f%s"%(i,h.score,"*" if h.is_true else ""))
            else:
                print("h_%s=failed"%(i))
            i+=1

def main():
    cmdClean = 'rm -rf *.pddl *.dat *.log *.soln *.csv report.txt h_result.txt results.tar.bz2'
    os.system(cmdClean)

    startTime = time.time()
    print(sys.argv)
    options = Program_Options(sys.argv[1:])

    recognizer = LPRecognizer(options)
    hyp = recognizer.run_recognizer()

    # write_report(options.exp_file, hyps)

    # cmd = 'tar jcvf results.tar.bz2 *.log *.csv *.pddl *.soln report.txt'
    # os.system( cmd )

    realHyp = recognizer.get_real_hypothesis()

    # recognizer.print_scores()
    if hyp and realHyp and hyp.score == realHyp.score:
        print('TRUE!')
    else:
        print('FALSE!')

    print("--- %s seconds ---" % (time.time() - startTime))


if __name__ == '__main__':
    main()
