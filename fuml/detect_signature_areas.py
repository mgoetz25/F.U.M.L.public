"""
This module is for detecting signature areas and places that are intended to be filled out
but only have a flat line. For example: First Name: __________ Last Name: ________ Middle Initial: ___
"""
import math
import os
import tempfile

import matplotlib.patches
import matplotlib.pyplot as plt
import cv2
import numpy as np

import fuml.detect_boxes


def detect_signature_areas(
        filename,
        forced_height=1080,
        scale_interpolation=cv2.INTER_CUBIC,
        grayscale_threshold_lower=25,
        grayscale_threshold_upper=255,
        edge_threshold_lower=0,
        edge_threshold_upper=5,
        combined_dilation_kernel_dim=(2, 2),
        combined_dilation_iterations=0,
        line_min_width=100,
        vertical_widening=11
):
    """
    filename: the filename of the image
    forced_height: in pixels, what to force the height of the image while preserving aspect ratio
    scale_interpolation: method to interpolate the scale the image
    grayscale_threshold_lower: lower threshold for grayscale function
    grayscale_threshold_upper:  upper threshold for the grayscale function
    edge_threshold_lower: lower threshold for the edge detection function
    edge_threshold_upper: upper threshold for the edge detection function
    combined_dilation_kernel_dim: 2-tuple to use as kernel dimensions for dilation operation on combined image
    combined_dilation_iterations: number of times to perform the dilation operation on combined image
    line_minimum_width: minimum height of the horizontal lines to detect out of combined image
    vertical_widening: in pixels, how must to raise the top side of the fallible areas

      Returned Values:
    rects_descaled: the signature areas that match the original image fed in; this is the main result
    im_scaled: the image scaled to match the forced_height
    scale: what the original image was scaled so that its height matched forced_height
    new_width: original image width * scale
    new_height: original image height * scale
    """
    FIG_SIZE = (8, 8)

    im_raw = cv2.imread(filename)

    # fix the size of the image while keeping aspect ratio.
    width = im_raw.shape[1]
    height = im_raw.shape[0]
    # height must be forced_height by keep aspect ratio.
    # using vector algebra: if (new_width, new_height) = scale * (width, height), then
    #     by projection of the height dimension: new_height  = scale * height. Then solve for scale:
    #     scale = new_height / height
    scale = forced_height / height

    # apply the scale to the dimensions
    new_width = int(width * scale)
    new_height = int(height * scale)
    new_dim = (new_width, new_height)
    im_scaled = cv2.resize(im_raw, new_dim, interpolation=scale_interpolation)

    # create a grayscale version.
    gray = cv2.cvtColor(im_scaled, cv2.COLOR_BGR2GRAY)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # get a threshold version
    gray_thresh = cv2.threshold(
        gray,
        grayscale_threshold_lower,
        grayscale_threshold_upper,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(gray_thresh, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # get the edges of the grey image
    grey_edges = cv2.Canny(gray, edge_threshold_lower, edge_threshold_upper)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(grey_edges, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # combine the thresholded gray image with the edges
    combined = cv2.addWeighted(gray_thresh, 1.0, grey_edges, 1.0, gamma=1)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(combined, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # dilate the combined result
    dilate_kernel = np.ones(combined_dilation_kernel_dim, np.uint8)
    combined_dilated = cv2.dilate(combined, dilate_kernel, iterations=combined_dilation_iterations)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(combined_dilated, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # declare what the processed image is
    processed_image = combined_dilated

    # get only the horizontal lines.
    kernel_horizontal = np.ones((1, line_min_width), np.uint8)
    horizontal_lines = cv2.morphologyEx(processed_image, cv2.MORPH_OPEN, kernel_horizontal)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(horizontal_lines, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # make a call to boxdetect
    # first, put current image from the pipeline into a temp file.
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    cv2.imwrite(tf.name, horizontal_lines)
    # now call boxdetect
    sig_line_rects, _, detect_boxes_visual = fuml.detect_boxes.detect_boxes(
        tf.name,
        width_range=(70, 4000),
        height_range=(1, 15),
        width_height_ratio_range=(10, 10000),
    )
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(detect_boxes_visual)
    #plt.show()
    # cleanup temp file
    tf.close()
    os.remove(tf.name)

    # we now have rectangles that capture the signature lines.
    # now, we need to calculate the signature areas, not the lines.

    # here is an idea, for each rectangle that captures the signature line,
    # shift it up by its height so it sits above the signature line.
    # then, adjust the height of the rectangle so it is reasonable.

    rects_above_sig_line = list(
        map(
            # new rect = [x, y - h, w, h], it basically moves rectangle right above sig line.
            lambda rect: [rect[0], rect[1] - rect[3], rect[2], rect[3]],
            sig_line_rects
        )
    )

    # we now need to decrease the y (make rectangle go higher) while adjusting h
    # to compensate for the movement.
    # its just like moving the top side of the rectangle upward

    rects_above_sig_line_adjusted = list(
        map(
            lambda rect: [rect[0], rect[1] - vertical_widening, rect[2], rect[3] + vertical_widening],
            rects_above_sig_line
        )
    )

    # plot the results over the scaled image.
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(im_scaled)
    # plot each individual rectangle
    """
    ax = plt.gca()
    for rect in rects_above_sig_line_adjusted:
        ax.add_patch(
            matplotlib.patches.Rectangle(
                (rect[0], rect[1]),
                rect[2],
                rect[3],
                linewidth=1,
                edgecolor='r',
                facecolor='none'
            )
        )
    plt.show()
    """

    # rectangles currently describe the scaled image,
    # unscale the rectangles so they describe the original fed image.
    # w_orig * scale = w_proc, so w_orig = w_proc / scale.

    rects_descaled = list(
        map(
            lambda rect: [rect[0] / scale, rect[1] / scale, rect[2] / scale, rect[3] / scale],
            rects_above_sig_line_adjusted
        )
    )

    return rects_descaled, im_scaled, scale, new_width, new_height


if __name__ == "__main__":
    detect_signature_areas("fuml/data/pdfs_you_found_somewhere/1040_1.png")
