from flask import Flask, render_template, request, session, redirect, url_for, flash
from forms import AddCountyData, PatientLocateForm, PatientSearchForm, HospitalFormCreate, CaseForm, CaseLocateForm, PatientForm, PatientEditForm, CaseEditForm, registrationForm, ChooseDates
from datetime import datetime
from database import Database
from database_abstraction_classes import *
import os
import sys

# Database Configurations
host = 'localhost'
mongo_host = '127.0.0.1'
mongo_port = '20717'
user = 'root'
passwd = ''
dbname = 'COVID_Database'
mongo_con = None

db = Database(host, user, passwd, dbname)

# here we have mongodb conn to covid_db and a sql conn to covid_db.
DataBaseFactory.mongo_conn = db.mongo_con
mongo_con = db.mongo_con
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
        db.connect_to_mongodb()
        DataBaseFactory.databaseType = DBTYPE.MongoDB
    return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = registrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        sql = f"INSERT INTO login VALUES ('{username}', '{password}', '{role}')"
        db.insert(sql)
        flash(f"Created user {username} successfully!", 'success')
        session['usr'] = username
        session['role'] = role
        return redirect(url_for('home'))

    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":
        username = request.form['usr']
        password = request.form['pass']
        userRecord = DataBaseFactory.GetDataBaseObject().getUserRecords(username)

        if len(userRecord) == 0:
            flash('Invalid username!', 'warning')
        elif userRecord[0][1] != password:
            flash('Invalid password!', 'warning')
        else:
            session['usr'] = userRecord[0][0]
            session['role'] = userRecord[0][2]
            flash(
                f'''Logged in successfully! Your role is {session['role']}''', 'success')
            return redirect(url_for('home'))

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
    elif table == 'patient' and session['role'] not in ['doctor', 'hospital_admin']:
        sql = sql.replace(
            '*', 'patient_id, admitted, discharged, county_id, health_info, age, race, gender')
    body = db.query(sql)

    # Retrieve Table Header
    sql = f'''SHOW COLUMNS FROM {table}'''
    header = db.query(sql)
    if table == 'patient' and session['role'] not in ['doctor', 'hospital_admin']:
        del header[1:7]

    return render_template('view-table.html', header=header, body=body, table=table)


@app.route('/view-table-filter/<table>', methods=['GET'])
def viewTableFilter(table):
    # Retrieve Table Body
    qry = session['qry']

    try:
        body = db.query(qry)
    except:
        flash('No records found', 'danger')
        return redirect(url_for('viewTable', table=table))
    # Retrieve Table Header
    sql = f'''SHOW COLUMNS FROM {table} '''
    header = db.query(sql)
    if session['role'] not in ['doctor', 'hospital_admin']:
        del header[1:7]

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


@app.route('/patient_create', methods=['GET', 'POST'])
def patient_create():
    patient_form_create = PatientForm()
    if patient_form_create.validate_on_submit():
        form_data = patient_form_create.data
        id = patient_form_create.patient_id.data
        qry = db.patient_insert_sql(form_data)
        db.insert(qry)
        flash('New patient record created', 'success')
        return redirect(f'/patient_created/{id}.html')
    return render_template('patient_create.html', template_form=patient_form_create)


@app.route('/patient_created/<new_patient_id>', methods=['GET', 'POST'])
def patient_created(new_patient_id):
    session['qry'] = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    return redirect(f'/view-table-filter/patient')


@app.route('/patient_updated/<new_patient_id>', methods=['GET', 'POST'])
def patient_updated(new_patient_id):
    session['qry'] = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    table = 'patient'
    flash('Patient record updated', 'success')
    return redirect(f'/view-table-filter/{table}')


@app.route('/edit-patient-data/<id>', methods=['GET', 'POST'])
def editPatientData(id):
    # Initialize form from forms.py
    form = PatientForm()

    # if form is sent back (POST) to the server
    if form.validate_on_submit():
        # capture data from form
        form_data = form.data
        # build SQL query in update table
        qry = db.patient_update_sql(form_data)
        # update table with new data
        try:
            db.insert(qry)
        except:
            flash('Not able to update patient record', 'warning')
            return render_template(f'edit-patient-data.html', template_form=form, id=id)
        # redirect user to patient updated page
        return redirect(f'/patient_updated/{id}.html')

    # get values for this row from the database
    sql = f"SELECT * FROM patient WHERE patient_id = '{id}'"
    res = db.query(sql)

    # populate values to the form
    form.patient_id.data = res[0][0]
    form.name.data = res[0][1]
    form.address_street.data = res[0][2]
    form.address_city.data = res[0][3]
    form.address_state.data = res[0][4]
    form.address_zip.data = res[0][5]
    form.phone.data = res[0][6]
    form.admitted.data = res[0][7]
    form.discharged.data = res[0][8]
    form.county_id.data = res[0][9]
    form.health_info.data = res[0][10]
    form.age.data = res[0][11]
    form.race.data = res[0][12]
    form.gender.data = res[0][13]

    return render_template('edit-patient-data.html', template_form=form, id=id)


