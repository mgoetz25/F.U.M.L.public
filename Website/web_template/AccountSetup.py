# file for creating the database file

# imports
import sqlite3 as sql
import Website.web_template.Encryption as Encryption
import string,base64
from werkzeug.security import generate_password_hash
import random
import math

# connects to/creates database files and cursors to traverse them
con = sql.connect('Users.db')
cur = con.cursor()

# creates a new User table
cur.execute('''DROP TABLE IF EXISTS Users''')

# username and email have to both be unique
cur.execute('''CREATE TABLE Users(
Username TEXT PRIMARY KEY NOT NULL,
Password TEXT NOT NULL,
Email TEXT NOT NULL,
EmailCode TEXT NOT NULL,
Verified BOOL NOT NULL,
UNIQUE(Email));
''')

# saves changes
con.commit()
print('User table created.')

# default user for testing login functionality

unm = str(Encryption.cipher.encrypt(b'gohuntafish').decode("utf-8"))
psw = str(Encryption.cipher.encrypt(b'hatsunemiku').decode("utf-8"))
print(Encryption.cipher.decrypt(psw))
pswhash = generate_password_hash(str(psw))
eml = str(Encryption.cipher.encrypt(b'gohuntafish1@gmail.com').decode("utf-8"))

cur.execute("Insert Into Users (Username, Password, Email, EmailCode, Verified) Values (?,?,?,?,?)",(unm, pswhash, eml, 1, True))

code = random.random() * 1000000
code = math.trunc(code)
if code < 100000:
    code = str(code).zfill(6)

unm = str(Encryption.cipher.encrypt(b'fudge').decode("utf-8"))
psw = str(Encryption.cipher.encrypt(b'test').decode("utf-8"))
pswhash = generate_password_hash(str(psw))
eml = str(Encryption.cipher.encrypt(b'fudgemuffinlord@gmail.com').decode("utf-8"))

cur.execute("Insert Into Users (Username, Password, Email, EmailCode, Verified) Values (?,?,?,?,?)",(unm, pswhash, eml, str(code), False))

con.row_factory = sql.Row
cur = con.cursor()

# print user table
for row in cur.execute('SELECT * from Users'):
    print(str(Encryption.cipher.decrypt(row[0])))
    print(row[0])
    #print(str(Encryption.cipher.decrypt(row[1])))
    print(row[1])
    print(str(Encryption.cipher.decrypt(row[2])))
    print(row[3])
    print(row[4])

# saves the changes
con.commit()
