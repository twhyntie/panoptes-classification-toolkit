#!/usr/bin/env python
# -*- coding: utf-8 -*-

#...the usual suspects.
import os, inspect

#...for the unit testing.
import unittest

#...for the logging.
import logging as lg

#...for the classifications.
from classifications import ClassificationSet


class ClassificationsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_classification_set(self):

        ## The test classification set.
        cs = ClassificationSet("testdata/results.csv", (27, 9, 14))

        # Test the number of classifications in the test dataset.
        self.assertEqual(cs.getNumberOfClassifications(), 20)


if __name__ == "__main__":

    lg.basicConfig(filename='log_test_classifications.log', filemode='w', level=lg.DEBUG)

    lg.info("")
    lg.info("=====================================================")
    lg.info(" Logger output from wrappers/test_classifications.py ")
    lg.info("=====================================================")
    lg.info("")

    unittest.main()
