"""
The purpose of this module it to ensure that the testing system works as
intended. This test uses an 'absolute import' relative to the root of this
project, and the testing script at the root of this project should be
responsible for finding this file and running it.
"""

import unittest
import sys

from fuml import dummy_code  # there is functionality from here to test


class MyTestCase(unittest.TestCase):
    def test_example(self):
        self.assertEqual(True, True)
        self.assertGreaterEqual(10, 5)
        self.assertEqual(dummy_code.adder(2, 3), 5)


if __name__ == '__main__':
    unittest.main()
