#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 MoEDAL and CERN@school - Skimming Panoptes classifications.

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

#...for the JSON data handling.
import json

#...for the time (being).
import time, calendar

if __name__ == "__main__":

    print("*")
    print("*================================================*")
    print("* CERN@school - Panoptes classification skimming *")
    print("*================================================*")

    # Get the datafile path from the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument("inputPath",       help="Path to the input dataset.")
    parser.add_argument("outputPath",      help="The path for the output files.")
    parser.add_argument("workflowVersion", help="The workflow version.")
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

    ## The workflow version.
    #
    # FIXME: validation on the workflow version string.
    workflow_version = args.workflowVersion

    # Set the logging level.
    if args.verbose:
        level=lg.DEBUG
    else:
        level=lg.INFO

    # Configure the logging.
    lg.basicConfig(filename=os.path.join(outputpath, 'log_skim-classifications.log'), filemode='w', level=level)

    print("*")
    print("* Input path          : '%s'" % (datapath))
    print("* Output path         : '%s'" % (outputpath))
    print("* Workflow version    : '%s'" % (workflow_version))
    print("*")
    lg.info(" *================================================*")
    lg.info(" * CERN@school - Panoptes classification skimming *")
    lg.info(" *================================================*")
    lg.info(" *")
    lg.info(" * Input path          : '%s'" % (datapath))
    lg.info(" * Output path         : '%s'" % (outputpath))
    lg.info(" * Workflow version    : '%s'" % (workflow_version))
    lg.info(" *")

    ## The headers.
    headers = []

    ## The annotations {"UserID_SubjectID":annotation}.
    anno_dict = {}

    ## A dictionary of logged on users.
    logged_on_users = {}

    ## A dictionary of non-logged on users.
    non_logged_on_users = {}

    ## A dictionary of subjects {subject_id:num_classifications}.
    subject_dict = {}

    ## A dictionary of subjects (logged-on users).
    #
    # { subject_id:number_of_classifications }
    logged_on_subject_dict = {}

    ## A dictionary of subjects (non-logged-on users).
    #
    # { subject_id:number_of_classifications }
    non_logged_on_subject_dict = {}

    ## The total number of classifications (as a check).
    total_classifications_check = 0

    # Read in the file.
    with open(datapath, "r") as df:

        ## The CSV file reader.
        reader = csv.reader(df)

        # Loop over the rows of the CSV file via the reader.
        for i, row in enumerate(reader):
            if i == 0:
                # Extract the header information.
                headers = row
            else:
                # Extract the data.

                # Check if the workflow is the correct version.
                #
                ## The workflow version.
                workflow_v = row[5]
                #
                #lg.info(" * Workflow version: %s" % (workflow_version))
                #
                if workflow_v != workflow_version:
                    continue

                # The User's ID.
                user_id = ""

                ## The time stamp the classification was created at (string).
                time_stamp_string = row[6]

                ## The UNIX time stamp the classification was created at (seconds).
                time_stamp_sec = calendar.timegm(time.strptime(time_stamp_string, "%Y-%m-%d %H:%M:%S %Z"))

                ## The subject ID [image number]_[row]_[col].
                subject_id = json.loads(row[11]).values()[0]["id"]
                #
                #lg.info(" *--> Subject ID: %s" % (subject_id))

                if subject_id not in subject_dict.keys():
                    subject_dict[subject_id] = 1
                else:
                    subject_dict[subject_id] += 1

                # Was the user logged in?
                if row[1] != "":
                    # For logged in users, use the User ID and the UNIX timestamp.
                    user_id = row[1] + ":%d" % (time_stamp_sec)

                    # Add the user to the logged-on user list.
                    if user_id not in logged_on_users.keys():
                        logged_on_users[user_id] = []

                    # Add to the logged-on user subject classification count.
                    if subject_id not in logged_on_subject_dict.keys():
                        logged_on_subject_dict[subject_id] = 1
                    else:
                        logged_on_subject_dict[subject_id] += 1

                else:
                    # For non-logged in users, use the User IP hash and UNIX timestamp.
                    user_id = row[2] + ":%d" % (time_stamp_sec)

                    # Add the user to the non-logged-on user list.
                    if user_id not in non_logged_on_users.keys():
                        non_logged_on_users[user_id] = []

                    # Add to the non-logged-on user subject classification count.
                    if subject_id not in non_logged_on_subject_dict.keys():
                        non_logged_on_subject_dict[subject_id] = 1
                    else:
                        non_logged_on_subject_dict[subject_id] += 1

                ## The annotation ID (should be unique!).
                anno_id = "%s-%s" % (user_id, subject_id)
                #
                #lg.info(" *--> Annotation ID: %s" % (anno_id))

                ## The annotation.
                anno = row[10]

                # Add the annotation to the dictionary.
                if anno_id in anno_dict.keys():
                    lg.error(" * ERROR!")
                    lg.error(" * User ID: %s" % (user_id))
                    lg.error(" * Subject: %s" % (subject_id))
                    raise IOError("* ERROR: The same user has classified the same subject twice!")
                else:
                    anno_dict[anno_id] = anno

    lg.info(" *")

    ## The header information.
    lg.info(" *--------------------")
    lg.info(" * HEADER INFORMATION ")
    lg.info(" *--------------------")

    for i, field_name in enumerate(headers):
        lg.info(" * %02d: '%s'" % (i, field_name))

    lg.info(" *")

    #=========================================================================
    # Write out the new annotation file.
    #=========================================================================
    #
    # We want to write out a new, skimmed set of annotations ready to be
    # processed by other scripts in this repo.

    ## The annotation file string (for writing).
    annos = ""

    # Loop over the annotations and write them to the output string.
    for anno_id, anno in anno_dict.iteritems():
        annos += "%s,%s\n" % (anno_id, anno)

    ## The skimmed CSV filename.
    skimmed_csv_filename = os.path.join(outputpath, "annotations.csv")
    #
    with open(skimmed_csv_filename, "w") as sf:
        sf.write(annos)

    #=========================================================================
    # User summary information.
    #=========================================================================
    #
    # We also want to know a bit about the users who made the classifications.

    ## The number of unique logged-on users.
    num_logged_on_users = len(logged_on_users)

    ## The number of unique non-logged-on users.
    num_non_logged_on_users = len(non_logged_on_users)

    lg.info(" *")
    lg.info(" *------------------")
    lg.info(" * USER INFORMATION ")
    lg.info(" *------------------")
    lg.info(" *")
    lg.info(" * Number of unique     logged-on users: % 6d" % (num_logged_on_users))
    lg.info(" * Number of unique non-logged-on users: % 6d" % (num_non_logged_on_users))
    lg.info(" *")

    ## The number of subjects classified.
    num_subjects = len(subject_dict)

    lg.info(" *----------------------------")
    lg.info(" * CLASSIFICATION INFORMATION ")
    lg.info(" *----------------------------")
    lg.info(" *")
    lg.info(" * Number of subjects classified: % 6d" % (num_subjects))
    lg.info(" *")

    ## A count of the number of classifications.
    total_classifications = 0

    ## A count of the classifications by logged-on users.
    tot_logged = 0

    ## A count of the classifications by non-logged-on users.
    tot_non_logged = 0

    lg.info(" * Number of classifications per subject:")
    lg.info(" *")

    # Produce an ordered CSV file of the number of classifications
    # per subject (all users, logged-on users, non-logged-on users).

    ## The string for the CSV file content (headers provided).
    subjects_vs_classifications = "subject_id,total,by_logged_on_users,by_non_logged_on_users\n"

    for i, sub_id in enumerate(sorted(subject_dict.keys())):

        total_classifications += subject_dict[sub_id]

        if sub_id in logged_on_subject_dict.keys():
            l_s = logged_on_subject_dict[sub_id]
            tot_logged += l_s
        else:
            l_s = 0
        if sub_id in non_logged_on_subject_dict.keys():
            n_s = non_logged_on_subject_dict[sub_id]
            tot_non_logged += n_s
        else:
            n_s = 0

        lg.info(" *--> %s: % 6d (% 3d + %3d)" % (sub_id, subject_dict[sub_id], l_s, n_s))

        subjects_vs_classifications += "%s,%d,%d,%d" % (sub_id, subject_dict[sub_id],l_s,n_s)
        if i < len(subject_dict):
            subjects_vs_classifications += "\n"
    #
    subjects_vs_classifications_filename = os.path.join(outputpath, "subjects.csv")
    #
    with open(subjects_vs_classifications_filename, "w") as sf:
        sf.write(subjects_vs_classifications)

    lg.info(" *")
    lg.info(" * Total (count)                    : % 6d" % (total_classifications))
    lg.info(" * Total (from annotations)         : % 6d" % (len(anno_dict)))
    lg.info(" * Total (logged-on, non-logged-on) : % 6d (%d + %d)" % (tot_logged + tot_non_logged, tot_logged, tot_non_logged))
    lg.info(" *")

    lg.info(" * For the skimmed annotations, see       : '%s'" % (skimmed_csv_filename))
    lg.info(" * For the clasificatios per subject, see : '%s'" % (subjects_vs_classifications_filename))
    lg.info(" *")
