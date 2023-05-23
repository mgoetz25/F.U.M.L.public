"""
This module is for detecting checkboxes and character boxes at the minimum.
"""
import copy

import matplotlib.patches
from boxdetect import config
from boxdetect.pipelines import get_boxes
import matplotlib.pyplot as plt

import cv2
import numpy as np


def detect_boxes(
        file_name,
        width_range=(7, 1000),
        height_range=(7, 280),
        scaling_factors=[1.0, 1.05, 1.08, 1.1, 1.15, 1.2, 1.25, 1.3, 1.4, 1.45, 1.50],
        width_height_ratio_range=(0.90, 20.0),
        dilation_iterations=0
):
    """
    file_name: filename to image
    width_range: a 2-tuple describing the width-rage of the boxes to detect
    height_range: a 2-tuple describing the height-range of the boxes to detect
    scaling_factors: a list of factors to scale the image by to detect boxes
    width_height_ratio_range: a range of what the width dived by height must be for the boxes
    dilation_iterations: number of times to dilate the image before detecting boxes

      Returned Values:
    rects: a list of detected rectangles or boxes
    image: the inputted image
    output_image: the image with rectangles drawn over it
    """
    cfg = config.PipelinesConfig()

    cfg.width_range = width_range
    cfg.height_range = height_range

    cfg.scaling_factors = copy.deepcopy(scaling_factors)  # deepcopy for safety: do not want default argument to change.

    cfg.wh_ratio_range = width_height_ratio_range

    cfg.group_size_range = (1, 1)

    cfg.dilation_iterations = dilation_iterations

    rects, grouping_rects, image, output_image = get_boxes(
        file_name, cfg=cfg, plot=False
    )

    #plt.figure(figsize=(8, 8))
    #plt.imshow(output_image)
    #plt.show()
    return rects, image, output_image


