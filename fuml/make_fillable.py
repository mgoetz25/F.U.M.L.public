import io
import os
import tempfile

import PyPDF2.utils
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.colors import white
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from fuml import get_fillable_areas
from fuml.utils import pdf2image


def make_pdf_fillable(source_pdf_path, fillable_pdf_path, pagesize=letter):
    # create handle to read fed pdf
    try:
        existing_pdf = PdfFileReader(open(source_pdf_path, "rb"))
    except PyPDF2.utils.PyPdfError as e:
        print(e)
        return

    # create a temporary directory to hold the images
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_name = temp_dir.name

    pdf2image.pdf_to_images(
        source_pdf_path,
        temp_dir_name,
        "png",
        "img_"
    )

    # define where to write fillable pdf to.
    output = PdfFileWriter()

    # process each page
    for page in range(existing_pdf.numPages):
        print("Page: " + str(page))

        # define path were the page's image is located
        page_img_path = os.path.join(temp_dir_name, "img_" + str(page) + ".png")
        boxInfo = get_fillable_areas.get_fillable_areas(
            page_img_path
        )
        # remove temporary file
        os.remove(page_img_path)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=pagesize)
        # print(letter)
        # width = int(pageInfo[4]/pageInfo[3])
        # height = int(pageInfo[5]/pageInfo[3])
        # can.setPageSize((width, height))
        can.setFillColorRGB(1, 0, 0)
        currentPage = existing_pdf.getPage(page)
        form = can.acroForm

        # print(boxInfo)
        # print(can.getpdfdata())

        # do business logic here.
        # add text and check boxes
        for i, box in enumerate(boxInfo):
            xPos = box[0] / 2
            yPos = letter[1] - ((box[1] / 2) + box[3] / 2)
            boxWidth = box[2] / 2
            boxHeight = box[3] / 2
            form.textfield(name='textbox_' + str(page) + '_' + str(i),
                           x=xPos, y=yPos,
                           fillColor=white,
                           width=boxWidth, height=boxHeight,
                           forceBorder=True,
                           borderColor=white)

        can.save()
        packet.seek(0)
        fillablePage = PdfFileReader(packet)

        currentPage.mergePage(fillablePage.getPage(0))
        output.addPage(currentPage)

    outputStream = open(fillable_pdf_path, "wb")
    output.write(outputStream)
    outputStream.close()

    # cleanup the temporary directory
    temp_dir.cleanup()
    print("Fillable pdf is at: " + fillable_pdf_path)


if __name__ == "__main__":
    make_pdf_fillable(
        "fuml/data/pdfs_you_found_somewhere/1040.pdf",
        "fuml/data/pdfs_you_found_somewhere/fillableV_1040.pdf"
    )
