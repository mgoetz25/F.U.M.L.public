# imports
import os
from flask import *
from flask_mail import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
import Website.web_template.Encryption as Encryption
from fuml.make_fillable import make_pdf_fillable
import sqlite3 as sql
import re
import random
import math
from datetime import timedelta
import PyPDF2


# create web app and handle restrictions on file upload
app = Flask(__name__)
# create the upload folders when setting up your app
os.makedirs(os.path.join(app.instance_path, 'forms'), exist_ok=True)
os.makedirs(os.path.join(app.instance_path, 'results'), exist_ok=True)
# filetype extensions restriction
app.config['UPLOAD_EXTENSIONS'] = {'.pdf'}
# file size restriction, currently 10 MB. changing the 10 changes the max MB allowed.
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
# ability to change host and port
HOST = '127.0.0.1'
PORT = 5000
# flask email settings, eventually move to environment variables for easy updatability
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'ebae1fc0c8ce0a'
app.config['MAIL_PASSWORD'] = 'ab28f83e2cc3de'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes= 5)
mail = Mail(app)
path = ''


# homepage, displays file upload form for user
@app.route('/', methods=['GET', 'POST'])
def index():
    global path
    # if uploading a file
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        f = request.files['file']
        # storing filename securely to protect against incorrect user input
        f.filename = secure_filename(f.filename)
        # checks for if file exists and if is within the requirements, then saves to static folder
        if f and allowed_file(f.filename):
            unique_filename = make_unique(f.filename)
            forms = os.path.join(app.instance_path, 'forms', secure_filename(unique_filename))
            results = os.path.join(app.instance_path, 'results', secure_filename(unique_filename))
            # save uploaded file to forms
            f.save(os.path.join(app.instance_path, 'forms', secure_filename(unique_filename)))
            # make pdf fillable and save to results folder
            make_pdf_fillable(forms, results)
            print(results + secure_filename(unique_filename))
            if os.path.exists(results):
                msg = "file uploaded successfully"
                session['uploaded'] = True
                # email message to send
                if session.get('logged_in') and session.get('verified') and session.get('send'):
                    emsg = Message('Here is your uploaded PDF!', sender='no-reply@fuml.com',
                                   recipients=[str(session.get('email'))])
                    emsg.body = "Hello " + str(session.get(
                        'name')) + ", here is your fillable PDF. This email was sent by an automated system. " \
                                   "Send any inquiries or concerns to fakeemail@place.com."
                    with app.open_resource('instance/results/' + str(unique_filename)) as fp:
                        emsg.attach('instance/forms/' + str(unique_filename), "application/pdf", fp.read())
                    mail.send(emsg)
                path = results
                return redirect('/result/' + f.filename)
            # if file is a malformed pdf it will not have saved in results
            else:
                session['uploaded'] = False
                msg = 'malformed pdf files cannot be read'
                return result(f.filename, msg)
        # if file is not valid
        else:
            session['uploaded'] = False
            if not f:
                msg = 'no file uploaded'
            else:
                msg = 'please enter a PDF file'
            return result(f.filename, msg)
    # if not uploading a file
    if not session.get('logged_in'):
        return render_template("index.html", msg="Hello guest!")
    else:
        if not session.get('verified'):
            return render_template("index.html", msg=session['name'] + ", please check your email for your verification code.")
        return render_template("index.html", msg="Hello " + session['name'] + "!")


# about page, displays information about F.U.M.L.
@app.route('/about')
def about():
    return render_template("about.html")


# signup page
@app.route('/signup')
def signup():
    if not session.get('logged_in'):
        return render_template('signup.html')
    else:
        return render_template('pagenotfound.html')


