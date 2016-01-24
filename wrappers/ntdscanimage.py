#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

  MoEDAL and Panoptes: NTD scan wrapper class.

"""

#...for the OS stuff.
import os

#...for the logging.
import logging as lg

#...for the JSON data handling.
import json

#...for the plotting.
import matplotlib.pyplot as plt

#...for the image manipulation.
import matplotlib.image as mpimg

#...for the MATH.
import numpy as np

## For the k-means clustering.
#from scipy.cluster.vq import *

# Load the LaTeX text plot libraries.
from matplotlib import rc

# Uncomment to use LaTeX for the plot text.
rc('font',**{'family':'serif','serif':['Computer Modern']})
rc('text', usetex=True)

class NtdScanBlob:
    """ Wrapper class for the blobs identified in the NTD scan image. """

    def __init__(self, anno_id, x, y, r):

        ## The ID of the annotation the blob was found in.
        self.__anno_id = anno_id

        ## The blob's x position in the image.
        self.__x = x

        ## The blob's y position in the image.
        self.__y = y

        ## The blob radius.
        self.__r = r

    def __lt__(self, other):
        return self.__anno_id < other.__anno_id
    def get_anno_id(self):
        return self.__anno_id
    def get_x(self):
        return self.__x
    def get_y(self):
        return self.__y
    def get_r(self):
        return self.__r


class NtdScanImage:
    """ Wrapper class for the NTD scan image. """

    def __init__(self, outputpath, **kwargs):

        lg.info(" *")
        lg.info(" *===================================")
        lg.info(" * Initialising NtdScanImage object. ")
        lg.info(" *")

        ## The subject ID.
        self.__subject_id = None
        #
        if "subject_id" in kwargs.keys():
            # TODO: validate the value.
            self.__subject_id = kwargs["subject_id"]

        ## The scan image input path.
        self.__scan_image_path = None
        #
        if "scan_image_path" in kwargs.keys():
            # TODO: validate the value.
            self.__scan_image_path = kwargs["scan_image_path"]

            if not os.path.exists(self.__scan_image_path):
                raise IOError("* ERROR: image '%s' does not exist!" % (self.__scan_image_path))

        ## The number of annotations.
        self.__num_annotations = 0

        ## The number of blobs.
        self.__num_blobs = []

        ## The blobs.
        self.__blobs = []

        ## The subject output path.
        self.__output_path = os.path.join(outputpath, self.__subject_id)
        #
        if not os.path.isdir(self.__output_path):
            os.mkdir(self.__output_path)

        ## The path to the scan analysis plots.
        self.__plot_path = os.path.join(outputpath, self.__subject_id, "plots")
        #
        if not os.path.isdir(self.__plot_path):
            os.mkdir(self.__plot_path)

        ## Path to the image file for the (analysed) scan image.
        self.__image_output_path = os.path.join(self.__plot_path, self.__subject_id + ".png")

        ## Path of the output directory for the subject data.
        self.__data_output_path = os.path.join(outputpath, self.__subject_id, "data")
        #
        if not os.path.isdir(self.__data_output_path):
            os.mkdir(self.__data_output_path)

        lg.info(" * Subject ID              : '%s'" % (self.__subject_id))
        lg.info(" * Scan image path         : '%s'" % (self.__scan_image_path))
        lg.info(" * Scan plots path         : '%s'" % (self.__plot_path))
        lg.info(" *")

    def get_number_of_annotations(self):
        return self.__num_annotations

    def get_number_of_blobs_list(self):
        return self.__num_blobs

    def add_annotation(self, anno_id, anno):
        """ Add information from a classification annotation. """

        ## The annotation data
        d = json.loads(anno)

        self.__num_annotations += 1

        lg.info(" * Number of JSON entries in the annotation: % 5d" % (len(d)))

        # Loop over the task answers for this annotation.
        for entry in d:

            #===========
            # The blobs
            #===========
            if entry["task"] == "T3":

                # Get the blob information from the annotation.
                blob_info = entry["value"]

                lg.info(" * Number of blobs found: %d" % (len(blob_info)))

                # Add the number of blobs found in this annotation.
                self.__num_blobs.append(len(blob_info))

                # Add a blob for each blob found.
                for blob_i in blob_info:
                    x = blob_i["x"]
                    y = blob_i["y"]
                    r = blob_i["r"]
                    self.__blobs.append(NtdScanBlob(anno_id,x,y,r))
                    lg.info(" *--> Blob (x,y,r) = (%f,%f,%f))" % (x,y,r))

        lg.info(" *")

    def make_scan_image(self, outputpath):
        """ Recreates the original scan image with additional analysis. """

        if not os.path.isdir(outputpath):
            raise IOError("* ERROR: output path '%s' does not exist!" % (outputpath))

        if not self.__scan_image_path or not os.path.exists(self.__scan_image_path):
            raise IOError("* ERROR: '%s' scan image not found!" % (self.__scan_image_path))

        # Load in the image.
        # The image as a NumPy array.
        img = mpimg.imread(self.__scan_image_path)

        lg.info(" * Image dimensions: %s" % (str(img.shape)))

        ## The figure upon which to display the scan image.
        plot = plt.figure(101, figsize=(5.0, 5.0), dpi=150, facecolor='w', edgecolor='w')

        # Adjust the position of the axes.
        plot.subplots_adjust(bottom=0.17, left=0.15)

        ## The plot axes.
        plotax = plot.add_subplot(111)

        # Set the y axis label.
        plt.ylabel("$x$")

        # Set the x axis label.
        plt.xlabel("$y$")

        # Show the image (uncomment to do so).
        plt.imshow(img)
        #plt.show()

        # Draw the blob centres.
        #
        blob_xs = [blob.get_x() for blob in self.__blobs]
        blob_ys = [blob.get_y() for blob in self.__blobs]
        #
        plt.scatter(blob_xs,blob_ys,marker='x',color='#CC9900',linewidth=1.0)
        #
        # Use k-means clustering to find the blob centres.
        #num_blobs = 2 # FIXME: make this a variable dependent on the
        #blob frequency mode (i.e. most populous bin).
        #
        #res, idx = kmeans2(np.array(zip(blob_xs, blob_ys)), num_blobs)
        #
        #plt.scatter(res[:,0],res[:,1], marker='x', s = 500, linewidths=2)

        # Draw the blobs.
        for blob in self.__blobs:
            blob_circle = plt.Circle((blob.get_x(), blob.get_y()), blob.get_r(), color='#CC9900', fill=False, linewidth=3.0, alpha=1.0)
            plt.gcf().gca().add_artist(blob_circle)

        # Add a grid.
        plt.grid(1)

        # Crop the plot limits to the limits of the scan iteself.
        plotax.set_xlim([0, img.shape[1]])
        plotax.set_ylim([img.shape[0]-1, 0])

        # Save the figure.
        plot.savefig(self.__output_path)

    def make_num_blobs_plot(self):
        """ Plots a histogram of the number of blobs found in the scan. """

        ## The figure upon which to display the scan image.
        plot = plt.figure(102, figsize=(5.0, 5.0), dpi=150, facecolor='w', edgecolor='w')

        # Adjust the position of the axes.
        plot.subplots_adjust(bottom=0.17, left=0.15)

        ## The plot axes.
        plotax = plot.add_subplot(111)

        # Set the x axis label.
        plt.xlabel("Number of blobs identified")

        # Set the y axis label.
        plt.ylabel("Number of classifications")

        # A list of bin edges.
        my_bins = range(max(self.__num_blobs)+2)

        # Make the histogram.
        n, bins, patches = plt.hist(self.__num_blobs, bins=my_bins, histtype='stepfilled', align='left')

        # Set the plot's visual properties.
        plt.setp(patches, 'facecolor', 'g', 'alpha', 0.75, 'linewidth', 0.0)

        ## An array for the x axis tick values.
        x_ticks = np.arange(0, max(self.__num_blobs)+2)

        # Set the x axis ticks accordingly.
        plotax.set_xticks(x_ticks)

        # Set the x axis limits to make sure the whole bar width is displayed.
        plotax.set_xlim([-0.5, max(self.__num_blobs)+0.5])

        # Add a grid.
        plt.grid(1)

        # Save the figure.
        plot.savefig("%s/blobs.png" % (self.__plot_path))

    def make_blob_details_csv_file(self):
        """ Write out the (anonymised) blob details to a CSV file. """

        ## The string for output to the CSV file.
        ds  = "annotation_id,x,y,r\n"
        ds += ",[pixels],[pixels],[pixels]\n"

        for i, b in enumerate(sorted(self.__blobs)):
            ds += "%s,%.1f,%.1f,%.1f" % (b.get_anno_id(),b.get_x(),b.get_y(),b.get_r())
            if i < len(self.__blobs):
                ds += "\n"

        with open(os.path.join(self.__data_output_path, "blobs.csv"), "w") as df:
            df.write(ds)
