#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 MoEDAL and CERN@school - Processing Panoptes subjects.

 See the README.md file and the GitHub wiki for more information.

 http://cernatschool.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

# Wrapper class for the subject set.
from wrappers.subjects import SubjectSet


if __name__ == "__main__":

    print("*")
    print("*==================================================*")
    print("* CERN@school - Panoptes subject processing *")
    print("*==================================================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputPath",       help="Path to the input dataset.")
    parser.add_argument("outputPath",      help="The path for the output files.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    args = parser.parse_args()

    ## The path to the data file.
    datapath = args.inputPath

    ## The output path.
    outputpath = args.outputPath

    # Check if the output directory exists. If it doesn't, quit.
    if not os.path.isdir(outputpath):
        raise IOError("* ERROR: '%s' output directory does not exist!" % (outputpath))

    # Set the logging level.
    if args.verbose:
        level=lg.DEBUG
    else:
        level=lg.INFO

    # Configure the logging.
    lg.basicConfig(filename=os.path.join(outputpath, 'log_process-subjects.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("*")
    lg.info(" *---------------------")
    lg.info(" * process-subjects.py ")
    lg.info(" *---------------------")
    lg.info(" * Input path          : '%s'" % (datapath))
    lg.info(" * Output path         : '%s'" % (outputpath))
    lg.info(" *")


    ## The subject set.
    sset = SubjectSet(datapath)

    # Create the subject page (initial).
    for fn, subject in sset.getSubjects().iteritems():
        subject.makePage(datapath, outputpath)
