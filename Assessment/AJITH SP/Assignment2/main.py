from urllib import request
from flask import Flask,render_template
import ibm_db

app = Flask(__name__)


conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCa.crt;UID=ffp29290;pwd=ayzYtEguiWUQva81",'','')

createQuery="create Table USER (FIRST_NAME VARCHAR(20),LAST_NAME VARCHAR(20),EMAIL VARCHAR(50),COUNTRY VARCHAR(20),ADDRESS VARCHAR(100),CITY VARCHAR(20),STATE VARCHAR(20),PIN_CODE INTEGER)"
create_table = ibm_db.exec_immediate(conn, createQuery)

@app.route('/')
def first():
    return render_template("index.html")

@app.route('/post',methods=["POST"])
def post():
    fname=request.form["fname"]
    lname=request.form["lname"]
    email=request.form["email"]
    country=request.form["country"]
    address=request.form["address"]
    city=request.form["city"]
    state=request.form["state"]
    zip=request.form["zip"]
    
    insertQuery = "insert into USER values({fname},{lname},{email},{country},{address},{city},{state},{zip})"
    insert_table = ibm_db.exec_immediate(conn, insertQuery)
    
    return render_template("login.html")

@app.route('/aboutpage')
def page():
    email = request.form["email"]
    emailquery="SELECT EMAIL FROM USER WHERE EMAIL={email}"
    table = ibm_db.exec_immediate(conn,emailquery)
    if(email== table):
        return render_template("mainindex.html")
    else:    
        return render_template("index.html")

@app.route('/index')
def start():
    return render_template("index.html")

if(__name__)=="__main__":
    app.run(debug=True)