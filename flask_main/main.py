from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import pdb
import os
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = b'helloworld'

host = '192.168.64.2'
mongo_host = '127.0.0.1'
mongo_port = '20717'
user = 'tom'
passwd = 'tom'
dbname = 'COVID_Database'


def connect_to_xampp(host, user, passwd, dbname):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host, user=user, passwd=passwd, autocommit=True)
    except mysql.connector.Error as E:
        print(E)
    return connection


def connect_to_db(con, dbname):
    csr = con.cursor()
    csr.execute("use " + dbname)
    con.commit()


def create_tables():
    createScript = open(os.path.join('..', 'COVID_Table.sql'))
    sqlCmds = " ".join(createScript.readlines())
    csr = con.cursor()
    for res in csr.execute(sqlCmds, multi=True):
        pass
    con.commit()


def load_tables():
    global con
    connect_to_db(con, dbname)
    path_table = [('county_jul', 'county'), ('hospital', 'hospital'),
                  ('login', 'login'), ('patients_july', 'patient'), ('case', 'case_no')]
    for i in path_table:
        county_path = os.path.join(os.getcwd(), '..', i[0]+'.csv')
        county_path = county_path.replace(r"/mnt/c", r"C:")
        if(i[1] is not 'patient'):
            load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' IGNORE 1 LINES;".format(
                county_path, i[1])
        else:
            load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' IGNORE 1 LINES (patient_id, name, address,@dummy, @dummy, @dummy, phone, admitted, discharged, county_id, health_info, age,race,gender);".format(
                county_path, i[1])
        csr = con.cursor()
        csr.execute(load_data_query)
        con.commit()


def database_created():
    csr = con.cursor()
    csr.execute("SHOW DATABASES LIKE '" + dbname + "';")
    res = csr.fetchall()
    return len(res) != 0


def return_query(query):
    global con
    csr = con.cursor()
    csr.execute(query)
    return csr.fetchall()


def connect_to_mongodb():
    # MongoClient("mongodb://" + mongo_host+':'+mongo_port)
    client = MongoClient('mongodb://127.0.0.1:27017')
    global mongo_con
    if(mongo_con != None):
        # already connected
        return
    exists = False
    for db in client.list_databases():
        if db["name"] == "covid_db":
            exists = True
    if(exists == False):
        raise Exception("You do not have a covid_db in your list of databases")
    mongo_con = client.covid_db
    return


# pdb.set_trace()
con = connect_to_xampp(host, user, passwd, dbname)
mongo_con = None
if not database_created():
    create_tables()
    load_tables()
connect_to_db(con, dbname)
# connect_to_mongodb()


@app.route('/switch_db')
def switch_db():
    if "use_mongo" in session:
        session.pop('use_mongo', None)
    else:
        session['use_mongo'] = True
        connect_to_mongodb()
    return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
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
    session.pop('usr', None)
    return redirect(url_for('home'))


@app.route('/somewhere_else', methods=['POST'])
def results_page():
    if request.method == 'POST':
        tblname = request.form['tablename']
        qry = "select * from " + tblname + ";"
        res = return_query(qry)
        return render_template('results.html', res=res, name=tblname)


@app.route('/chart', methods=['GET', 'POST'])
def chart_page():
    type1 = ""
    if request.method == 'POST':
        status = request.form['cases']
        chart_data = {}
        demographic = request.form['by']
        statuses = mongo_con.cases.find(
            {}, {'status': 1, 'id': 0}).distinct('status')
        demographics = []
        type1 = request.form['type']
        if "age" in demographic:
            demographics = [10, 20, 30, 40, 50, 60, 70]
            for dem in demographics:
                total = mongo_con.cases.find(
                    {"$and": [{'status': status}, {'patient_info.' + demographic: dem}]}).count()
                chart_data[dem] = total
        else:
            demographics = mongo_con.cases.find(
                {}, {'patient_info.'+demographic: 1, 'id': 0}).distinct('patient_info.' + demographic)
            for dem in demographics:
                total = mongo_con.cases.find(
                    {"$and": [{'status': status}, {'patient_info.' + demographic: dem}]}).count()
                chart_data[dem] = total
        return render_template('chart.html', dems=demographics, chart_data=chart_data, type1=type1)
    return render_template('chart.html', chart_data=None, type1=type1)
