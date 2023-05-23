import os
import sys

import fitz as fitz

"""
Small utility to convert pdfs to images.
Can be run as a script with three arguments:
    pdf source file name: the path to the pdf
    image directory: where you want to put the images
    prefix: a common prefix to put on the images
        for example: if prefix is 'img_', then the images generated are:
            img_1.png
            img_2.png
            ...
        in the directory 'image directory' of course.
"""


def pdf_to_images(pdf_filename, dir_for_images, image_format="png", image_prefix="img_"):
    """
    pdf_filename: the path to the pdf to render
    dir_for_images: the directory where to place the pages' images
    image_format: a string to describe format. Ex: 'png' '.JpG', etc.
    image_prefix: a common prefix before every image file. Ex: "img_", "taxform_", etc.
    """
    image_format = image_format.strip('.').lower()
    pdf_file = fitz.open(pdf_filename)
    page_num = 0
    for page in pdf_file:
        # get pixel representation of the pdf page.
        # the matrix object is used to determine the resolution at which
        #   to render the pdf into images.
        pixels = page.get_pixmap(alpha=False, matrix=fitz.Matrix(2, 2))
        pixels.save(os.path.join(dir_for_images, image_prefix + str(page_num) + "." + image_format))
        page_num += 1


if __name__ == "__main__":
    pdf_source_file = sys.argv[1]
    dir_for_imgs = sys.argv[2]
    prefix = sys.argv[3]
    pdf_to_images(pdf_source_file, dir_for_imgs, "png", prefix)
