from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import sqlite3
import random
import os

USER = None
USERID = None
conn = sqlite3.connect('/Users/souravjohar/Documents/Code/Flask/water.db')
c = conn.cursor()

app = Flask(__name__)

app.secret_key = 'lolol'


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        pass
    else:
        c.execute("select custid from userlogin where username = '{}'".format(USER))
        global USERID
        USERID = c.fetchone()[0]
        c.execute("select firstname, lastname from customers where custid = '{}'".format(USERID))
        f, l = c.fetchone()
        d_name = f + " " + l
        return render_template('index.html', d_name=d_name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        r_username = request.form['username']
        r_pass = request.form['password']
        try:
            c.execute("select pword from userlogin where username = '{}'".format(r_username))
            pword = c.fetchall()[0][0]
            if pword == r_pass:
                session['logged_in'] = True
                global USER
                USER = r_username
                return redirect(url_for('home'))
            else:
                error = 'Invalid Credentials. Please try again.'
        except Exception as e:
            print str(e)
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))


@app.route('/profile')
@login_required
def displayProfile():
    c.execute("select firstname, lastname, address, areaid from customers where custid = '{}'".format(USERID))

    f, l, a, aid = c.fetchone()
    c.execute("select areaname from area where areaid = '{}'".format(aid))
    area = c.fetchone()[0]

    c.execute("select phone from phone where custid = '{}'".format(USERID))
    p = c.fetchone()[0]
    data = dict(firstname=f, lastname=l, phone=p, address=a, area=area)
    return render_template("profile.html", data=data)


@app.route('/connection')
@login_required
def displayConn():
    c.execute("select waterallowance, connectiontype, address,areaid from customers where custid = '{}'".format(USERID))
    wa, ct, a, aid = c.fetchone()
    c.execute("select areaname from area where areaid = '{}'".format(aid))
    area = c.fetchone()[0]
    c.execute("select suppliername from supplier where areaid = '{}'".format(aid))
    s = random.choice(c.fetchone())
    if wa == "null":
        data = dict(ct=ct.split("-")[0], wa="unlimited", address=a, area=area, supp=s)
    else:
        data = dict(ct=ct, wa=wa, address=a, area=area, supp=s)
    return render_template("connection.html", data=data)


@app.route('/complain', methods=['GET', 'POST'])
@login_required
def displayComplains():
    prev = None
    c.execute(
        "select serviceid, servicetype, servicerequest, servicestatus from service where custid = '{}'".format(USERID))
    result = c.fetchone()
    if result == None:
        data = 0
    else:
        sid, st, sr, ss = result
        data = dict(sid=sid, st=st, sr=sr, ss=ss)
        prev = True
    if request.method == "GET":
        return render_template("complain.html", data=data)
    else:
        servicetype = request.form.get('service')
        complain = request.form['complainbody'][2:]
        c.execute('select serviceid from service order by serviceid desc limit 1')
        sid = c.fetchone()
        if sid == None:
            sid = 1
        else:
            sid = int(sid[0]) + 1
        status = "Processing"
        if prev:
            flash("Sorry, but we can only process one complain at a time. You have an existing unserviced complaint.")
            return redirect(url_for('displayComplains'))
        else:
            print "insering new service"
            c.execute('insert into service values (?,?,?,?,?)',
                      (sid, USERID, servicetype, complain, status))
            c.execute('update customers set complain = ? where custid = ?',
                      ("True", USERID))
            conn.commit()
            return redirect(url_for('displayComplains'))


@app.route('/feedback', methods=['POST', 'GET'])
@login_required
def getFeedback():
    if request.method == 'GET':
        return render_template('feedback.html')
    else:
        feedback = request.form['feedbackbody'][2:]
        c.execute('select feedbackid from feedback order by feedbackid desc limit 1')
        fid = c.fetchone()
        if fid == None:
            fid = 1
        else:
            fid = int(fid[0]) + 1
        c.execute('insert into feedback values (?,?,?)', (fid, USERID, feedback))
        conn.commit()
        flash("Thank you for your feedback!")
        return redirect(url_for('getFeedback'))


if __name__ == "__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 4411)))
