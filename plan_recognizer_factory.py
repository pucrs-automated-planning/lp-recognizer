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

    def get_recognizer(self, name, options=None):
        """Returns an instance of PlanRecognizer given the name used in the parameters"""
        if options == None:
            options = copy.copy(self.options)

        # Filter options
        if "-f1" in name:
            name = name.replace("-f1", "")
            options.filter = 1
        elif "-f2" in name:
            name = name.replace("-f2", "")
            options.filter = 2

        # Observation constraints
        if "-o" in name:
            name = name.replace("-o", "")
            options.h_obs = True

        # Heuristic options
        if "-clpsd" in name:
            name = name.replace("-clpsd", "")
            options.heuristics = ["lmcut_constraints()", "pho_constraints()", "state_equation_constraints()", "delete_relaxation_constraints()"]
        elif "-cps" in name:
            name = name.replace("-cps", "")
            options.heuristics = ["pho_constraints()", "state_equation_constraints()"]
        elif "-cls" in name:
            name = name.replace("-cls", "")
            options.heuristics = ["lmcut_constraints()", "state_equation_constraints()"]
        elif "-clp" in name:
            name = name.replace("-clp", "")
            options.heuristics = ["lmcut_constraints()", "pho_constraints()"]
        elif "-cl" in name:
            name = name.replace("-cl", "")
            options.heuristics = ["lmcut_constraints()"]
        elif "-cp" in name:
            name = name.replace("-cp", "")
            options.heuristics = ["pho_constraints()"]
        elif "-cs" in name:
            name = name.replace("-cs", "")
            options.heuristics = ["state_equation_constraints()"]
        elif "-cd" in name:
            name = name.replace("-cd", "")
            options.heuristics = ["delete_relaxation_constraints()"]


        recognizer = self.recognizers[name](options)
        return recognizer
