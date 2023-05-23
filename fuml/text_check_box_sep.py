"""
This module is responsible for distinguishing between checkboxes and textboxes.
"""


def separate_text_check_boxes(boxes, cb_wh_ratio_accept_range=(0.8, 1.1)):
    """
    boxes: a list of boxes. each box is in the format [x, y, w, h]
    cb_wh_ratio_accept_range: a 2-tuple. Used to determine if a box is a checkbox.
      if the width / height of the current box falls in this range, the box
      is considered a checkbox; otherwise, it might be a textbox.

      Return Values:
    textboxes: sublist of boxes considered textboxes
    checkboxes: sublist of boxes considered checkboxes

      Essential Property (this function satisfies this):
    Joining the outputted textboxes and checkboxes will result in boxes but
      may be in a different order.
    """

    # declare the textboxes and the checkboxes
    textboxes = []
    checkboxes = []

    for box in boxes:
        width = box[2]
        height = box[3]
        wh_ratio = width / height

        # see if the box is a checkbox
        lower_bound = cb_wh_ratio_accept_range[0]
        upper_bound = cb_wh_ratio_accept_range[1]
        if lower_bound <= wh_ratio <= upper_bound:
            checkboxes.append(box)
        else:
            # if not a checkbox, it must be a textbox
            textboxes.append(box)

    return textboxes, checkboxes

if __name__ == "__main__":
    pass