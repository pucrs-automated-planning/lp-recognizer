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
                                       "r:be:ht:m:T:F:H:",
                                       ["recognizer-name=",
                                        "batch",
                                        "experiment=",
                                        "help",
                                        "max-time=",
                                        "max-memory=",
                                        "theta=",
                                        "filter=",
                                        "heuristics="])
        except getopt.GetoptError:
            print("Missing or incorrect parameters specified!", file=sys.stderr)
            usage()
            sys.exit(1)

        self.batch = False
        self.exp_file = None
        self.domain_name = None
        self.instance_names = []
        self.goal_file = None
        self.max_time = 1800
        self.hyp_max_time = 120
        self.max_memory = 1024
        self.recognizer_name = None
        self.theta = 1 # Multiplier for any slack parameter
        self.filter = 0 # Obs filter
        self.weight = 3
        self.heuristics = ["lmcut_constraints()", "pho_constraints()", "state_equation_constraints()"]

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

            if opcode in ('-r', '--recognizer-name'):
                if oparg == 'v':
                    self.recognizer_name = "h-value"
                elif oparg == 'c':
                    self.recognizer_name = "h-value-c"
                elif oparg == 's':
                    self.recognizer_name = "soft-c"
                elif oparg == 'dc':
                    self.recognizer_name = "delta-h-c"
                elif oparg == 'dc-f1':
                    self.recognizer_name = "delta-h-c-f1"
                elif oparg == 'dc-f2':
                    self.recognizer_name = "delta-h-c-f2"
                elif oparg == 'w':
                    self.recognizer_name = "weighted-c"
                elif oparg == 'wdc':
                    self.recognizer_name = "weighted-delta-h-c"
                elif oparg == 'dcu':
                    self.recognizer_name = "delta-h-c-uncertainty"
                elif oparg == 'dcu-f1':
                    self.recognizer_name = "delta-h-c-f1-uncertainty"
                elif oparg == 'dcu-f2':
                    self.recognizer_name = "delta-h-c-f2-uncertainty"
                elif oparg == 'wu':
                    self.recognizer_name = "weighted-c-uncertainty"
                elif oparg == 'wdcu':
                    self.recognizer_name = "weighted-delta-h-c-uncertainty"
                else:
                    self.recognizer_name = oparg

        # TODO Code below is currently useless because we set parameters manually in run experimennts (need to thoroughly clean this up)
        if self.batch:
            print("Not checking other files", file=sys.stderr)
            return

        if self.exp_file is None:
            print("No experiment file was specified!!", file=sys.stderr)
            usage()
            sys.exit(1)

        os.system('tar jxvf %s' % self.exp_file)
        if not os.path.exists('domain.pddl'):
            os.system('tar -jxvf %s' % self.exp_file + ' --strip-components 1')
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
