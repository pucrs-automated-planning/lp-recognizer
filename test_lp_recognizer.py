import unittest

from plan_recognizer_factory import PlanRecognizerFactory, LPRecognizerDeltaHC, LPRecognizerHValue, LPRecognizerHValueC, LPRecognizerSoftC, LPRecognizerSoftCUncertainty, LPRecognizerHValueCUncertainty, LPRecognizerDeltaHCUncertainty, LPRecognizerDeltaHS, LPRecognizerDeltaHSUncertainty, Program_Options 

class TestPlanRecognizerFactory(unittest.TestCase):
    def setUp(self):
        pass

    def test_factory(self):
        factory = PlanRecognizerFactory(None)
        recognizer = factory.get_recognizer("h-value")
        self.assertEqual(recognizer.__class__, LPRecognizerHValue)
        recognizer = factory.get_recognizer("h-value-c")
        self.assertEqual(recognizer.__class__, LPRecognizerHValueC)
        recognizer = factory.get_recognizer("soft-c")
        self.assertEqual(recognizer.__class__, LPRecognizerSoftC)
        recognizer = factory.get_recognizer("soft-c-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerSoftCUncertainty)
        recognizer = factory.get_recognizer("delta-h-s")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHS)
        recognizer = factory.get_recognizer("delta-h-s-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHSUncertainty)
        recognizer = factory.get_recognizer("delta-h-c")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHC)
        recognizer = factory.get_recognizer("delta-h-c-uncertainty")
        self.assertEqual(recognizer.__class__, LPRecognizerDeltaHCUncertainty)

    def test_hvalue_recognizer(self):
        factory = PlanRecognizerFactory(None)
        recognizer = factory.get_recognizer("h-value",options=None)

if __name__ == '__main__':
    unittest.main()
    