from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import pdb
import os
from pymongo import MongoClient
from forms import PatientFormCreate
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired

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

def connect_to_db(con,dbname):
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


@app.route('/somewhere_else',methods=['POST'])
def results_page():
    if request.method == 'POST':
        tblname = request.form['tablename']
        qry = "select * from " + tblname + ";"
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