def detect_boxes_cv2(
        filename,
        forced_height=1080,
        scale_interpolation=cv2.INTER_CUBIC,
        grayscale_threshold_lower=25,
        grayscale_threshold_upper=255,
        edge_threshold_lower=0,
        edge_threshold_upper=5,
        edge_closing_kernel_dim=(3, 3),
        combined_dilation_kernel_dim=(2, 2),
        combined_dilation_iterations=1,
        line_minimum_width=23,

        # arguments to pass into detect_boxes
        width_range=(7, 1000),
        height_range=(7, 280),
        scaling_factors=[1.0, 1.05, 1.08, 1.1, 1.15, 1.2, 1.25, 1.3, 1.4, 1.45, 1.50],
        width_height_ratio_range=(0.90, 20.0),
        dilation_iterations=0

):
    """
    filename: the filename to the image
    forced_height: in pixels, what to force the height of the image to while preserving aspect ratio
    scale_interpolation: method to interpolate the scale of the image
    grayscale_threshold_lower: lower threshold for grayscale function
    grayscale_threshold_upper:  upper threshold for the grayscale function
    edge_threshold_lower: lower threshold for the edge detection function
    edge_threshold_upper: upper threshold for the edge detection function
    edge_closing_kernel_dim: 2-tuple to use as kernel dimensions for closing operation on edge detected image
    combined_dilation_kernel_dim: 2-tuple to use as kernel dimensions for dilation operation on combined image
    combined_dilation_iterations: number of times to perform the dilation operation on combined image
    line_minimum_width: minimum width of the vertical and horizontal lines to detect out of combined image

      These arguments are passed into detect_boxes
    width_range: a 2-tuple describing the width-rage of the boxes to detect
    height_range: a 2-tuple describing the height-range of the boxes to detect
    scaling_factors: a list of factors to scale the image by to detect boxes
    width_height_ratio_range: a range of what the width dived by height must be for the boxes
    dilation_iterations: number of times to dilate the image before detecting boxes

      Returned Values:
    rects: a list of detected boxes or rectangles which are in the form of a list: [x,y,w,h]
    final_image: the processed image after all of the transformations before being fed to detect_boxes
    im_scaled: the scaled version of the inputted image
    scale: the calculated scale
    new_width: the calculated new width = scale * original_width
    new_height: the calculated new height = scale * original_height

      Notes:
    The returned rects value describes the rectangles with its coordinates intended to describe the scaled image.
     before using the rects, for each rect in rects, divide each component by the returned scale to get rects which
     describe the original image, please!
    """
    FIG_SIZE = (8, 8)

    im_raw = cv2.imread(filename)

    # upscale image some
    width = im_raw.shape[1]
    height = im_raw.shape[0]
    # height must be forced_height by keep aspect ratio.
    # using vector algebra: if (new_width, new_height) = scale * (width, height), then
    #     by projection of the height dimension: new_height  = scale * height. Then solve for scale:
    #     scale = new_height / height
    scale = forced_height / height  # 20% more

    # apply the scale to the dimensions.
    new_width = int(width * scale)
    new_height = int(height * scale)
    new_dim = (new_width, new_height)
    # create the scaled version.
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

    # close any holes in the edges
    close_kernel = np.ones(edge_closing_kernel_dim, np.uint8)
    grey_edges_closed = cv2.morphologyEx(grey_edges, cv2.MORPH_CLOSE, close_kernel)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(grey_edges_closed, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # combine the thresholded gray image with the closed edges
    # combined = cv2.addWeighted(gray_thresh, 1.0, grey_edges, 1.0, gamma=0)
    combined = cv2.addWeighted(gray_thresh, 1.0, grey_edges_closed, 1.0, gamma=1)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(combined, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # dilate the combined result
    dilate_kernel = np.ones(combined_dilation_kernel_dim, np.uint8)
    combined_dilated = cv2.dilate(combined, dilate_kernel, iterations=combined_dilation_iterations)
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(combined_dilated, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # define the image to perform the box detection.
    processed_image = combined_dilated

    # now with a black and white image, identify horizontal and vertical lines.
    # try https://towardsdatascience.com/checkbox-table-cell-detection-using-opencv-python-332c57d25171
    #   vertical and horizontal components.

    line_min_width = line_minimum_width
    kernel_h = np.ones((1, line_min_width), np.uint8)
    kernel_v = np.ones((line_min_width, 1), np.uint8)
    vert = cv2.morphologyEx(processed_image, cv2.MORPH_OPEN, kernel_v)
    hori = cv2.morphologyEx(processed_image, cv2.MORPH_OPEN, kernel_h)
    vert_and_hori = hori | vert
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(cv2.cvtColor(vert_and_hori, cv2.COLOR_GRAY2RGB))
    #plt.show()

    # not used now
    """
    # see https://stackoverflow.com/questions/22240746/recognize-open-and-closed-shapes-opencv
    # it goes over the hierarchy of contours.
    contours = cv2.findContours(vert_and_hori, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
    """

    # write image to temp file and send to boxdetect
    import tempfile
    import os
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")  # because delete=False, closing file != delete.
    cv2.imwrite(tf.name, vert_and_hori)
    # capture the results of box detection
    rects, final_image, output_image = detect_boxes(
        tf.name,
        width_range=width_range,
        height_range=height_range,
        scaling_factors=scaling_factors,
        width_height_ratio_range=width_height_ratio_range,
        dilation_iterations=dilation_iterations
    )
    tf.close()
    os.remove(tf.name)  # delete temp file

    # plot detected boxes over original image.
    #plt.figure(figsize=FIG_SIZE)
    #plt.imshow(im_scaled)
    # plot each individual rectangle
    """
    ax = plt.gca()

    for rect in rects:
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

    # rects describes rectangles over scaled image. The caller does
    # not care about those, they want rectangles that describe the image
    # fed into the function. Make those.
    rects_corrected = []
    for rect in rects:
        # unscale each coordinate to match the original image's scale.
        rects_corrected.append([coord / scale for coord in rect])

    return rects_corrected, final_image, im_scaled, scale, new_width, new_height,


if __name__ == "__main__":
    # result = detect_boxes("data/pdfs_you_found_somewhere/1040_0.png")
    detect_boxes_cv2("fuml/data/pdfs_you_found_somewhere/1040_0.png")
