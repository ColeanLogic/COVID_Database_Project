from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
import pdb
import os
from forms import PatientForm, PatientLocateForm, PatientSearchForm, CaseForm, CaseLocateForm
from database_class import Database
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.secret_key = b'helloworld'

host = '192.168.64.2'
user = 'cassie'
passwd = 'cassie'
dbname= 'coviddb'

db = Database(host, user, passwd, dbname)

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
@app.route('/patient_create', methods=['GET', 'POST'])
def patient_create():
    global con
    patient_form_create = PatientForm()
    if patient_form_create.validate_on_submit():
        form_data = patient_form_create.data 
        qry = "INSERT INTO patient (patient_id, name, address_street, address_city, address_state, address_zip, county_id, phone, age, admitted, discharged, race, gender, health_info) VALUES ("       
        numeric_data = ('patient_id', 'county_id', 'age')
        for key, value in form_data.items():
            if key != 'submit' and key != 'csrf_token':    
                if value == None:
                    if key == 'admitted' or key == 'discharged':
                        qry = qry + f"NULL, "
                    else:
                        qry = qry + f"'NULL', "
                else:
                    if key in numeric_data:
                        qry = qry + f"{value}, "
                    else:
                        qry = qry + f"'{value}', "
            else:
                continue
        qry = qry[:-2]
        qry = qry + ")"
        csr = con.cursor()
        csr.execute(qry)
        return redirect(f'/patient_created/{patient_form_create.patient_id.data}.html')
    return render_template('patient_create.html', template_form = patient_form_create)

@app.route('/patient_created/<new_patient_id>', methods=['GET', 'POST'])
def patient_created(new_patient_id):
    qry = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    res = return_query(qry)
    return render_template('patient_created.html', res=res)

@app.route('/patient_locate', methods=['GET', 'POST'])
@app.route('/patient_locate/<status>', methods=['GET', 'POST'])
def patient_locate(status=""):
    global con
    patient_locate_form = PatientLocateForm()
    if patient_locate_form.validate_on_submit():
        patient_id = patient_locate_form.patient_id.data
        qry = f"SELECT * FROM patient WHERE patient_id = '{patient_id}'"
        res = return_query(qry)
        if (res):
            patient_form_update = PatientForm()
            patient_form_update.name.data = res[0][1]
            patient_form_update.phone.data = res[0][2]
            patient_form_update.admitted.data = res[0][3]
            patient_form_update.discharged.data = res[0][4]
            patient_form_update.county_id.data = res[0][5]
            patient_form_update.health_info.data = res[0][6]
            patient_form_update.age.data = res[0][7]
            patient_form_update.race.data = res[0][8]
            patient_form_update.gender.data = res[0][9]
            patient_form_update.address_street.data = res[0][10]
            patient_form_update.address_city.data = res[0][11]
            patient_form_update.address_state.data = res[0][12]
            patient_form_update.address_zip.data = res[0][13]
            return render_template(f'/patient_update.html', res = res, template_form = patient_form_update)
        else:
            status='not_found'
            return redirect(f'patient_locate/{status}')
    return render_template('patient_locate.html', template_form = patient_locate_form, status = status)

@app.route('/patient_update', methods=['GET', 'POST'])
def patient_update():    
    patient_form_update = PatientForm()
    if patient_form_update.validate_on_submit():
        form_data = patient_form_update.data
        qry = "UPDATE patient SET "         
        numeric_data = ('patient_id', 'county_id', 'age')
        for key, value in form_data.items():
            if key != 'submit' and key != 'csrf_token' and key != 'patient_id':    
                if value == None:
                    if key == 'admitted' or key == 'discharged':
                        qry = qry + f"{key} = NULL, "
                    else:
                        qry = qry + f"{key} = 'NULL', "
                else:
                    if key in numeric_data:
                        qry = qry + f"{key} = {value}, "
                    else:
                        qry = qry + f"{key} = '{value}', "
            else:
                continue
        qry = qry[:-2]
        qry = qry + f" WHERE patient_id = {form_data['patient_id']};"
        csr = con.cursor()
        csr.execute(qry)
        return redirect(f'/patient_updated/{patient_form_update.patient_id.data}.html')
    return render_template('patient_update.html', template_form = patient_form_update)

