from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import pdb
import os
from pymongo import MongoClient
from database_abstraction_classes import *

app = Flask(__name__)
app.secret_key = b'helloworld'

host = '127.0.0.1'
mongo_host = '127.0.0.1'
mongo_port = '20717'
user = 'root'
passwd = ''
dbname= 'COVID_Database'
mongo_con = None

def connect_to_xampp(host,user,passwd,dbname):
    connection = None
    try:
        connection = mysql.connector.connect(host=host,user=user,passwd=passwd,autocommit=True,database=dbname)
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
    
def connect_to_mongodb():
    client = MongoClient('mongodb://127.0.0.1:27017');#MongoClient("mongodb://" + mongo_host+':'+mongo_port)
    global mongo_con
    if(mongo_con != None):
        #already connected
        return 
    exists = False
    for db in client.list_databases():
        if db["name"] == "covid_db":
          exists = True
    if(exists==False):
        raise Exception("You do not have a covid_db in your list of databases")
    mongo_con = client.covid_db
    return

con = connect_to_xampp(host,user,passwd,dbname)
if not database_created():
    create_tables()
    load_tables()
connect_to_db(con,dbname)
connect_to_mongodb()

#here we have mongodb conn to covid_db and a sql conn to covid_db.
DataBaseFactory.mongo_conn = mongo_con
DataBaseFactory.sql_conn = con
DataBaseFactory.databaseType = DBTYPE.SQL

@app.route('/switch_db')
def switch_db():
    if "use_mongo" in session:
        DataBaseFactory.databaseType = DBTYPE.SQL
        session.pop('use_mongo',None)
    else:
        session['use_mongo'] = True
        connect_to_mongodb()
        DataBaseFactory.databaseType = DBTYPE.MongoDB
    return redirect(url_for('home'))

@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['usr'] = request.form['usr']
        session['role'] = DataBaseFactory.GetDataBaseObject().getRole(session['usr'])
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
    session.pop('role',None)
    return redirect(url_for('home'))

@app.route('/somewhere_else',methods=['POST'])
def results_page():
    if request.method == 'POST':
        tblname = request.form['tablename']
        res = DataBaseFactory.GetDataBaseObject().selectAllFromEntity(tblname)
        return render_template('results.html',res=res,name=tblname);

type1 = ""
status =""
demographic = ""

@app.route('/chart',methods=['GET','POST'])
def chart_page():
    global type1
    global status
    global demographic
    use_old_values = False
    dataList = None
    successfulUpdate = None
    if request.method == 'POST':
        fieldsToShow = ""
        if "showFields" in request.form:
            use_old_values = True
            fieldsToShow = request.form['showFields']
            dataList = DataBaseFactory.GetDataBaseObject().selectDataFromSummary(status,fieldsToShow)
        if "idToUpdate" in request.form:
            use_old_values = True
            idtoupdate = request.form['idToUpdate']
            attr = request.form['attrToUpdate']
            newVal = request.form['newValue']
            DataBaseFactory.GetDataBaseObject().updateEntity(idtoupdate,"",attr,newVal)
        if not use_old_values:
            status = request.form['cases']
        chart_data = {}
        if not use_old_values:
            demographic = request.form['by']
        #statuses = mongo_con.cases.find({},{'status':1,'id':0}).distinct('status')
        demographics = []
        if not use_old_values:
            type1 = request.form['type']
        if "age" in demographic:
            demographics = [10,20,30,40,50,60,70]
            for dem in demographics:
                #DataBaseFactory.GetDataBaseObject().summarizeStatusFromDemographic(st)
                total = mongo_con.cases.find({"$and":[{'status':status},{'patient_info.' + demographic:dem}]}).count()
                chart_data[dem] = total
        else:
            demographics = mongo_con.cases.find({},{'patient_info.'+demographic:1,'id':0}).distinct('patient_info.' + demographic)
            for dem in demographics:
                total = DataBaseFactory.GetDataBaseObject().summarizeStatusFromDemographic(status,demographic,dem)
                print(total)
                chart_data[dem] = total
        return render_template('chart.html',dems=demographics,chart_data=chart_data,type1=type1,status=status,category=demographic,dataList=dataList,successfulUpdate=successfulUpdate)
    return render_template('chart.html',chart_data=None,type1=type1)
