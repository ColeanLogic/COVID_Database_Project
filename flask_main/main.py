from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import pdb
import os
from forms import PatientFormCreate, HospitalFormCreate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = b'helloworld'

host = 'localhost'
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
        if(i[1] != 'patient'):
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

# Connect to mysql database, create database if not created yet
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
        return render_template('results.html',res=res,name=tblname)

@app.route('/hooray', methods=['GET', 'POST'])
def hooray():
    return render_template('hooray.html')

# Patient Routes
@app.route('/patient_created/<new_patient_id>', methods=['GET', 'POST'])
def patient_created(new_patient_id):
    qry = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    res = return_query(qry)
    return render_template('patient_created.html', res=res)

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


#The following lines of code are detain the creation of a hospital
@app.route('/hospital_created/<new_hospital_id>', methods=['GET', 'POST'])
def hospital_created(new_hospital_id):
    qry = f'''SELECT * FROM hospital WHERE hospital_id = "{new_hospital_id}"'''
    res = return_query(qry)
    return render_template('hospital_created.html', res=res)

@app.route('/hospital_create', methods=['GET', 'POST'])
def hospital_create():
    global con
    hospital_form_create = HospitalFormCreate()
    if hospital_form_create.validate_on_submit():
        new_hospital_id = hospital_form_create.hospital_id.data
        new_name = hospital_form_create.name.data
        new_county_id = hospital_form_create.county_id.data
        qry = f'''INSERT INTO hospital (hospital_id, name, county_id) VALUES ({new_hospital_id},"{new_name}","{new_county_id}");'''
        csr = con.cursor()
        csr.execute(qry)
        return redirect(f'/hospital_created/{new_hospital_id}.html')
    return render_template('hospital_create.html', template_form=hospital_form_create)

