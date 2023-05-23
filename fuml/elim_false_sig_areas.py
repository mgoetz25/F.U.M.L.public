"""
This module is responsible for eliminating signature areas that conflict with other areas.
"""


def interval_overlap(i1, i2):
    """
    Given two intervals in the form (u, v), test to see if they have any overlap
    For algorithm, see: https://stackoverflow.com/a/20925869/11370665

    i1: interval 1
    i2: interval 2

    Return Value:
    True or False
    """

    if i1[1] >= i2[0] and i2[1] >= i1[0]:
        return True
    else:
        return False


def box_touch(a, b):
    """
    Given two boxes in the format [x, y, w, h], determines
      if the two boxes have any overlap or 'touch'.
    For algorithm, see: https://stackoverflow.com/a/20925869/11370665

    a: box 1
    b: box 2

    Return Value:
    True or False
    """

    # convert boxes from [x,y,w,h] to [x1,y1,x2,y2] format
    a_fixed = [a[0], a[1], a[0] + b[2], a[1] + a[3]]
    b_fixed = [b[0], b[1], b[0] + b[2], b[1] + b[3]]

    # get a x and y projections
    a_x_interval = [a_fixed[0], a_fixed[2]]
    a_y_interval = [a_fixed[1], a_fixed[3]]

    # get b x and y projections
    b_x_interval = [b_fixed[0], b_fixed[2]]
    b_y_interval = [b_fixed[1], b_fixed[3]]

    # a and b overlap/touch iff some interval between them overlaps
    if interval_overlap(a_x_interval, b_x_interval) or interval_overlap(a_y_interval, b_y_interval):
        return True
    else:
        return False


def eliminate_if_touch_another(sub_boxes, dom_boxes):
    """
    For each sub_box in sub_boxes, check to see if there exists a box in
      dom_boxes that 'touches' the current sub_box; if that is the case,
      eliminate the current sub_box.
    The implementation has O(sd) runtime complexity where s is the number
      of sub_boxes and d is the number of dom_boxes: effectively quadratic.
    The intended use-case is to make sub_boxes the signature areas and
      dom_boxes the detected closed boxes.

    sub_boxes: the boxes to possible eliminate on a box to box basis
    dom_boxes: used to determine if a certain sub_box should be eliminated

    Return Values:
    filtered_sub_boxes: a subset of the sub_boxes that does not a dom_box
    """
    filtered_sub_boxes = []
    for sub_box in sub_boxes:
        touch_some_dom_box = False  # for each sub_box; only raised if touches some dom_box
        for dom_box in dom_boxes:
            if box_touch(sub_box, dom_box):
                touch_some_dom_box = True
        # now that the current sub_box has been tested against every
        #   dom_box, if there was a dom_box that touched the sub_box,
        #   do NOT add that sub_box to the result.
        if not touch_some_dom_box:
            # add sub_box if it does not touch any dom_box
            filtered_sub_boxes.append(sub_box)

    return filtered_sub_boxes


if __name__ == "__main__":
    """
    print(eliminate_if_touch_another(
        [
            [0, 0, 10, 10],
            [0, 0, 2, 2]
        ],
        [
            [100, 100, 2, 2],
            [1000, 1000, 10, 10],
            [5, 5, 1, 1]
        ]
    ))
    """
