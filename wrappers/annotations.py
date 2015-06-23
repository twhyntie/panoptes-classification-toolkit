#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

  MoEDAL and Panoptes: Annotation wrapper classes.

"""

#...for the OS stuff.
import os

#...for the logging.
import logging as lg

#...for the JSON stuff.
import json

class Pit:
    """ Wrapper class for the filled circle pits. """

    def __init__(self, dat):
        """
        Constructor.

        @param [in] dat The pit data from the classification CSV dump.
        """

        ## The pit radius.
        self.__r = dat["r"]

        ## The pit x.
        self.__x = dat["x"]

        ## The pit y.
        self.__y = dat["y"]

    def getX(self):
        return self.__x

    def getY(self):
        return self.__y

    def getRadius(self):
        return self.__r


class Annotation:

    def __init__(self, dat, workflow_spec):
        """
        Constructor.

        @param [in] dat The annotation data from the classification CSV dump.
        @param [in] workflow_spec Tuple with the workflow ID, ver. maj, min.
        """

        ## A list of pits found in the scan.
        self.__pits = []

        ## Is there anything unusual in the frame?
        self.__anything_unusual = None

        lg.info(" * Creating annotation information...")
        lg.info(" * Workflow %d (v%d.%d)." % (workflow_spec))
        lg.info(" *")

        # We only cater for this workflow at the moment.
        if workflow_spec == (27, 9, 14):
            self.processAnnotation(dat)


    def processAnnotation(self, dat):
        """
        Process the annotation data (27 v9.14).

        It's a bit hacky at the moment.
        It will depend on the final workflow used in the end.
        """
        ## The annotation data in JSON format.
        jd = json.loads(dat[1:-1].replace("\"\"", "\"").strip())

        # Loop over the tasks in the annotation data.
        for task in jd:

            # The "is there anything unusual?" question.
            if task["task"] == "init":
                if task["value"] == 1:
                    self.__anything_unusual = False
                elif task["value"] == 0:
                    self.__anything_unusual = True
                else:
                    raise IOError("* ERROR: Invalid value for \"Anything unusual?\" task...")

            # The pit circling task.
            elif task["task"] == "T1":

                # Loop over the pit circles.
                for p in task["value"]:
                    ## The current pit.
                    pit = Pit(p)

                    # Add the pit to the list.
                    self.__pits.append(pit)

        lg.info(" *------> Number of pits identified: %d" % (self.getNumberOfPitsIdentified()))

        for pit in self.__pits:
            lg.info(" *---------> Pit at (% 4d, % 4d) r = %6.2f" % (pit.getX(), pit.getY(), pit.getRadius()))
        if self.anythingUnusual():
            lg.info(" *------> Unusual subject - FLAGGED!")
        else:
            lg.info(" *------> Nothing unusual to see here.")
        lg.info(" *")

    def anythingUnusual(self):
        return self.__anything_unusual

    def getNumberOfPitsIdentified(self):
        return len(self.__pits)
