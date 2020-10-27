#!/usr/bin/env python2.7

import h_plan_recognizer
import const_plan_recognizer
import delta_plan_recognizer

import importlib
import copy

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

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
        h_recognizers.update(const_recognizers)
        h_recognizers.update(delta_recognizers)
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
            if arg[0] == 'f':
                options.filter = int(arg[1:])
            elif arg[0] == 'o':
                options.h_obs = True
            elif arg[0] == 'c':
                options.heuristics = []
                if 'l' in arg:
                    options.heuristics.append("lmcut_constraints()")
                if 'p' in arg:
                    options.heuristics.append("pho_constraints()")
                if 's' in arg:
                    options.heuristics.append("state_equation_constraints()")
                if 'd' in arg:
                    options.heuristics.append("delete_relaxation_constraints()")
                if 'f1' in arg:
                    options.heuristics.append("flow_constraints(systematic(1))")
                if 'f2' in arg:
                    options.heuristics.append("flow_constraints(systematic(2))")
                if 'f3' in arg:
                    options.heuristics.append("flow_constraints(systematic(3))")
            else:
                print("Recognizer option unknown: " + arg)
                exit()

        recognizer = self.recognizers[name](options)
        return recognizer
