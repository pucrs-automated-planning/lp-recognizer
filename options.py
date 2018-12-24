import getopt, os, sys


def usage():
    print >> sys.stderr, "Parameters:"
    print >> sys.stderr, "-e  --experiment <file>          Plan Recognition experiment files (tar'ed)"
    print >> sys.stderr, "-h  --help                       Get Help"
    print >> sys.stderr, "-t  --max-time <time>            Maximum allowed execution time (defaults to 1800 secs)"
    print >> sys.stderr, "-m  --max-memory <time>          Maximum allowed memory consumption (defaults to 1Gb)"
    print >> sys.stderr, "-s  --simple                     Simple inference (max. #obs accounted in relaxed plan)"
    print >> sys.stderr, "-B  --bfs                        Bypass EHC search and solve the problem by Greedy Best First Search"


class Program_Options:

    def __init__(self, args):
        try:
            opts, args = getopt.getopt(args,
                                       "e:ht:m:sB",
                                       ["experiment=",
                                        "help",
                                        "max-time=",
                                        "max-memory=",
                                        "simple",
                                        "bfs"])
        except getopt.GetoptError:
            print >> sys.stderr, "Missing or incorrect parameters specified!"
            usage()
            sys.exit(1)

        self.exp_file = None
        self.domain_name = None
        self.instance_names = []
        self.goal_file = None
        self.max_time = 1800
        self.max_memory = 1024
        self.simple_pr = False
        self.bfs = False
        for opcode, oparg in opts:
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
            if opcode in ('-s', '--simple'):
                self.simple_pr = True
            if opcode in ('-B', '--bfs'):
                self.bfs = True

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
