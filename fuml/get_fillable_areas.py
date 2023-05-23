"""
This module is for simply getting the fillable areas of an image and nothing more.
"""

import tempfile

import fuml.detect_boxes
import fuml.detect_signature_areas
import fuml.elim_false_sig_areas
import fuml.text_check_box_sep


def get_fillable_areas(filename):
    """
    Takes an image file with the name filename and returns the fillable areas.

    filename: the name of the image file

    Returned Values:
    fillable_areas: a list of rectangles in the format [x,y,w,h]
    """
    solid_rects, _, _, _, _, _ = fuml.detect_boxes.detect_boxes_cv2(filename)
    signature_rects, _, _, _, _ = fuml.detect_signature_areas.detect_signature_areas(filename)

    correct_signature_rects = fuml.elim_false_sig_areas.eliminate_if_touch_another(signature_rects, solid_rects)
    all_rects = solid_rects + correct_signature_rects

    return all_rects


def get_fillable_areas_separated(filename):
    rects = get_fillable_areas(filename)
    textboxes, checkboxes = fuml.text_check_box_sep.separate_text_check_boxes(rects)
    return textboxes, checkboxes


if __name__ == "__main__":
    get_fillable_areas("fuml/data/pdfs_you_found_somewhere/1040_0.png")
