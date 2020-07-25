from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import pdb
import os

app = Flask(__name__)
app.secret_key = b'helloworld'

host = '127.0.0.1'
user = 'root'
passwd = ''
dbname= 'COVID_Database'

def connect_to_xampp(host,user,passwd,dbname):
    connection = None
    try:
        connection = mysql.connector.connect(host=host,user=user,passwd=passwd,autocommit=True)
    except mysql.connector.Error as E:
        print(E)
    return connection
def connect_to_db(con,dbname):
    csr = con.cursor()
    csr.execute("use " + dbname)
    con.commit()

def create_tables():
    createScript = open(os.path.join('..','COVID_Table.sql'))
    sqlCmds = " ".join(createScript.readlines())
    csr = con.cursor()
    for res in csr.execute(sqlCmds,multi=True):
        pass
    con.commit()
def load_tables():
    global con
    connect_to_db(con,dbname)
    path_table = [('county_jul','county'),('hospital','hospital'),('login','login'),('patients_july','patient'),('case','case_no')]
    for i in path_table:
        county_path = os.path.join(os.getcwd(), '..',i[0]+'.csv')
        county_path = county_path.replace(r"/mnt/c", r"C:")
        if(i[1] is not 'patient'):
            load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' IGNORE 1 LINES;".format(county_path,i[1])
        else:
            load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' IGNORE 1 LINES (patient_id, name, address,@dummy, @dummy, @dummy, phone, admitted, discharged, county_id, health_info, age,race,gender);".format(county_path,i[1])
        csr = con.cursor()
        csr.execute(load_data_query)
        con.commit()
def database_created():
    csr = con.cursor()
    csr.execute("SHOW DATABASES LIKE '" + dbname +"';")
    res = csr.fetchall()
    return len(res)!=0

def return_query(query):
    global con
    csr = con.cursor()
    csr.execute(query)
    return csr.fetchall()

con = connect_to_xampp(host,user,passwd,dbname)
if not database_created():
    create_tables()
    load_tables()
connect_to_db(con,dbname)

@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['usr'] = request.form['usr']
    return render_template('home.html')
    
@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/test')
def test():
    strbuilder = ""
    return render_template('test.html')

@app.route('/logout')
def logout():
    session.pop('usr',None)
    return redirect(url_for('home'))

@app.route('/somewhere_else',methods=['POST'])
def results_page():
    if request.method == 'POST':
        tblname = request.form['tablename']
        qry = "select * from " + tblname +";"
        res = return_query(qry)
        return render_template('results.html',res=res,name=tblname);
