from flask import Flask, render_template, request, session, redirect, url_for, flash
from forms import PatientFormCreate, AddCountyData
from datetime import datetime
from database import Database
from database_abstraction_classes import *
import os

# Database Configurations
host = '192.168.64.2'
mongo_host = '127.0.0.1'
mongo_port = '20717'
user = 'tom'
passwd = 'tom'
dbname = 'COVID_Database'
mongo_con = None

db = Database(host, user, passwd, dbname)

# here we have mongodb conn to covid_db and a sql conn to covid_db.
DataBaseFactory.mongo_conn = mongo_con
DataBaseFactory.sql_conn = db.con
DataBaseFactory.databaseType = DBTYPE.SQL

app = Flask(__name__)
app.secret_key = b'helloworld'


@app.route('/switch_db')
def switch_db():
    if "use_mongo" in session:
        DataBaseFactory.databaseType = DBTYPE.SQL
        session.pop('use_mongo', None)
    else:
        session['use_mongo'] = True
        connect_to_mongodb()
        DataBaseFactory.databaseType = DBTYPE.MongoDB
    return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['usr'] = request.form['usr']
        session['role'] = DataBaseFactory.GetDataBaseObject().getRole(
            session['usr'])
        flash('Logged in successfully!', 'success')
    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    message = session['usr'] + " logged out successfully"
    flash(message, 'success')
    session.pop('usr', None)
    return redirect(url_for('home'))


@app.route('/view-table/<table>', methods=['GET'])
def viewTable(table):
    # Retrieve Table Body
    sql = f'''SELECT * FROM {table}'''
    if table == 'county':
        sql = '''SELECT * FROM county ORDER BY county_date DESC LIMIT 1000'''
    body = db.query(sql)

    # Retrieve Table Header
    sql = f'''SHOW COLUMNS FROM {table} '''
    header = db.query(sql)

    return render_template('view-table.html', header=header, body=body, table=table)


@app.route('/view-schema', methods=['GET'])
def viewSchema():
    return render_template('view-schema.html')


@app.route('/test')
def test():
    strbuilder = ""
    return render_template('test.html')


@app.route('/somewhere_else', methods=['POST'])
def results_page():
    if request.method == 'POST':
        tblname = request.form['tablename']
        sql = "SELECT * FROM " + tblname + ";"
        # res = db.query(sql)
        res = DataBaseFactory.GetDataBaseObject().selectAllFromEntity(tblname)
        return render_template('results.html', res=res, name=tblname)

# ---------------------------------------------------------
# Patient Routes
# ---------------------------------------------------------


@app.route('/patient_created/<new_patient_id>', methods=['GET', 'POST'])
def patient_created(new_patient_id):
    sql = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    res = db.query(sql)
    return render_template('patient_created.html', res=res)


@app.route('/patient_create', methods=['GET', 'POST'])
def patient_create():
    patient_form_create = PatientFormCreate()

    if patient_form_create.validate_on_submit():
        # get data from form
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

        # built query and execute
        sql = f'''INSERT INTO patient (patient_id, name, address_street, address_city,
                address_state, address_zip, county_id, phone, age, race, gender, health_info, admitted, discharged)
                VALUES ({new_patient_id},"{new_name}","{new_address_street}","{new_address_city}","{new_address_state}",
                        "{new_address_zip}","{new_county_id}","{new_phone}", "{new_age}","{new_race}","{new_gender}",
                        "{new_health_info}","{new_admitted}","{new_discharged}");'''
        db.insert(sql)

        return redirect(f'/patient_created/{new_patient_id}.html')
    return render_template('patient_create.html', template_form=patient_form_create)

# ---------------------------------------------------------
# County Table Routes (Add County Data, Update County Data)
# ---------------------------------------------------------


