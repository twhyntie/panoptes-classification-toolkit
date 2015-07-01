#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

  MoEDAL and Panoptes: Subject wrapper classes.

"""

#...for the OS stuff.
import os

#...for the logging.
import logging as lg

#...for the JSON stuff.
import json

class Subject:

    def __init__(self, filename, **kwargs):
        """
        Constructor.

        @param [in] filename The subject's file name.
        @param [in] **kwargs Key word arguments.
        """

        ## The subject filename.
        self.__filename = filename

        if "mag" not in kwargs.keys():
            raise IOError("SUBJECT_NO_MAGNIFICATION")

        ## The subject magnification.
        self.__mag = kwargs["mag"]

        lg.info(" * Creating subject information for '%s'." % (filename))
        lg.info(" *")

    def __lt__(self, other):
        return self.__filename < other.__filename

    def getSubjectFilename(self):
        return self.__filename

    def makePage(self, data_path, output_path):

        bn = os.path.basename(self.__filename)

        image_path = bn
        #image_path = os.path.join(data_path, bn)

        page_path = os.path.join(output_path, bn.split(".")[0] + ".html")

        ps = """<!DOCTYPE html>
<title>Panoptes Subject Browser</title>
<h1>SUBJECT_NAME</h1>
"""

        ps = ps.replace("SUBJECT_NAME", bn)

        with open(page_path, "w") as pf:
            pf.write(ps)


class SubjectSet:
    """ Wrapper class for a set of Panoptes subjects. """

    def __init__(self, data_path):
        """
        Constructor.
        """

        ## The manifest file path.
        manifest_file_path = os.path.join(data_path, "manifest.csv")
        #
        if not os.path.exists(manifest_file_path):
            raise IOError("* ERROR: no manifest file found in '%s' - exiting." % (manifest_file_path))

        ## Dictionary of the subjects { file_name:subject }.
        self.__subjects = {}

        # Get the subject details from the manifest.
        with open(manifest_file_path, "r") as mf:
            lines = mf.readlines()[1:]
            for l in lines:
                vals = l.strip().split(",")

                ## The filename.
                fn = vals[4]

                ## The magnification.
                mag = vals[3]

                ## The subject.
                subject = Subject(fn, mag=mag)

                # Check the subject file is in the input path.
                if not os.path.exists(os.path.join(data_path, fn)):
                    raise IOError("* ERROR: subject '%s' not found in '%s'." % (fn, data_path))

                # Add the subject.
                self.__subjects[fn] = subject


    def getNumberOfSubjects(self):
        return len(self.__subjects)

    def getSubjects(self):
        return self.__subjects