# handles adding of user to database
@app.route('/usersignup', methods=['POST', 'GET'])
def adduser():
    # if user is logged in, don't render sign up page
    if session.get('logged_in'):
        return index()
    else:
        if request.method == 'POST':
            m = []
            em = 'test@xyzmail.com'
            con = sql.connect('Users.db')
            pw = ''
            rpw = ''
            try:
                # retrieve user input from fields
                un = request.form['usr']
                em = request.form['email']
                pw = request.form['psw']
                rpw = request.form['repsw']

                # check password entered
                passes = password_check(pw)

                # if valid user signed up
                if len(un) > 0 and email_check(em) and pw == rpw and passes.get('password_ok'):
                    try:
                        # encrypts data before saving
                        unenc = str(Encryption.cipher.encrypt(bytes(un, 'utf-8')).decode("utf-8"))
                        emenc = str(Encryption.cipher.encrypt(bytes(em, 'utf-8')).decode("utf-8"))
                        pwenc = str(Encryption.cipher.encrypt(bytes(pw, 'utf-8')).decode("utf-8"))
                        pwhash = generate_password_hash(str(pwenc))
                        # email verification
                        code = random.random() * 1000000
                        code = math.trunc(code)
                        if code < 100000:
                            code = str(code).zfill(6)
                        cur = con.cursor()
                        cur.execute(
                            "Insert Into Users (Username, Password, Email, EmailCode, Verified) Values (?,?,?,?,?)",
                            (unenc, pwhash, emenc, str(code), False))
                        con.commit()
                        # automatically logs in signed up user
                        session['name'] = un
                        session['email'] = em
                        session['logged_in'] = True
                        session['verified'] = False
                        # sends user verification email
                        emsg = Message('Verify Your Email', sender='no-reply@fuml.com',
                                       recipients=[str(session.get('email'))])
                        emsg.body = "Hello " + str(session.get(
                            'name')) + " please enter this code in your settings to verify your email and get " \
                                       "your completed PDFs sent to you: \n" + str(code)
                        mail.send(emsg)
                    # checks for existing username and password
                    except con.IntegrityError as e:
                        print(e)
                        if str(e).endswith('Username'):
                            m.append('Account with Username already exists.')
                        if str(e).endswith('Email'):
                            m.append('Account with Email already exists.')
                        session['logged_in'] = False
            except con.DatabaseError:
                con.rollback()
                m[0] = 'database is offline'
            finally:
                con.close()
                if session.get('logged_in'):
                    return index()
                else:
                    # generate incorrect sign up messages
                    if not email_check(em):
                        m.append("Invalid email")
                    if passes.get('length_error'):
                        m.append("Password must be at least 8 characters long")
                    if passes.get('digit_error'):
                        m.append("Password must have at least one digit")
                    if passes.get('uppercase_error'):
                        m.append("Password must have at least one uppercase letter")
                    if passes.get('lower_error'):
                        m.append("Password must have at least one lowercase letter")
                    if passes.get('symbol_error'):
                        m.append("Password must have at least one symbol")
                    if pw != rpw:
                        m.append("Password re-entry must match the original")
                    return render_template('signup.html', message=m)


# email validation
def email_check(email):
    # valid email follows this expression
    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(email_regex, email)


# password validation
def password_check(password):
    # must be at least 8 characters long
    length_error = len(password) < 8

    # must have at least one digit
    digit_error = re.search(r"\d", password) is None

    # must have at least one uppercase letter
    uppercase_error = re.search(r"[A-Z]", password) is None

    # must have at least one lowercase letter
    lowercase_error = re.search(r"[a-z]", password) is None

    # must have at least one symbol
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None

    # overall result of checks
    password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

    return {
        'password_ok': password_ok,
        'length_error': length_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
    }


# logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['name'] = 'guest'
    session['email'] = 'none'
    session['verified'] = False
    session.permanent = False
    return redirect('/')


# render login page
@app.route('/login')
def render_login():
    if not session.get('logged_in'):
        return render_template('login.html')
    return index()