@app.route('/patient_updated/<new_patient_id>', methods=['GET', 'POST'])
def patient_updated(new_patient_id):
    qry = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    res = return_query(qry)
    return render_template('patient_updated.html', res=res)

@app.route('/patient_view', methods=['GET', 'POST'])
def patient_view():
    patient_form_view = PatientSearchForm()
    if patient_form_view.validate_on_submit():
        form_data = patient_form_view.data
        if len(form_data) > 2:
            qry = "SELECT * FROM patient WHERE "
            numeric_data = ('patient_id', 'county_id', 'age')
            for key, value in form_data.items():
                if key != 'submit' and key != 'csrf_token':    
                    if value :
                        if key in numeric_data:
                            qry = qry + f"{key} = {value} AND "
                        else:
                            qry = qry + f"{key} = '{value}' AND "
                else:
                    continue
            qry = qry[:-4]
            qry = qry + ";"
            res = return_query(qry)
            return render_template('/patient_view_results.html', res=res)     
    return render_template('patient_view.html', template_form = patient_form_view)

# Case routes
@app.route('/case_create', methods=['GET', 'POST'])
def case_create():
    global db
    case_form_create = CaseForm()
    if case_form_create.validate_on_submit():
        form_data = case_form_create.data 
        qry = db.case_insert_sql(form_data)
        db.insert(qry)
        return redirect(f'/case_created/{case_form_create.case_id.data}')
    return render_template('case_create.html', template_form = case_form_create)

@app.route('/case_created/<new_case_id>', methods=['GET', 'POST'])
def case_created(new_case_id):
    global db
    form_data = {'case_id': f'{new_case_id}'}
    qry = db.case_select_sql(form_data)
    res = return_query(qry)
    return render_template('case_created.html', res=res)

@app.route('/case_locate', methods=['GET', 'POST'])
@app.route('/case_locate/<status>', methods=['GET', 'POST'])
def case_locate(status = ""):
    global db
    case_locate_form = CaseLocateForm()
    if case_locate_form.validate_on_submit():
        case_id = case_locate_form.case_id.data
        case_form_update = db.case_locate(case_id)
        if not case_form_update:
            status='not_found'
            return redirect(f'case_locate/{status}')
        else:
            return render_template(f'/case_update.html', template_form = case_form_update)
    return render_template('case_locate.html', template_form = case_locate_form)


# @app.route('/patient_locate', methods=['GET', 'POST'])
# @app.route('/patient_locate/<status>', methods=['GET', 'POST'])
# def patient_locate(status=""):
#     global con
#     patient_locate_form = PatientLocateForm()
#     if patient_locate_form.validate_on_submit():
#         patient_id = patient_locate_form.patient_id.data
#         qry = f"SELECT * FROM patient WHERE patient_id = '{patient_id}'"
#         res = return_query(qry)
#         if (res):
#             patient_form_update = PatientForm()
#             patient_form_update.name.data = res[0][1]
#             patient_form_update.phone.data = res[0][2]
#             patient_form_update.admitted.data = res[0][3]
#             patient_form_update.discharged.data = res[0][4]
#             patient_form_update.county_id.data = res[0][5]
#             patient_form_update.health_info.data = res[0][6]
#             patient_form_update.age.data = res[0][7]
#             patient_form_update.race.data = res[0][8]
#             patient_form_update.gender.data = res[0][9]
#             patient_form_update.address_street.data = res[0][10]
#             patient_form_update.address_city.data = res[0][11]
#             patient_form_update.address_state.data = res[0][12]
#             patient_form_update.address_zip.data = res[0][13]
#             return render_template(f'/patient_update.html', res = res, template_form = patient_form_update)
#         else:
#             status='not_found'
#             return redirect(f'patient_locate/{status}')
#     return render_template('patient_locate.html', template_form = patient_locate_form, status = status)