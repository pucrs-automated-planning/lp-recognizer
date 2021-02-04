from __future__ import print_function
import getopt, os, sys

def usage():
    print("Parameters:", file=sys.stderr)
    print("-e  --experiment <file>          Plan Recognition experiment files (tar'ed)", file=sys.stderr)
    print("-h  --help                       Get Help", file=sys.stderr)
    print("-t  --max-time <time>            Maximum allowed execution time (defaults to 1800 secs)", file=sys.stderr)
    print("-m  --max-memory <time>          Maximum allowed memory consumption (defaults to 1Gb)", file=sys.stderr)
    print("-H  --heuristics                 Fast Downward search heuristics as a comma-separated string:\nExample: -H lmcut_constraints(), pho_constraints(), state_equation_constraints()", file=sys.stderr)
    print("-r  --recognizer-name            Plan recognition name", file=sys.stderr)
class Program_Options:

    def __init__(self, args):
        try:
            opts, args = getopt.getopt(args,
                                       "r:be:ht:m:T:F:H:oS:i",
                                       ["recognizer-name=",
                                        "batch",
                                        "experiment=",
                                        "help",
                                        "max-time=",
                                        "max-memory=",
                                        "theta=",
                                        "filter=",
                                        "heuristics=",
                                        "h-obs",
                                        "solver=",
                                        "mip"])
        except getopt.GetoptError:
            print("Missing or incorrect parameters specified!", file=sys.stderr)
            usage()
            sys.exit(1)

        self.batch = False
        self.exp_file = None
        self.domain_name = None
        self.instance_names = []
        self.goal_file = None
        self.max_time = 120
        self.hyp_max_time = 10
        self.max_memory = 1024
        self.recognizer_name = None
        self.theta = 1 # Multiplier for any slack parameter
        self.filter = 0 # Obs filter
        self.weight = 3
        self.heuristics = ["lmcut_constraints()", "pho_constraints()", "state_equation_constraints()"]
        self.h_obs = 0
        self.solver = "soplex"
        self.mip = False

        for opcode, oparg in opts:
            if opcode in ('-b', '--batch'):
                print("Running batch experiments!", file=sys.stderr)
                self.batch = True
            if opcode in ('-h', '--help'):
                print("Help invoked!", file=sys.stderr)
                usage()
                sys.exit(0)
            if opcode in ('-e', '--experiment'):
                self.exp_file = oparg
                if not os.path.exists(self.exp_file):
                    print("File", self.exp_file, "does not exist", file=sys.stderr)
                    print("Aborting", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-t', '--max-time'):
                try:
                    self.max_time = int(oparg)
                    if self.max_time <= 0:
                        print("Maximum time must be greater than zero", file=sys.stderr)
                        sys.exit(1)
                except ValueError:
                    print("Time must be an integer", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-m', '--max-memory'):
                try:
                    self.max_memory = int(oparg)
                    if self.max_memory <= 0:
                        print("Maximum memory must be greater than zero", file=sys.stderr)
                        sys.exit(1)
                except ValueError:
                    print("Memory amount must be an integer", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-T', '--theta'):
                try:
                    self.theta = float(oparg)
                    if self.theta <= 0:
                        print("Theta parameter must be greater than zero", file=sys.stderr)
                        sys.exit(1)
                except ValueError:
                    print("Theta value must be a number", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-W', '--weighted'):
                print("Using weighted observations!", file=sys.stderr)
                self.weight_obs = True
            if opcode in ('-F', '--filter'):
                try:
                    self.filter = int(oparg)
                    if self.filter < 0:
                        print("Filter parameter must be at least zero", file=sys.stderr)
                        sys.exit(1)
                except ValueError:
                    print("Filter value must be an integer", file=sys.stderr)
                    sys.exit(1)
            if opcode in ('-H', '--heuristics'):
                self.heuristics = list(oparg.split(","))
                print("LIST OF HEURISTICS: "+oparg)
                print(self.heuristics)
            if opcode in ('-o', '--h-obs'):
                self.h_obs = 1
                print("Enable observations inside heuristic constraints!")
            if opcode in ('-S', '--solver'):
                self.solver = oparg
                print("Using LP solver: " + oparg)
            if opcode in ('-i', '--mip'):
                self.mip = True

            if opcode in ('-r', '--recognizer-name'):
                self.recognizer_name = oparg
                print("Using recognizer: " + oparg)


        # TODO Code below is currently useless because we set parameters manually in run experimennts (need to thoroughly clean this up)
        if self.batch:
            print("Not checking other files", file=sys.stderr)
            return

        if self.exp_file:
            self.extract_exp_file()


    def extract_exp_file(self, exp_file=None):
        if not exp_file:
            exp_file = self.exp_file
        print(exp_file)
        os.system('tar jxvf %s' % exp_file)
        if not os.path.exists('domain.pddl'):
            os.system('tar -jxvf %s' % exp_file + ' --strip-components 1')
            if not os.path.exists('domain.pddl'):
                print("No 'domain.pddl' file found in experiment file!", file=sys.stderr)
                usage()
                sys.exit(1)
        if not os.path.exists('template.pddl'):
            print("No 'template.pddl' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)
        if not os.path.exists('hyps.dat'):
            print("No 'hyps.dat' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)
        if not os.path.exists('obs.dat'):
            print("No 'obs.dat' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)
        if not os.path.exists('real_hyp.dat'):
            print("No 'real_hyp.dat' file found in experiment file!", file=sys.stderr)
            usage()
            sys.exit(1)
        solution_file = exp_file.replace("tar.bz2", "solution")
        if os.path.exists(solution_file):
            os.system("cp %s solution.dat" % solution_file)
        else:
            if "noisy" in exp_file:
                solution_file_original = solution_file.replace("-noisy_0.2", "").replace("-noisy", "").replace("-old", "").replace("_noisy", "")
                solution_file_original = solution_file_original.replace("full_1", "full").replace("full_2", "full").replace("full_3", "full")
                if os.path.exists(solution_file_original):
                    os.system("cp %s solution.dat" % solution_file_original)
                else:
                    print("No solution file: %s" % solution_file)
                    print("No solution file: %s" % solution_file_original)
                    os.system("cp real_hyp.dat solution.dat")
            else:
                print("No solution file: %s" % solution_file)
                os.system("cp real_hyp.dat solution.dat")


    def print_options(self):
        def print_yes(): 
            print("Yes", file=sys.stdout)
        def print_no():
            print("No", file=sys.stdout)

        print("Options set", file=sys.stdout)
        print("===========", file=sys.stdout)
        print("Experiment File:", self.exp_file, file=sys.stdout)
        print("Max. Time Allowed", self.max_time, file=sys.stdout)
        print("Max. Memory Allowed", self.max_memory, file=sys.stdout)
