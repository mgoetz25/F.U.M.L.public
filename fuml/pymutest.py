# imports
import fitz

def pdf_test():
    print(fitz.__doc__)
    try:
        # which file to be read
        filepath = "static/PDF Test Form.pdf"
        # creates a document object
        doc = fitz.open(filepath)
        # get document info and number of pages
        print(doc.metadata)
        print(doc.page_count)
        test_page_sizes(doc)
        # test adding a text field in the name field of the document
        # these are conversions from inches to user units
        test_add_field(doc,2.64 * 72,2.03 * 72,1.605 * 72,.48 * 72)
        # save changes and close document
        doc.save("static/PDF New Test Form.pdf")
        doc.close()
    except:
        # detects malformed pdf, couldn't find a specific exception for PyMuPDF
        print("Malformed pdf")

# function to test page sizes in document
def test_page_sizes(pdf):
    # check every page
    for page in pdf:
        # render page
        pix = page.get_pixmap()
        # convert user units to inches, each is 1/72 in
        w = pix.width / 72
        h = pix.height / 72
        # if page is not 8.5"x11"
        if w != 8.5 or h != 11:
            return False
        return True

# function to test functionality of adding widgets (fields)
def test_add_field(pdf,x,y,w,h):
    # get first page of pdf
    page = pdf[0]
    # create widget object
    widget = fitz.Widget()
    # widget of type text, can also be radio button, checkbox, etc.
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    # field name for data purposes, not seen by user
    widget.field_name = "text field"
    # default text in field
    widget.field_value = "lorem ipsum lol"
    # size of text field
    widget.rect = fitz.Rect(x,y,w + x,h + y)
    # add widget to page
    page.add_widget(widget)

if __name__ == '__main__':
    pdf_test()