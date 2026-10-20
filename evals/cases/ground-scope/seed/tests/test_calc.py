import unittest

from calc.calc import add, mul


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

    def test_mul(self):
        self.assertEqual(mul(2, 3), 6)