@app.route('/patient_view', methods=['GET', 'POST'])
def patient_view():
    patient_form_view = PatientSearchForm()
    if patient_form_view.validate_on_submit():
        form_data = patient_form_view.data
        if len(form_data) > 2:
            sql = db.patient_search_sql(form_data, role=session['role'])
            table = 'patient'
            session['qry'] = sql
            return redirect(url_for('viewTableFilter', table=table))
    return render_template('patient_view.html', template_form=patient_form_view)


# ---------------------------------------------------------
# Case Routes
# ---------------------------------------------------------


@app.route('/case_create', methods=['GET', 'POST'])
def case_create():
    global db
    case_form_create = CaseForm()
    if case_form_create.validate_on_submit():
        form_data = case_form_create.data
        qry = db.case_insert_sql(form_data)
        db.insert(qry)
        return redirect(f'/case_created/{case_form_create.case_id.data}')
    return render_template('case_create.html', template_form=case_form_create)


@app.route('/case_created/<new_case_id>', methods=['GET', 'POST'])
def case_created(new_case_id):
    global db
    form_data = {'case_id': f'{new_case_id}'}
    session['qry'] = db.case_select_sql(form_data)
    table = 'case_no'
    flash('New Case Created', 'success')
    return redirect(f'/view-table-filter/{table}')


@app.route('/edit-case-data/<id>', methods=['GET', 'POST'])
def editCaseData(id):
    # Initialize form from forms.py
    form = CaseForm()

    # get values for this row from the database
    sql = f"SELECT * FROM case_no WHERE case_id = '{id}'"
    res = db.query(sql)

    # if form is sent back (POST) to the server
    if form.validate_on_submit():
        # capture data from form
        form_data = form.data
        # build SQL query to update case table
        qry = db.case_update_sql(form_data)
        # update table with new data
        try:
            db.insert(qry)
        except:
            flash('Not able to update case record', 'warning')
            return render_template(f'edit-case-data.html', template_form=form, id=id)
        # redirect user to case updated page
        return redirect(f'/case_updated/{form.case_id.data}')

    # populate values to the form
    form.case_id.data = res[0][0]
    form.patient_id.data = res[0][1]
    form.county_id.data = res[0][2]
    form.hospital_id.data = res[0][3]
    form.status.data = res[0][4]
    form.hospital_name.data = res[0][5]

    return render_template('edit-case-data.html', template_form=form, id=id)


@app.route('/case_updated/<new_case_id>', methods=['GET', 'POST'])
def case_updated(new_case_id):
    session['qry'] = f'''SELECT * FROM case_no WHERE case_id = "{new_case_id}"'''
    table = 'case_no'
    flash('Case Record Updated', 'success')
    return redirect(f'/view-table-filter/{table}')


@app.route('/case_view', methods=['GET', 'POST'])
def case_view():
    case_form_view = CaseEditForm()
    if case_form_view.validate_on_submit():
        form_data = case_form_view.data
        if len(form_data) > 2:
            session['qry'] = db.case_search_sql(form_data)
            table = 'case_no'
            return redirect(f'/view-table-filter/{table}')
    return render_template('case_view.html', template_form=case_form_view)


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


@app.route('/county-chart', methods=['GET', 'POST'])
def countyChart(res=None):
    # instantiate form
    form = ChooseDates()

    # if form is sent back (POST) to the server
    if form.validate_on_submit():
        # capture data from form
        form_data = {}
        form_data["start_date"] = datetime.strftime(
            form.start_date.data, '%Y-%m-%d')
        form_data["end_date"] = datetime.strftime(
            form.end_date.data, '%Y-%m-%d')
        form_data["county_id"] = form.county_id.data
        form_data["state_name"] = form.state.data
        form_data["request_type"] = form.request_type.data
        sql = db.countyChartSql(form_data)
        res = db.query(sql)
        labels = []
        series = []
        for row in res:
            date_time = datetime.strptime(row[0], '%Y-%m-%d')
            date_str = date_time.strftime("%b %d")
            labels.append(date_str)
        for row in res:
            if form_data["request_type"] == "cases":
                series.append(int(row[1]))
            else:
                series.append(int(row[2]))
        return render_template('county-chart.html', form=form, res=res, labels=labels, series=series)

    return render_template('county-chart.html', form=form, res=res)


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
                chart_data[dem] = total
        return render_template('chart.html', dems=demographics, chart_data=chart_data, type1=type1, status=status, category=demographic, dataList=dataList, successfulUpdate=successfulUpdate)
    return render_template('chart.html', chart_data=None, type1=type1)


# ---------------------------------------------------------
# Hopital Table Routes (Add Hospital Data)
# ---------------------------------------------------------


@app.route('/hospital_create', methods=['GET', 'POST'])
def addHospitalData():
    # Initialize form from forms.py
    form = HospitalFormCreate()

    # if form is sent back (POST) to the server
    if form.validate_on_submit():
        # capture data from form
        hospital_id = form.hospital_id.data
        name = form.name.data
        county_id = form.county_id.data

        # insert data to county table
        sql = f'''INSERT INTO hospital (hospital_id, name, county_id) VALUES ("{hospital_id}","{name}","{county_id}");'''
        db.insert(sql)

        # redirect user to view county table
        flash('Hospital Data Successfully', 'success')
        return redirect(url_for('addHospitalData', table='hospital'))

    return render_template('hospital_create.html', form=form)
