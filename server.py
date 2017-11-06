from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import sqlite3
import random
import os
import subprocess
import webbrowser as wb

# collect thumbnails and images for css
# make a home page template
# make statistics module


USER = None
USERID = None
conn = sqlite3.connect('/Users/souravjohar/Documents/Code/water-management-system/water1.db')
c = conn.cursor()

app = Flask(__name__)

app.secret_key = 'lolol'
URL = "file:///Users/souravjohar/Documents/Code/water-management-system/home/index.html"


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and USER != None:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('cuslogin'))
    return wrap


def emplogin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and USER != None:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('emplogin'))
    return wrap


@app.route('/')
def home():
    wb.open(URL, new=1)
    return render_template("main.html")


@app.route('/cus/', methods=['GET', 'POST'])
@login_required
def cushome():
    if request.method == 'POST':
        pass
    else:
        c.execute("select custid from userlogin where username = '{}'".format(USER))
        global USERID
        try:
            USERID = c.fetchone()[0]
        except:
            pass
        c.execute("select firstname, lastname from customers where custid = '{}'".format(USERID))
        f, l = c.fetchone()
        d_name = f + " " + l
        try:
            c.execute("select pendingamount from billing where custid = '{}'".format(USERID))
            due_amt = c.fetchone()[0]
        except:
            due_amt = 0
        return render_template('index.html', d_name=d_name, due_amt=due_amt)


@app.route('/cus/bill')
@login_required
def showBill():
    c.execute("select pendingamount, duedate, fine from billing where custid = '{}'".format(USERID))
    try:
        due_amt, due_date, fine = c.fetchone()
    except:
        due_amt = 0
        due_date = "dunno"
        fine = 0
    total = int(due_amt) + int(fine)
    c.execute("update billing set pendingamount = 0 where custid = '{}'".format(USERID))
    c.execute("update billing set duedate = '10-8-2018' where custid = '{}'".format(USERID))
    c.execute("update billing set lastpmtdate = '08-11-2017' where custid = '{}'".format(USERID))
    conn.commit()
    return render_template('bill.html', due_amt=due_amt, due_date=due_date, fine=fine, total=total)


@app.route('/cus/login', methods=['GET', 'POST'])
def cuslogin():
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
                return redirect(url_for('cushome'))
            else:
                error = 'Invalid Credentials. Please try again.'
        except Exception as e:
            print str(e)
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


@app.route('/cus/logout')
@login_required
def cuslogout():
    session.pop('logged_in', None)
    USER = None
    flash('You were logged out.')
    return redirect(url_for('cuslogin'))


@app.route('/cus/profile')
@login_required
def displayProfile():
    c.execute("select firstname, lastname, address, areaid from customers where custid = '{}'".format(USERID))

    f, l, a, aid = c.fetchone()
    print a, aid
    p = "Not Provided"
    area = "Not Provided"
    try:
        c.execute("select areaname from area where areaid = '{}'".format(aid))
        area = c.fetchone()[0]
        c.execute("select phone from phone where custid = '{}'".format(USERID))
        p = c.fetchone()[0]
    except:
        pass

    data = dict(firstname=f, lastname=l, phone=p, address=a, area=area)
    return render_template("profile.html", data=data)


@app.route('/cus/connection', methods=['GET', 'POST'])
@login_required
def displayConn():
    try:
        c.execute(
            "select waterallowance, connectiontype, address,areaid from customers where custid = '{}'".format(USERID))
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
    except:
        if request.method == 'GET':
            return render_template('newconnection.html')
        else:
            phone = int(request.form['phone'])
            address = request.form['address']
            areaid = request.form.get('area')
            type = request.form.get('type')
            if type == "Pipeline - Unlimited":
                litres = 'unlimited'
            else:
                litres = request.form['litres']
            newconnection(phone, address, areaid, type, litres)
            flash('Congratulations on your new connection!')
            # make payment page
            return redirect(url_for('displayConn'))


