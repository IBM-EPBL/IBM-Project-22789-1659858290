from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

app = Flask(__name__)
app.secret_key = "ibm"

hostname = "ea286ace-86c7-4d5b-8580-3fbfa46b1c66.bs2io90l08kqb1od8lcg.databases.appdomain.cloud"
uid = "jbd44427"
pwd = "bbyhN0MEdJ6mIj7t"
driver = "{IBM DB2 ODBC DRIVER}"
db = "bludb"
port = "31505"
protocol = "TCPIP"
cert = "DigiCertGlobalRootCA.crt"


dsn = (
    "DATABASE={0};"
    "HOSTNAME={1};"
    "PORT={2};"
    "UID={3};"
    "SECURITY=SSL;"
    "SSLServerCertificate={4};"
    "PWD={5};"
).format(db, hostname, port, uid, cert, pwd)

print(dsn)

conn = ibm_db.connect(dsn, "", "") 

message = ""

@app.route('/', methods=['GET', 'POST'])
def home():
    print(session)
    print("Message - " + message)
    if session:
        if session["loggedin"]:
            return redirect(url_for('tracker'))
    else:
        login_page = True
        print(request.values.get('page'))
        if request.values.get('page') == "register":
            login_page = False
        return render_template('index.html', login=login_page, message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        global message

        user = request.form
        print(user)
        email = user["email"]
        passwrd = user["passwrd"]

        print("Email - " + email + ", Password - " + passwrd)

        sql = "SELECT * FROM users WHERE email = ? AND pass = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, passwrd)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        print("Account - ")
        print(account)

        if account:
            session['loggedin'] = True
            session['id'] = account['EMAIL']
            user_email = account['EMAIL']
            session['email'] = account['EMAIL']
            session['name'] = account['NAME']

            return redirect(url_for('tracker'))

        else:
            message = "Incorrect Email or Password"
            return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        global message

        user = request.form
        print(user)
        name = user["name"]
        email = user["email"]
        passwrd = user["passwrd"]

        sql = "SELECT * FROM USERS WHERE email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        print("Account - ", end="")
        print(account)

        if account:
            message = "Account already exists"
            return redirect(url_for('home', page="register"))
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = "Invalid email address"
            return redirect(url_for('home', page="register"))
        elif not re.match(r'[A-Za-z0-9]+', name):
            message = "Name must contain only characters and numbers"
            return redirect(url_for('home', page="register"))
        else:
            insert_sql = "INSERT INTO users VALUES (?, ?, ?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, passwrd)
            ibm_db.execute(prep_stmt)

            session['loggedin'] = True
            session['id'] = email
            user_email = email
            session['email'] = email
            session['name'] = name

            message = ""

            return redirect(url_for('tracker'))


@app.route('/tracker')
def tracker():
    global message
    data = []
    expenses = {"Medical Expenses": 0, "House Expenses": 0, "Education": 0, "Savings": 0, "Others": 0}
    fixlimit=0
    

    if session:
        if session["loggedin"]:
            sql = "SELECT date, transaction, type, amount FROM TRANSACTIONS WHERE email = ?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, session["email"])
            ibm_db.execute(stmt)   

            row = ibm_db.fetch_assoc(stmt)
            while row:
                data.append(row)
                expenses[row["TYPE"]] += row["AMOUNT"]
                row = ibm_db.fetch_assoc(stmt)
                
                
            sql1 = "SELECT LIMIT FROM EXPENSELIMIT WHERE email = ?"
            stmt1 = ibm_db.prepare(conn, sql1)
            ibm_db.bind_param(stmt1, 1, session["email"])
            ibm_db.execute(stmt1)

            dic = ibm_db.fetch_assoc(stmt1)
            avalimit=0
            fixlimit=0
            if dic:
                val_limit = list(dic.values())
                
                sql2 = "select sum(amount) as ta from transactions where email=?"
                stmt2 = ibm_db.prepare(conn,sql2)
                ibm_db.bind_param(stmt2,1,session["email"])
                ibm_db.execute(stmt2)

                dic1 = ibm_db.fetch_assoc(stmt2)
                
                val_ta = list(dic1.values())
                fixlimit = val_limit[0]
                avalimit = val_limit[0]-val_ta[0]
                if(avalimit < 0):
                    print("\n\nFrom add expenditure :",avalimit)
                    send_email()

            print(data)
            print(expenses)
            print(avalimit)

            message = ""

            return render_template('home.html', name=session['name'], data=data[::-1], expenses=expenses,avalimit=avalimit,fixlimit=fixlimit)
    else:
        message = "Session Expired"
    return redirect(url_for("home"))


@app.route('/add-expenditure', methods=['GET', 'POST'])
def add_expenditure():
    if request.method == "POST":
        details = request.form
        print(details)

        date = details["date"][-2:] + "/" + details["date"][5:7] + "/" + details["date"][:4]
        transaction = details["transaction"]
        type = details["type"]
        amount = details["amount"]
        print(date, transaction, type, amount)

        sql = "INSERT INTO transactions VALUES (?, ?, ?, ?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, date)
        ibm_db.bind_param(stmt, 2, transaction)
        ibm_db.bind_param(stmt, 3, type)
        ibm_db.bind_param(stmt, 4, amount)
        ibm_db.bind_param(stmt, 5, session["email"])

        ibm_db.execute(stmt)
        
        sql1 = "SELECT LIMIT FROM EXPENSELIMIT WHERE email = ?"
        stmt1 = ibm_db.prepare(conn, sql1)
        ibm_db.bind_param(stmt1, 1, session["email"])
        ibm_db.execute(stmt1)

        dic = ibm_db.fetch_assoc(stmt1)
        val_limit = list(dic.values())

        sql2 = "select sum(amount) as ta from transactions where email=?"
        stmt2 = ibm_db.prepare(conn,sql2)
        ibm_db.bind_param(stmt2,1,session["email"])
        ibm_db.execute(stmt2)
            
        dic1 = ibm_db.fetch_assoc(stmt2)
        val_ta = list(dic1.values())
        avalimit = val_limit[0]-val_ta[0]
        if(avalimit<0):
            send_email()

        return redirect(url_for('tracker'))
    
    
@app.route('/setLimit', methods=['GET', 'POST'])
def limiter():
    if request.method == "POST":
        details = request.form
        print(details)
        
        limit = details["limit"]
        print(limit)


        sql = "INSERT INTO EXPENSELIMIT VALUES (?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, limit)
        ibm_db.bind_param(stmt, 2, session["email"])
        ibm_db.execute(stmt)

        return redirect(url_for('tracker'))
    
    

@app.route('/changeLimit', methods=['GET', 'POST'])
def changer():
    if request.method == "POST":
        details = request.form
        print(details)
        
        limit = details["limit"]
        print(limit)


        sql = "UPDATE EXPENSELIMIT SET LIMIT=? WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, limit)
        ibm_db.bind_param(stmt, 2, session["email"])
        ibm_db.execute(stmt)

        return redirect(url_for('tracker'))


@app.route('/logout')
def logout():
    print("Logging Out")
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('home'))

def send_email():
    from_email=Email('211719104041@smartinternz.com')
    to_email=To('jayaraj.s.2019.cse@ritchennai.edu.in')
    subject = 'EXPENSE LIMIT EXCEEDED'
    content = Content("text/plain", "You have exceeded your MONTHLY EXPENSE LIMIT\nwith regards\n\t\t PETA-Team")
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        sg = SendGridAPIClient(['SendGridApiKey'])
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)



if __name__ == '__main__':
    app.run(debug=True)