@app.route('/add-county-data', methods=['GET', 'POST'])
def addCountyData():
    # Initialize form from forms.py
    form = AddCountyData()

    # populate dropdown with distinct counties
    sql = '''SELECT DISTINCT county_name FROM county'''
    counties = db.query(sql)
    for county in counties:
        form.county.choices.append(county[0])

    # populate dropdown with distinct states
    sql = '''SELECT DISTINCT state_name FROM county'''
    states = db.query(sql)
    for state in states:
        form.state.choices.append(state[0])

    # if form is sent back (POST) to the server
    if form.validate_on_submit():
        # capture data from form
        county_date = form.date.data
        county_name = form.county.data
        state_name = form.state.data
        cases = form.cases.data
        deaths = form.deaths.data

        # capture county_id from table where county and state
        sql = f"SELECT DISTINCT county_id FROM county WHERE county_name = '{county_name}' and state_name = '{state_name}'"
        county_id = db.query(sql)[0][0]

        # insert data to county table
        sql = f'''INSERT INTO county (county_date, county_name, state_name, county_id, cases, deaths)
                VALUES ('{county_date}', '{county_name}', '{state_name}', {county_id}, {cases}, {deaths})'''
        db.insert(sql)

        # redirect user to view county table
        flash('Inserted Data Successfully', 'success')
        return redirect(url_for('viewTable', table='county'))

    return render_template('add-county-data.html', form=form)


@app.route('/edit-county-data/<date>/<id>', methods=['GET', 'POST'])
def editCountyData(date, id):
    # Initialize form from forms.py
    form = AddCountyData()

    # get values for this row from the database
    sql = f'''SELECT * FROM county WHERE county_date = '{date}' and county_id = {id}'''
    result = db.query(sql)[0]
    date = result[0]
    county = result[1]
    state = result[2]
    cases = result[4]
    deaths = result[5]

    # if form is sent back (POST) to the server
    if form.is_submitted():
        # capture data from form
        new_county_date = datetime.strftime(form.date.data, '%Y-%m-%d')
        new_county_name = form.county.data
        new_state_name = form.state.data
        new_cases = form.cases.data
        new_deaths = form.deaths.data

        # Update values in county table
        sql = f'''UPDATE county SET county_date = '{new_county_date}', county_name = '{new_county_name}', state_name = '{new_state_name}', cases = {new_cases}, deaths = {new_deaths}
                WHERE county_date = '{date}' and county_id = {id}'''
        db.insert(sql)

        # redirect user to view county table
        flash('Updated Data Successfully', 'success')
        return redirect(url_for('viewTable', table='county'))

    # populate values to the form
    form.date.data = datetime.strptime(date, '%Y-%m-%d')
    form.county.choices.append(county)
    form.state.choices.append(state)
    form.cases.data = cases
    form.deaths.data = deaths

    # populate dropdown with distinct counties
    sql = '''SELECT DISTINCT county_name FROM county'''
    counties = db.query(sql)
    for county in counties:
        form.county.choices.append(county[0])

    # populate dropdown with distinct states
    sql = '''SELECT DISTINCT state_name FROM county'''
    states = db.query(sql)
    for state in states:
        form.state.choices.append(state[0])

    return render_template('edit-county-data.html', form=form, date=date, id=id)


type1 = ""
status = ""
demographic = ""


@app.route('/chart', methods=['GET', 'POST'])
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
            dataList = DataBaseFactory.GetDataBaseObject(
            ).selectDataFromSummary(status, fieldsToShow)
        if "idToUpdate" in request.form:
            use_old_values = True
            idtoupdate = request.form['idToUpdate']
            attr = request.form['attrToUpdate']
            newVal = request.form['newValue']
            DataBaseFactory.GetDataBaseObject().updateEntity(idtoupdate, "", attr, newVal)
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
            demographics = [10, 20, 30, 40, 50, 60, 70]
            for dem in demographics:
                # DataBaseFactory.GetDataBaseObject().summarizeStatusFromDemographic(st)
                total = mongo_con.cases.find(
                    {"$and": [{'status': status}, {'patient_info.' + demographic: dem}]}).count()
                chart_data[dem] = total
        else:
            demographics = mongo_con.cases.find(
                {}, {'patient_info.'+demographic: 1, 'id': 0}).distinct('patient_info.' + demographic)
            for dem in demographics:
                total = DataBaseFactory.GetDataBaseObject(
                ).summarizeStatusFromDemographic(status, demographic, dem)
                print(total)
                chart_data[dem] = total
        return render_template('chart.html', dems=demographics, chart_data=chart_data, type1=type1, status=status, category=demographic, dataList=dataList, successfulUpdate=successfulUpdate)
    return render_template('chart.html', chart_data=None, type1=type1)
