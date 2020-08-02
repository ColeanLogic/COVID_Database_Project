from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import pdb
import os
import sys
# from forms import PatientFormCreate
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, TextAreaField, RadioField
# from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = b'helloworld'

host = '127.0.0.1'
# mongo_host = '127.0.0.1'
# mongo_port = '20717'
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
    path_table = [('county_jan_to_april','county'),('county_may','county'),('county_jun','county'),('county_jul','county'),('hospital','hospital'),('login','login'),('patients_april','patient'),('patients_may','patient'),('patients_june','patient'),('patients_july','patient'),('patients_march','patient'),('case','case_no')]
    for i in path_table:
        county_path = os.path.join(os.getcwd(), '..',i[0]+'.csv')
        county_path = county_path.replace(r"/mnt/c", r"C:")
        if(i[1] != 'patient'):
            load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' IGNORE 1 LINES;".format(county_path,i[1])
        else:
            load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' IGNORE 1 LINES (patient_id, name, address_street, address_city, address_state, address_zip, phone, admitted, discharged, county_id, health_info, age,race,gender);".format(county_path,i[1])
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

# this is the inster data query
def insert_query(query):
    global con
    csr = con.cursor()
    csr.execute(query)

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
    mongo_con = client.covid_db;
    return

# pdb.set_trace()
con = connect_to_xampp(host,user,passwd,dbname)
# mongo_con = None
if not database_created():
    create_tables()
    load_tables()
connect_to_db(con,dbname)
# connect_to_mongodb()
@app.route('/switch_db')
def switch_db():
    if "use_mongo" in session:
        session.pop('use_mongo',None)
    else:
        session['use_mongo'] = True
        connect_to_mongodb()
    return redirect(url_for('home'));

@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['usr'] = request.form['usr']
    return render_template('home.html')
    
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form ['usr']
        password = request.form ['pass']
        qry = f'''SELECT * FROM login WHERE username="{username}";'''
        res = return_query(qry)

        print(res, file=sys.stderr)
        session['usr'] = None
        if len(res) == 0:
            print("Incorrect username", file=sys.stderr)
            return render_template('pass_fail.html')
        elif res[0][1] != password: # This makes assumptions and is kinda yicky
            print("Incorrect password", file=sys.stderr)
            return render_template('usr_fail.html')
        else:
            session['usr'] = username
        return redirect(url_for('home'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        session['usr'] = request.form['usr']
        username = request.form ['usr']
        password = request.form ['pass']
        role = request.form ['role']
        qry = f'''INSERT INTO login VALUES ("{username}","{password}","{role}");'''
        res = insert_query(qry)
        return redirect(url_for('home'))

    return render_template('register.html')

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
        
@app.route('/chart',methods=['GET','POST'])
def chart_page():
    type1 = ""
    if request.method == 'POST':
        status = request.form['cases']
        chart_data = {}
        demographic = request.form['by']
        statuses = mongo_con.cases.find({},{'status':1,'id':0}).distinct('status')
        demographics = []
        type1 = request.form['type']
        if "age" in demographic:
            demographics = [10,20,30,40,50,60,70]
            for dem in demographics:
                total = mongo_con.cases.find({"$and":[{'status':status},{'patient_info.' + demographic:dem}]}).count()
                chart_data[dem] = total
        else:
            demographics = mongo_con.cases.find({},{'patient_info.'+demographic:1,'id':0}).distinct('patient_info.' + demographic)
            for dem in demographics:
                total = mongo_con.cases.find({"$and":[{'status':status},{'patient_info.' + demographic:dem}]}).count()
                chart_data[dem] = total
        return render_template('chart.html',dems=demographics,chart_data=chart_data,type1=type1)
    return render_template('chart.html',chart_data=None,type1=type1)

@app.route('/patient_create', methods=['GET', 'POST'])
def patient_create():
    global con
    patient_form_create = PatientFormCreate()
    if patient_form_create.validate_on_submit():
        new_patient_id = patient_form_create.patient_id.data
        new_name = patient_form_create.name.data
        new_address_street = patient_form_create.address_street.data
        new_address_city = patient_form_create.address_city.data
        new_address_state = patient_form_create.address_state.data
        new_address_zip = patient_form_create.address_zip.data
        new_county_id = patient_form_create.county_id.data
        new_phone = patient_form_create.phone.data
        new_age = patient_form_create.age.data
        new_race = patient_form_create.race.data
        new_gender = patient_form_create.gender.data
        new_health_info = patient_form_create.health_info.data
        new_admitted = patient_form_create.admitted.data
        new_discharged = patient_form_create.discharged.data
        qry = f'''INSERT INTO patient (patient_id, name, address_street, address_city, address_state, address_zip, county_id, phone, age, race, gender, health_info, admitted, discharged) VALUES ({new_patient_id},"{new_name}","{new_address_street}","{new_address_city}","{new_address_state}","{new_address_zip}","{new_county_id}","{new_phone}", "{new_age}","{new_race}","{new_gender}","{new_health_info}","{new_admitted}","{new_discharged}");'''
        csr = con.cursor()
        csr.execute(qry)
        return redirect(f'/patient_created/{new_patient_id}.html')
    return render_template('patient_create.html', template_form=patient_form_create)
