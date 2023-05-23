# imports
import os
from flask import *
from werkzeug.utils import secure_filename

# create web app and handle restrictions on file upload
app = Flask(__name__)
# file upload folder
app.config['UPLOAD_FOLDER'] = 'static/'
# filetype extensions restriction
app.config['UPLOAD_EXTENSIONS'] = {'.pdf'}
# file size restriction, currently 10 MB. changing the 10 changes the max MB allowed.
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# homepage, displays file upload form for user
@app.route('/')
def upload():
    return render_template("file_upload_form.html")

# results page, displays whether or not their file was successfully uploaded
@app.route('/result', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        # storing filename securely to protect against incorrect user input
        filename = secure_filename(f.filename)
        # checks for if file exists and if is within the requirements, then saves to static folder
        if f and allowed_file(filename):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            msg = "file uploaded successfully"
            return render_template("result.html", name=f.filename, msg=msg)
        else:
            msg = "file not uploaded"
            return render_template("result.html", name="None", msg=msg)

# error handler for pagenotfound errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template("pagenotfound.html", msg=error)

# error handler for too large file size errors
@app.errorhandler(413)
def request_entity_too_large(error):
    print(error)
    return render_template("result.html", name="None", msg="file too large")

# function that checks a file for correct extension type
def allowed_file(filename):
    # cleanse trailing whitespace and make lowercase
    filename_fixed = filename.strip().lower()
    for extension in app.config['UPLOAD_EXTENSIONS']:
        if filename_fixed.endswith(extension.lower()):
            return True
    return False

if __name__ == '__main__':
    app.run(debug=True)