# login page
@app.route('/login', methods=['POST'])
def login():
    m = 'test'
    if request.method == 'POST':
        try:
            # request username and password from forms
            name = request.form['username']
            pword = request.form['password']

            # encrypt entered username and password
            nm = str(Encryption.cipher.encrypt(bytes(name, 'utf-8')).decode("utf-8"))
            pwd = str(Encryption.cipher.encrypt(bytes(pword, 'utf-8')).decode("utf-8"))
            with sql.connect('Users.db') as con:
                cur = con.cursor()

                sql_select_query = """Select * from Users where Username = ?"""
                cur.execute(sql_select_query, (nm,))
                row = cur.fetchone()
                # check if email was used instead of username
                if row is None:
                    sql_select_query = """Select * from Users where Email = ?"""
                    cur.execute(sql_select_query, (nm,))
                    row = cur.fetchone()
                # if user account exists and password hash matches
                if row is not None and check_password_hash(row[1], str(pwd)):
                    dname = str(Encryption.cipher.decrypt(row[0]))
                    dmail = str(Encryption.cipher.decrypt(row[2]))
                    session['logged_in'] = True
                    # if the user's account is verified
                    if row[4]:
                        session['verified'] = True
                        # whether verified wants to be sent emails
                        if row[3] == 0:
                            session['send'] = False
                        elif row[3] == 1:
                            session['send'] = True
                    else:
                        session['verified'] = False
                    # if user used their username to login
                    if name == dname:
                        session['name'] = name
                        session['email'] = dmail
                    # if user used their email to login
                    elif name == dmail:
                        session['name'] = dname
                        session['email'] = name
                else:
                    session['logged_in'] = False
                    m = "Invalid username/email and/or password!"
        except con.DatabaseError:
            con.rollback()
            m = "Database is offline."
        finally:
            con.close()
            if session.get('logged_in'):
                session.permanent = True
                return index()
            else:
                return render_template('login.html', message=m)


# render user settings page
@app.route('/settings')
def render_settings():
    return render_template('settings.html')


# settings page
@app.route('/settings', methods=['POST'])
def settings():
    m = 'test'
    con = sql.connect('Users.db')
    if request.method == 'POST':
        try:
            # verified user is trying to change whether to receive emails
            if session.get('verified'):
                if session.get('send') and request.form.get('sendemail') == 'ChangeSend':
                    session['send'] = False
                    m = 'You will now not receive emails of your finished PDFs.'
                elif not session.get('send') and request.form.get('sendemail') == 'ChangeSend':
                    session['send'] = True
                    m = 'You will now receive emails of your finished PDFs.'
            # unverified user seeking verification
            else:
                # get user code input
                code = request.form['emcode']
                con.row_factory = sql.Row
                cur = con.cursor()
                # search for particular user
                sql_select_query = """Select * from Users where Username = ?"""
                nm = str(Encryption.cipher.encrypt(bytes(session.get('name'), 'utf-8')).decode("utf-8"))
                cur.execute(sql_select_query, (nm,))
                row = cur.fetchone()
                # if their entered code matches, update user to verified and re-render the page
                if row[3] == code:
                    update_query = '''Update Users set Verified = True where Username = ?'''
                    cur.execute(update_query, (nm,))
                    update_query = '''Update Users set EmailCode = 0 where Username = ?'''
                    cur.execute(update_query, (nm,))
                    con.commit()
                    session['verified'] = True
                    session['send'] = False
                    m = 'Successfully verified your email!'
                else:
                    m = 'Incorrect code.'
        except con.DatabaseError:
            con.rollback()
            m = "Database is offline."
        finally:
            con.close()
            return render_template('settings.html', msg=m)


# others page, placeholder
@app.route('/others')
def others():
    return render_template("others.html")


# results page
@app.route("/result/<filename>", methods=['GET'])
def result(filename, msg='File uploaded successfully'):
    return render_template("result.html", value=filename, msg=msg)


# return file to user for download
@app.route("/return-files/<filename>")
def return_files_tut(filename):
    return send_file(path, as_attachment=True, attachment_filename='')


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
    # cleanse trailing whitespace if it exits for some reason
    filename_trimmed = filename.strip()
    for extension in app.config['UPLOAD_EXTENSIONS']:
        if filename_trimmed.endswith(extension.lower()):
            return True
    return False


# function to ensure each saved and downloadable PDF is a unique filename
def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(host=HOST, port=PORT, debug=True)
