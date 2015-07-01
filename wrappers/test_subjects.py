#!/usr/bin/env python
# -*- coding: utf-8 -*-

#...the usual suspects.
import os, inspect

#...for the unit testing.
import unittest

#...for the logging.
import logging as lg

#...for the classifications.
from subjects import SubjectSet


class ClassificationsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_subject_set(self):

        ## The test classification set.
        cs = SubjectSet("testdata")

        # Test the number of subjects in the test dataset.
        self.assertEqual(cs.getNumberOfSubjects(), 2)

        ## The first test subject key (filename).
        test_subject_1_key = cs.getSubjects().keys()[0]
        #
        ## The first test subject.
        test_subject_1 = cs.getSubjects()[test_subject_1_key]
        #
        # Check the file name.
        self.assertEqual(test_subject_1.getSubjectFilename(), "00000_00_00.png")


if __name__ == "__main__":

    lg.basicConfig(filename='log_test_subjects.log', filemode='w', level=lg.DEBUG)

    lg.info(" *")
    lg.info(" *==============================================")
    lg.info(" * Logger output from wrappers/test_subjects.py ")
    lg.info(" *==============================================")
    lg.info(" *")

    unittest.main()

