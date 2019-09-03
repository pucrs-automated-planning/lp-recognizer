import getopt, os, sys


def usage():
    print >> sys.stderr, "Parameters:"
    print >> sys.stderr, "-e  --experiment <file>          Plan Recognition experiment files (tar'ed)"
    print >> sys.stderr, "-h  --help                       Get Help"
    print >> sys.stderr, "-t  --max-time <time>            Maximum allowed execution time (defaults to 1800 secs)"
    print >> sys.stderr, "-m  --max-memory <time>          Maximum allowed memory consumption (defaults to 1Gb)"
    print >> sys.stderr, "-v  --hvalue                     Plan recognition by h-value"
    print >> sys.stderr, "-c  --h-value-c                  Plan recognition by h-value with enforced constraints derived from the observations"
    print >> sys.stderr, "-s  --soft-c                     Plan recognition with soft constraints"    
    print >> sys.stderr, "-d  --delta-h-c                  Plan recognition by delta between h-value-c and h-value"
    print >> sys.stderr, "-f  --delta-h-s                  Plan recognition by delta between h-value-c and soft-c"
    print >> sys.stderr, "-u  --h-value-c-uncertainty      Plan recognition with soft constraints accounting for missing observations"    
    print >> sys.stderr, "-n  --delta-h-c-uncertainty      Plan recognition with delta h-c accounting for missing observations"
    print >> sys.stderr, "-k  --delta-h-s-uncertainty      Plan recognition with delta h-s accounting for missing observations"

class Program_Options:

    def __init__(self, args):
        try:
            opts, args = getopt.getopt(args,
                                       "be:ht:m:T:vcrsdfunk",
                                       ["batch",
                                        "experiment=",
                                        "help",
                                        "max-time=",
                                        "max-memory=",
                                        "theta=",
                                        "h-value",
                                        "h-value-c",
                                        "delta-h-c",
                                        "delta-h-s",
                                        "soft-c",
                                        "h-value-c-uncertainty",
                                        "delta-h-c-uncertainty",
                                        "delta-h-s-uncertainty"])
        except getopt.GetoptError:
            print >> sys.stderr, "Missing or incorrect parameters specified!"
            usage()
            sys.exit(1)

        self.batch = False
        self.exp_file = None
        self.domain_name = None
        self.instance_names = []
        self.goal_file = None
        self.max_time = 1800
        self.max_memory = 1024
        self.h_value = False
        self.h_value_c = False
        self.delta_h_c  = False
        self.delta_h_s  = False
        self.soft_c = False
        self.h_value_c_uncertainty = False
        self.delta_h_c_uncertainty = False
        self.delta_h_s_uncertainty = False
        self.theta = 1 # Multiplier for any slack parameter 

        for opcode, oparg in opts:
            if opcode in ('-b', '--batch'):
                print >> sys.stderr, "Running batch experiments!"
                self.batch = True
            if opcode in ('-h', '--help'):
                print >> sys.stderr, "Help invoked!"
                usage()
                sys.exit(0)
            if opcode in ('-e', '--experiment'):
                self.exp_file = oparg
                if not os.path.exists(self.exp_file):
                    print >> sys.stderr, "File", self.exp_file, "does not exist"
                    print >> sys.stderr, "Aborting"
                    sys.exit(1)
            if opcode in ('-t', '--max-time'):
                try:
                    self.max_time = int(oparg)
                    if self.max_time <= 0:
                        print >> sys.stderr, "Maximum time must be greater than zero"
                        sys.exit(1)
                except ValueError:
                    print >> sys.stderr, "Time must be an integer"
                    sys.exit(1)
            if opcode in ('-m', '--max-memory'):
                try:
                    self.max_memory = int(oparg)
                    if self.max_memory <= 0:
                        print >> sys.stderr, "Maximum memory must be greater than zero"
                        sys.exit(1)
                except ValueError:
                    print >> sys.stderr, "Memory amount must be an integer"
                    sys.exit(1)
            if opcode in ('-T', '--theta'):
                try:
                    self.theta = float(oparg)
                    if self.theta <= 0:
                        print >> sys.stderr, "Theta parameter must be greater than zero"
                        sys.exit(1)
                except ValueError:
                    print >> sys.stderr, "Theta value must be a number"
                    sys.exit(1)
            if opcode in ('-v', '--hvalue'):
                self.h_value = True
            if opcode in ('-c', '--h-value-c'):
                self.h_value_c = True
            if opcode in ('-s', '--soft-c '):
                self.soft_c = True
            if opcode in ('-d', '--delta-h-c'):
                self.delta_h_c  = True
            if opcode in ('-f', '--delta-h-s'):
                self.delta_h_s  = True
            if opcode in ('-u', '--h-value-c-uncertainty '):
                self.h_value_c_uncertainty = True
            if opcode in ('-n', '--delta-h-c-uncertainty'):
                self.delta_h_c_uncertainty = True
            if opcode in ('-k', '--delta-h-s-uncertainty'):
                self.delta_h_s_uncertainty = True

        # TODO Code below is currently useless because we set parameters manually in run experimennts (need to thoroughly clean this up)
        if self.batch:
            print >> sys.stderr, "Not checking other files"
            return
        
        if self.exp_file is None:
            print >> sys.stderr, "No experiment file was specified!!"
            usage()
            sys.exit(1)

        os.system('tar jxvf %s' % self.exp_file)
        if not os.path.exists('domain.pddl'):
            os.system('tar -jxvf %s' % self.exp_file + ' --strip-components 1')
            if not os.path.exists('domain.pddl'):
                print >> sys.stderr, "No 'domain.pddl' file found in experiment file!"
                usage()
                sys.exit(1)
        if not os.path.exists('template.pddl'):
            print >> sys.stderr, "No 'template.pddl' file found in experiment file!"
            usage()
            sys.exit(1)
        if not os.path.exists('hyps.dat'):
            print >> sys.stderr, "No 'hyps.dat' file found in experiment file!"
            usage()
            sys.exit(1)
        if not os.path.exists('obs.dat'):
            print >> sys.stderr, "No 'obs.dat' file found in experiment file!"
            usage()
            sys.exit(1)
        if not os.path.exists('real_hyp.dat'):
            print >> sys.stderr, "No 'real_hyp.dat' file found in experiment file!"
            usage()
            sys.exit(1)

    def print_options(self):
        def print_yes(): print >> sys.stdout, "Yes"

        def print_no(): print >> sys.stdout, "No"

        print >> sys.stdout, "Options set"
        print >> sys.stdout, "==========="
        print >> sys.stdout, "Experiment File:", self.exp_file
        print >> sys.stdout, "Max. Time Allowed", self.max_time
        print >> sys.stdout, "Max. Memory Allowed", self.max_memory
