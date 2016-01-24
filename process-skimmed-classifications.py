#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 MoEDAL and CERN@school - Processing skimmed Panoptes classifications.

 See the README.md file and the GitHub wiki for more information.

 http://cernatschool.web.cern.ch

"""

# Import the code needed to manage files.
import os, glob

#...for parsing the arguments.
import argparse

#...for the logging.
import logging as lg

#...for the CSV file processing.
import csv

#...for dealing with JSON data.
import json

#...for the time (being).
import time, calendar

# Wrapper class for the NTD scan images.
from wrappers.ntdscanimage import NtdScanImage

if __name__ == "__main__":

    print("*")
    print("*===========================================================*")
    print("* CERN@school - Processing skimmed Panoptes classifications *")
    print("*===========================================================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputPath",       help="Path to the input dataset.")
    parser.add_argument("outputPath",      help="The path for the output files.")
    parser.add_argument("subjectId",       help="The subject ID [XXXXX_XX_XX].")
    parser.add_argument("scanImagePath",   help="The scan image path.")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    args = parser.parse_args()

    ## The path to the data file.
    datapath = args.inputPath

    # Check if the input file exists. If it doesn't, quit.
    if not os.path.exists(datapath):
        raise IOError("* ERROR: '%s' input file does not exist!" % (datapath))

    ## The output path.
    outputpath = args.outputPath

    # Check if the output directory exists. If it doesn't, quit.
    if not os.path.isdir(outputpath):
        raise IOError("* ERROR: '%s' output directory does not exist!" % (outputpath))

    ## The subject ID.
    subject_id = args.subjectId
    #
    # FIXME Check format.

    ## The path to the subject's scan image.
    #
    # FIXME: Check the filename is correct, it exists, etc.
    scan_image_path = args.scanImagePath

    # Set the logging level.
    if args.verbose:
        level=lg.DEBUG
    else:
        level=lg.INFO

    # Configure the logging.
    lg.basicConfig(filename=os.path.join(outputpath, 'log_process-skimmed-classifications.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("* Subject ID          : '%s'" % (subject_id))
    print("* Subject image path  : '%s'" % (scan_image_path))
    print("*")
    lg.info(" *===========================================================*")
    lg.info(" * CERN@school - Processing skimmed Panoptes classifications *")
    lg.info(" *===========================================================*")
    lg.info(" *")
    lg.info(" * Input path          : '%s'" % (datapath))
    lg.info(" * Output path         : '%s'" % (outputpath))
    lg.info(" * Subject ID          : '%s'" % (subject_id))
    lg.info(" * Subject image path  : '%s'" % (scan_image_path))
    lg.info(" *")

    ## The number of annotations found for the subject ID.
    num_annos = 0

    ## The NTD scan image
    scan = NtdScanImage(outputpath, \
                        subject_id=subject_id, \
                        scan_image_path=scan_image_path \
                       )

    # Load the skimmed annotations CSV file.
    with open(datapath, "r") as df:

        # Read i the skimmed classifications.
        lines = df.readlines()

        # Loop over the entries.
        for i, line in enumerate(lines):

            # Extract the data.

            ## The annotation ID.
            anno_id = line.split(",")[0]

            ## The subject ID (from the annotation ID).
            sub_id = anno_id.split("-")[1]

            # Skip the subjects we don't want to look at.
            if sub_id != subject_id:
                continue

            # Count the number of annotations found for the subject.
            num_annos += 1

            # Extract the annotation information.
            scan.add_annotation(anno_id,line.split(",", 1)[1])

            # Uncomment to only process the first classification.
            #break

    lg.info(" *")
    lg.info(" * Number of annotations found for '%s': % 6d" % (subject_id, scan.get_number_of_annotations()))
    lg.info(" *")

    # Make the scan image file.
    scan.make_scan_image(outputpath)

    # Make the number of blobs identified per classification plot.
    scan.make_num_blobs_plot()

    # Make the blob details CSV file.
    scan.make_blob_details_csv_file()
