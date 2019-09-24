#!/usr/bin/env python2.7

from plan_recognizer import PlanRecognizer
import plan_recognition
# XXX My implementation of the factory relies on all recognizer classes having been imported into the plan_recognition module
from plan_recognition import LPRecognizerDeltaHC, LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerSoftCUncertainty, LPRecognizerHValueCUncertainty, LPRecognizerDeltaHCUncertainty, LPRecognizerDeltaHS, LPRecognizerDeltaHSUncertainty, Program_Options 
import const_plan_recognizer
import delta_plan_recognizer

import importlib

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

    def __init__(self, options):
        self.options = options

    
    def get_recognizer(self, name, options=None):
        """Returns an instance of PlanRecognizer given the name used in the parameters"""
        # From https://stackoverflow.com/questions/7584418/iterate-the-classes-defined-in-a-module-imported-dynamically
        # to create a dict that maps the names to the classes
        # dict([(name, cls) for name, cls in mod.__dict__.items() if isinstance(cls, type)])
        if options == None:
            options = self.options

        # Finding the objects 
        recognizers = dict([(cls.name, cls) for name, cls in plan_recognition.__dict__.items() if isinstance(cls,type) and issubclass(cls, PlanRecognizer)])
        # print(recognizers)
        recognizer = recognizers[name](options)

        return recognizer


