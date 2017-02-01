from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug import generate_password_hash as generate, check_password_hash as check, secure_filename
import MySQLdb
import json
from functools import wraps
import csv
import os

app = Flask(__name__)
app.secret_key = "\xc2S\xbdE%u\x9cP2Z\xa8ZrsY\xe2\x99\x95\xa6\xe5\xc3\xd0\xe9\x83"

# Database Setup
cnx = {'host': '0.0.0.0',
       'username': 'root',
       'password': 'root',
       'db': 'ikarus'}

conn = MySQLdb.connect(cnx['host'], cnx['username'],
                       cnx['password'], cnx['db'])
cur = conn.cursor()
app.config['UPLOAD_FOLDER'] = 'uploads/'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] == "csv"


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("email"):
            return f(*args, **kwargs)
        else:
            error = "You need to login first!"
            return render_template('index.html', error=error)
    return wrap


@app.route('/')
def home():
    if session.get('email'):
        return redirect(url_for('userBody'))
    return render_template("index.html")


@app.route('/login', methods=["POST"])
def login():
    req = request.get_json(force=True)
    val = 'SELECT password FROM users WHERE email="{0}"'.format(
        req.get("email"))
    cur.execute(val)
    row = cur.fetchone()
    if row:
        if check(row[0], req.get("password")):
            session["email"] = req["email"]
            message = "ok"
            return json.dumps({"message": message})
        else:
            error = "You typed a wrong password. Please try again!"
            return json.dumps({"error": error})
    else:
        error = "Email does not exist!"
        return json.dumps({"error": error})


@app.route('/signup', methods=["POST"])
def signup():
    req = request.get_json(force=True)
    val = 'SELECT * FROM users WHERE email="{0}"'.format(req.get("email"))
    cur.execute(val)
    row = cur.fetchall()
    if row:
        error = "This email is already registered!"
        return json.dumps({"error": error})
    else:
        val = 'INSERT INTO users VALUES(NULL,%s,%s,%s,%s)'
        cur.execute(val, (req.get("name"), req.get("email"),
                          generate(req.get("password")), req.get("phone_no")))
        conn.commit()
        message = "You have successfully registered. Please login to continue!"
        return json.dumps({"message": message})


@app.route('/userBody', methods=["GET"])
@login_required
def userBody():
    return render_template("userBody.html")


@app.route('/logout')
@login_required
def logout():
    session.pop("email", None)
    message = "You have successfully logged out!"
    return render_template("index.html", message=message)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('uploadFile')
    other_data = request.form
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.mkdir(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        name = other_data.get("name")
        phone_no = other_data.get("phoneno")
        location = other_data.get("location")
        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "rb") as f:
            f.readline()  # Ignore the first line
            reader = csv.reader(f)
            for row in reader:
                val = 'INSERT INTO csv_data VALUES(NULL,%s,%s,%s,%s)'
                cur.execute(val, (row[0], row[1] if name else None, row[
                            2] if phone_no else None, row[3] if location else None))
                conn.commit()
        message = "OK"
        return json.dumps({"message": message})
    else:
        message = "Error"
        return json.dumps({"message": message})


@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    val = "SELECT * FROM csv_data"
    cur.execute(val)
    data = []
    rows=cur.fetchall()
    if rows:
        for row in rows:
            dic = {}
            dic["email"] = row[1]
            dic["name"] = row[2]
            dic["phone_no"] = row[3]
            dic["location"] = row[4]
            data.append(dic)
        print data
        return json.dumps({"data": data})
    else:
        return json.dumps({"data": None})


@app.route('/truncate', methods=['POST'])
def truncate():
    val = "TRUNCATE TABLE csv_data"
    cur.execute(val)
    conn.commit()
    message = "ok"
    return json.dumps({"message": message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
