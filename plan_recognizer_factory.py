#!/usr/bin/env python3

import h_plan_recognizer
import const_plan_recognizer
import delta_plan_recognizer
import div_plan_recognizer

import importlib
import copy

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def parse_constraints(arg):
    heuristics = []
    i = 1
    while i < len(arg):
        if arg[i] == 'l':
            n = 0 # Noisy
            if len(arg) > i+1 and arg[i+1].isdigit():
                i += 1
                n = int(arg[i])
            h = "lmcut_constraints(%s)" % n
        if arg[i] == 'p':
            h = "pho_constraints()"
        if arg[i] == 's':
            h = "state_equation_constraints()"
        if arg[i] == 'd':
            # Use time variables
            time_vars = False
            if len(arg) > i+1 and arg[i+1] == 't':
                i += 1
                time_vars = True
            # Noise filter
            noisy = 0
            if len(arg) > i+1 and arg[i+1] == 'a': # Soft for all + inv (D4)
                i += 1
                noisy = 3
            if len(arg) > i+1 and arg[i+1] == 'b': # Soft for obs only + inv (D3)
                i += 1
                noisy = 2
            elif len(arg) > i+1 and arg[i+1] == 'o': # Soft for obs only (D2)
                i += 1
                noisy = 1
            # MIP vars
            param = 0
            if len(arg) > i+1 and arg[i+1].isdigit():
                i += 1
                param = arg[i]
            if param == '1': # use_integer_vars_op 
                h = "delete_relaxation_constraints(%s, 1, 0, 0, 0, 0, %s)" % (time_vars, noisy)
            elif param == '2': # use_integer_vars_facts
                h = "delete_relaxation_constraints(%s, 0, 0, 1, 0, 0, %s)" % (time_vars, noisy)
            elif param == '3': # use_integer_vars_achiever
                h = "delete_relaxation_constraints(%s, 0, 0, 0, 1, 0, %s)" % (time_vars, noisy)
            elif param == '4': # use_integer_vars_time
                h = "delete_relaxation_constraints(%s, 0, 0, 0, 0, 1, %s)" % (time_vars, noisy)
            elif param == '5': # use_integer_vars_op (obs only)
                h = "delete_relaxation_constraints(%s, 2, 0, 0, 0, 0, %s)" % (time_vars, noisy)
            elif param == '6': # use_integer_vars_op2
                h = "delete_relaxation_constraints(%s, 0, 1, 0, 0, 0, %s)" % (time_vars, noisy)
            elif param == '7': # all integer
                h = "delete_relaxation_constraints(%s, 1, 1, 1, 1, 1, %s)" % (time_vars, noisy)
            else: # use all integer_vars
                h = "delete_relaxation_constraints(%s, 0, 0, 0, 0, 0, %s)" % (time_vars, noisy)
        if arg[i] == 'f':
            i += 1
            # Systematic patterns size
            s = arg[i]
            # Naive systematic
            n = False
            if len(arg) > i+1 and arg[i+1] == 'n':
                i += 1
                n = True
            # Partial merge type
            p = 0
            if len(arg) > i+1 and arg[i+1] == 'f':
                i += 1
                p = 2
            # Goal variables only
            g = False
            if len(arg) > i+1 and arg[i+1] == 'g':
                i += 1
                g = True
            # Partial merges parameters
            m = True
            if len(arg) > i+1 and arg[i+1].isdigit():
                i += 1
                # 0 -> no merges, 1 -> merges within operator, 2 -> merges inter-operators
                if arg[i] == '0': # Preconditions + effects
                    param = ", merge_preconditions=2, merge_effects=2"
                    m = False
                elif arg[i] == '1': # Preconditions
                    param = ", merge_preconditions=2, merge_effects=0"
                    m = False
                elif arg[i] == '2': # Effects
                    param = ", merge_preconditions=0, merge_effects=2"
                    m = False
                elif arg[i] == '3': # Preconditions + effects (intra)
                    param = ", merge_preconditions=1, merge_effects=1"
                    m = False
                elif arg[i] == '4': # Preconditions (intra)
                    param = ", merge_preconditions=1, merge_effects=0"
                    m = False
                elif arg[i] == '5': # Effects (intra)
                    param = ", merge_preconditions=0, merge_effects=1"
                    m = False
                elif arg[i] == '6': # Preconditions x effects
                    param = ", merge_preconditions=4, merge_effects=0"
                    m = False
                elif arg[i] == '7': # Preconditions x effects (intra)
                    param = ", merge_preconditions=3, merge_effects=0"
                    m = False
                else:
                    param = ", merge_preconditions=2, merge_effects=2"
                    m = False
                if len(arg) > i+1 and arg[i+1] >= 'a' and arg[i+1] <= 'd':
                    i += 1
                    if arg[i] == 'a':
                        param += ", max_merge_feature_size=3"
                    else:
                        param += ", max_merge_feature_size=4"
            # Old partial merges
            elif len(arg) > i+1 and arg[i+1] >= 'a' and arg[i+1] <= 'd':
                i += 1
                if arg[i] == 'a':
                    param = ", max_merge_feature_size=2"
                elif arg[i] == 'b':
                    param = ", max_merge_feature_size=4"
                elif arg[i] == 'c':
                    param = ", max_merge_feature_size=8"
                else:
                    param = ", max_merge_feature_size=16"
                if len(arg) > i+1 and arg[i+1] >= 'a' and arg[i+1] <= 'b':
                    i += 1
                    if arg[i] == 'a':
                        param += ", partial_merge_time_limit=10"
                p = 1
            else:
                param = ""
            m = True
            param = "self_loop_optimization=false, use_mutexes=%s, partial_merges=%s, merge_goal_only=%s" % (m, p, g) + param
            h = "flow_constraints(systematic(%s, only_interesting_patterns=%s), %s)" % (s, not n, param)
        print(h)
        heuristics.append(h)
        i += 1
    return heuristics

