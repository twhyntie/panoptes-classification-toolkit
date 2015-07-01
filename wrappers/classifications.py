#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

  MoEDAL and Panoptes: Classification wrapper classes.

"""

#...for the OS stuff.
import os

#...for the logging.
import logging as lg

#...for the subject wrapper class.
#from subjects import Subject

#...for the JSON stuff.
import json

#...for the annotation wrapper class.
from annotations import Annotation


class Classification:

    def __init__(self, values):
        """
        Constructor.

        @param [in] values The raw data string from the classification CSV row.
        """

        # Parse this data a bit more cleverly as the commas
        # appear all over the place in a non-fixed format.

        ## The name of the user who made the classification.
        self.__user_name, values = values.split(",", 1)

        ## The IP address from which the classification was made.
        self.__ip_address, values = values.split(",", 1)

        ## The workflow ID.
        self.__workflow_id, values = values.split(",", 1)
        #
        self.__workflow_id = int(self.__workflow_id)

        ## The workflow name.
        self.__workflow_name, values = values.split(",", 1)

        # Extract the workflow version numbers.
        workflow_version, values = values.split(",", 1)
        #
        major, minor = workflow_version.split(".")

        ## The workflow version (major).
        self.__workflow_version_maj = int(major)

        ## The workflow version (minor).
        self.__workflow_version_min = int(minor)

        ## The timestamp.
        self.__timestamp_str, values = values.split(",", 1)

        # Remove the two blanks - gold standard and expert info?
        b1, b2, values = values.split(",", 2)

        # OK so what's next...
        metadata, values = values.split("}\"", 1)

        ## The classification metadata.
        self.__metadata = metadata + "}\""
        #
        b3, values = values.split(",", 1)

        # Extract the annotation information.
        annotation, values = values.split("]\"", 1)
        #
        annotation = annotation + "]\""
        #
        ## The classification annotation.
        self.__annotation = Annotation(annotation, \
            (self.__workflow_id, self.__workflow_version_maj, self.__workflow_version_min))
        #
        b4, values = values.split(",", 1)

        ## The subject data in JSON format.
        subject_jd = json.loads(values.strip()[1:-1].replace("\"\"", "\""))
        #
        if len(subject_jd) > 1:
            raise IOError("* ERROR: subject data has more than one entry!")

        ## The subject ID.
        self.__subject_id = subject_jd.keys()[0]

        ## The subject filename.
        self.__subject_filename = subject_jd[self.__subject_id]["filename"]

        # Update the user.
        lg.info(" * New classification:")
        lg.info(" *---> User name          : '%s'" % (self.__user_name))
        lg.info(" *---> IP address         : '%s'" % (self.__ip_address))
        lg.info(" *---> Workflow           : %d (v%d.%d): '%s'" \
            % (self.__workflow_id, self.__workflow_version_maj, self.__workflow_version_min, self.__workflow_name))
        lg.info(" *---> Timestamp          : '%s'" % (self.__timestamp_str))
        lg.info(" *---> Subject            : '%s' (%s)" % (self.getSubjectId(), self.getSubjectFilename()))
        lg.info(" *")

    def getSubjectId(self):
        return self.__subject_id

    def getSubjectFilename(self):
        return self.__subject_filename

    def getWorkflowSpec(self):
        return (self.__workflow_id, self.__workflow_version_maj, self.__workflow_version_min)


class ClassificationSet:
    """ Wrapper class for the set of classifications. """

    def __init__(self, csv_path, workflow_spec):
        """
        Constructor.
        """

        if not os.path.exists(csv_path):
            raise IOError("* ERROR: '%s' does not exist!" % (csv_path))

        ## The header information.
        headers = ""

        ## The classification data.
        cd = []

        # Read in the classifications CSV file.
        with open(csv_path, "r") as cf:

            # Read in the data.
            lines = cf.readlines()

            # The classification header information.
            headers = lines[0].strip()

            # Extract the classification data.
            cd = lines[1:]

        ## Set of the user names.
        user_names = set()

        ## Dictionary of the workflows { id: ( "name", {version} ) }
        workflows = {}

        ## Set of the subject IDs.
        subject_ids = set()

        ## A dictionary of subject classification counts { ID:count }
        self.__subject_classification_count = {}

        ## A list of the classifications.
        self.__cs = []

        # Loop over the records and populate the classification set.
        for i, c in enumerate(cd):

            ## The classification.
            classification = Classification(c)

            # Skip classifications that aren't from the required workflow.
            if classification.getWorkflowSpec() != workflow_spec:
                continue

            # Get the classification's subject ID.
            subject_id = classification.getSubjectId()

            if subject_id in self.__subject_classification_count.keys():
                self.__subject_classification_count[subject_id] += 1
            else:
                self.__subject_classification_count[subject_id] = 1

            # Add the classification to the classification set.
            self.__cs.append(classification)


    def getNumberOfClassifications(self):
        return len(self.__cs)

    def getSubjectClassificationCount(self):
        return self.__subject_classification_count

    def getNumberOfUniqueSubjectsClassified(self):

        lg.info(" * Subject classification counts:")
        for subject_id, count in self.__subject_classification_count.iteritems():
            lg.info(" * Subject ID %s: % 5d" % (subject_id, count))
        lg.info(" *")

        return len(self.__subject_classification_count)