@app.route('/cus/updateplan', methods=['GET', 'POST'])
@login_required
def updatePlan():
    if request.method == 'GET':
        return render_template('updateplan.html')
    else:
        address = request.form['address']
        areaid = request.form.get('area')
        type = request.form.get('type')
        if type == "Pipeline - Unlimited":
            litres = 'unlimited'
        else:
            litres = request.form['litres']
        newconnection(None, address, areaid, type, litres)
        # make payment page
        flash('Plan changed successfully!')
        return redirect(url_for('displayConn'))


@app.route('/cus/complain', methods=['GET', 'POST'])
@login_required
def displayComplains():
    prev = None
    c.execute(
        "select serviceid, servicetype, servicerequest, servicestatus from service where custid = '{}'".format(USERID))
    try:
        result = c.fetchall()[-1]
    except:
        result = None
    if result == None:
        data = 0
    else:
        sid, st, sr, ss = result
        data = dict(sid=sid, st=st, sr=sr, ss=ss)
        if ss == "Processing":
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


@app.route('/cus/feedback', methods=['POST', 'GET'])
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


@app.route('/cus/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        pword = request.form['password']
        c.execute("select pword from userlogin where username = '{}'".format(email))

        error1 = None
        error2 = None
        error3 = None
        error4 = None

        if c.fetchone() is not None:
            error1 = "Email already exists"
        if len(fname) == 0:
            error2 = "First Name cannot be empty"
        if len(lname) == 0:
            error3 = "Last Name cannot be empty"
        if len(pword) <= 5:
            error4 = "Password must be more than 5 characters long"
        if error1 or error2 or error3 or error4:
            if str(error1) != 'None':
                flash(error1)
            if str(error2) != 'None':
                flash(error2)
            if str(error3) != 'None':
                flash(error3)
            if str(error4) != 'None':
                flash(error4)
            return render_template('signup.html')
        else:
            newCustomer(email, fname, lname, pword)
            flash("Account created! You can now login with your new credentials.")
            return redirect(url_for('cuslogin'))


'''employee side'''


@app.route('/emp/', methods=['GET', 'POST'])
@emplogin_required
def emphome():
    if request.method == 'POST':
        pass
    else:
        c.execute("select firstname, lastname from employee where empid = '{}'".format(USER))
        f, l = c.fetchone()
        d_name = f + " " + l
        return render_template('empindex.html', d_name=d_name)


@app.route('/emp/emplogin', methods=['GET', 'POST'])
def emplogin():
    error = None
    if request.method == 'POST':
        r_username = request.form['username']
        r_pass = request.form['password']
        try:
            c.execute("select password from emplogin where empid = '{}'".format(r_username))
            pword = c.fetchall()[0][0]
            if pword == r_pass:
                session['logged_in'] = True
                global USER
                USER = r_username
                return redirect(url_for('emphome'))
            else:
                error = 'Invalid Credentials. Please try again.'
        except Exception as e:
            print (str(e))
            error = 'Invalid Credentials. Please try again.'
    return render_template('emplogin.html', error=error)


@app.route('/emp/emplogout')
@emplogin_required
def emplogout():
    session.pop('logged_in', None)
    USER = None
    flash('You were logged out.')
    return redirect(url_for('emplogin'))


@app.route('/emp/empcomplain', methods=['GET', 'POST'])
@emplogin_required
def empcomplain():
    prev = None
    c.execute(
        "select custid, serviceid, servicetype, servicerequest, servicestatus from service where servicestatus not in ('procesed', 'Processed')")
    result = c.fetchall()
    if request.method == "GET":
        return render_template("empcomplain.html", data=result, length=len(result))
    else:
        r_complainid = request.form['complainNo']
        try:
            c.execute(
                "update service set servicestatus = 'Processed' where serviceid = '{}'".format(r_complainid))
            conn.commit()
        except Exception as e:
            print (str(e))
            error = 'Error trying to service this request.'
        return redirect(url_for('empcomplain'))


@app.route('/emp/empprofile', methods=['GET', 'POST'])
@emplogin_required
def empprofile():
    c.execute("select * from employee where empid = '{}'".format(USER))
    result = c.fetchone()
    empid = result[0]
    firstname = result[1]
    lastname = result[2]
    phone = result[3]
    sex = result[4]
    designation = result[5]
    deptid = result[6]
    salary = result[7]
    c.execute("select deptname from department where deptid = '{}'".format(deptid))
    deptname = c.fetchone()[0]
    data = dict(firstname=firstname, lastname=lastname, phone=phone,
                designation=designation, deptname=deptname, salary=salary)
    if request.method == "GET":
        return render_template("empprofile.html", data=data)


@app.route('/emp/empcustomer', methods=['GET', 'POST'])
@emplogin_required
def empcustomer():
    c.execute("select deptid from employee where empid = '{}'".format(USER))
    deptid = c.fetchone()[0]
    if deptid != 'dep1' and deptid != 'dep2':
        flash("You are not authorized to access the Customer Database.")
        return redirect(url_for('emphome'))
    else:
        if request.method == 'POST':
            custid = request.form['CustomerID']
            c.execute(
                "select firstname,lastname,address,areaid,connectiontype,waterallowance from customers where custid = '{}'".format(custid))
            firstname, lastname, address, areaid, connectiontype, waterallowance = c.fetchone()
            c.execute("select areaname from area where areaid = '{}'".format(areaid))
            area = c.fetchone()[0]
            c.execute("select phone from phone where custid = '{}'".format(custid))
            phone = c.fetchone()[0]
            c.execute("select supplierid,suppliername from supplier where areaid = '{}'".format(areaid))
            supplierid, suppliername = c.fetchone()
            c.execute("select vehicleid from transport where supplierid = '{}'".format(supplierid))
            vid = c.fetchone()[0]
            c.execute(
                "select pendingamount, duedate,lastpmtdate,fine from billing where custid = '{}'".format(custid))
            pendingamount, duedate, lastpdate, fine = c.fetchone()
            if connectiontype != 'Water Lorry':
                vid = "NA"

            data = dict(vid=vid, suppliername=suppliername, firstname=firstname, lastname=lastname, phone=phone, address=address, area=area,
                        connectiontype=connectiontype, waterallowance=waterallowance, pendingamount=pendingamount, duedate=duedate, lastpdate=lastpdate, fine=fine)
            return render_template("empcustomer.html", data=data)
        else:
            data = dict(phone=0)
            return render_template("empcustomer.html", data=data)


@app.route('/emp/empfeedback')
@emplogin_required
def empfeedback():
    c.execute("select *  from feedback")
    feedback = c.fetchall()
    return render_template("empfeedback.html", data=feedback, length=len(feedback))


'''general functions'''


def newCustomer(email, fname, lname, pword):
    c.execute('select count(*) from customers')
    count = int(c.fetchone()[0])
    custid = "c" + str(count + 1)
    c.execute("insert into customers(custid,firstname, lastname, address,connectiontype) values(?,?,?,?,?)",
              (custid, fname, lname, "Not Provided", "Not Provided"))
    c.execute("insert into userlogin values(?,?,?)", (email, pword, custid))
    conn.commit()


def newconnection(phone, address, areaid, type, litres):
    if phone != None:
        c.execute(
            "insert into phone values('{}',{})".format(USERID, phone))
    c.execute(
        "update customers set address = '{}' where custid = '{}'".format(address, USERID))
    c.execute(
        "update customers set areaid = '{}' where custid = '{}'".format(areaid, USERID))
    c.execute(
        "update customers set connectiontype = '{}' where custid = '{}'".format(type, USERID))
    c.execute(
        "update customers set waterallowance = '{}' where custid = '{}'".format(litres, USERID))
    c.execute(
        "update area set connections = connections + 1 where areaid = '{}'".format(areaid))
    conn.commit()


if __name__ == "__main__":
    try:
        procs = subprocess.check_output(["lsof", "-i", ":5000"])
        procs = procs.split()
        pid = procs[procs.index('Python') + 1]
        print pid
        os.system('kill {}'.format(pid))
        print "killed"
    except:
        pass
    app.run(host="0.0.0.0")