# Comment this out for Python 3
# class PlanRecognizerFactory(metaclass=Singleton):
class PlanRecognizerFactory(object):
    __metaclass__ = Singleton

    def __init__(self, options=None):
        self.options = options
        self.recognizers = self.get_recognizers()

    def get_recognizers(self):
        # From https://stackoverflow.com/questions/7584418/iterate-the-classes-defined-in-a-module-imported-dynamically
        # to create a dict that maps the names to the classes
        # dict([(name, cls) for name, cls in mod.__dict__.items() if isinstance(cls, type)])
        h_recognizers = dict([(cls.name, cls) for name, cls in h_plan_recognizer.__dict__.items() if isinstance(cls,object) and hasattr(cls,'name')])
        const_recognizers = dict([(cls.name, cls) for name, cls in const_plan_recognizer.__dict__.items() if isinstance(cls,object) and hasattr(cls,'name')])
        delta_recognizers = dict([(cls.name, cls) for name, cls in delta_plan_recognizer.__dict__.items() if isinstance(cls,object) and hasattr(cls,'name')])
        div_recognizers = dict([(cls.name, cls) for name, cls in div_plan_recognizer.__dict__.items() if isinstance(cls,object) and hasattr(cls,'name')])
        h_recognizers.update(const_recognizers)
        h_recognizers.update(delta_recognizers)
        h_recognizers.update(div_recognizers)
        return h_recognizers

    def get_recognizer_names(self):
        recognizers = self.get_recognizers()
        return list(recognizers.keys())


    def get_recognizer(self, fullname, options=None):
        """Returns an instance of PlanRecognizer given the name used in the parameters"""
        if options == None:
            options = copy.copy(self.options)

        args = fullname.split("-")
        name = args[0]

        for arg in args[1:]:
            if arg[0] == 'i':
                options.mip = True
            elif arg[0] == 'f':
                options.filter = int(arg[1:])
            elif arg[0] == 'o':
                if len(arg) == 1:
                    options.h_obs = 1
                else:
                    options.h_obs = int(arg[1:]) + 1
            elif arg[0] == 'c':
                options.heuristics = parse_constraints(arg)
            else:
                print("Recognizer option unknown: " + arg)
                exit()

        recognizer = self.recognizers[name](options)
        return recognizer
