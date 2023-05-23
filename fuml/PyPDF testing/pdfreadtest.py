# imports
import PyPDF4.utils
import PyPDF4

def pdf_test():
    try:
        # which file to be read
        filepath = "PDF Test Form.pdf"
        # create pdf object, 'rb' is read binary
        pdf = PyPDF4.PdfFileReader(open(filepath, 'rb'))
        # get pdf document info and num of pages
        print(pdf.getDocumentInfo())
        print(pdf.getNumPages())
    except PyPDF4.utils.PdfReadError as e:
        # detects malformed pdf
        print(e)

if __name__ == '__main__':
    pdf_test()
