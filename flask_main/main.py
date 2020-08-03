from flask import Flask, render_template, request, session, redirect, url_for, flash
from forms import AddCountyData, PatientLocateForm, PatientSearchForm, CaseForm, CaseLocateForm, PatientForm, PatientEditForm
from datetime import datetime
from database_class import Database
from database_abstraction_classes import *
import os

# Database Configurations
host = '192.168.64.2'
mongo_host = '127.0.0.1'
mongo_port = '20717'
user = 'cassie'
passwd = 'cassie'
dbname= 'coviddb'
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

####TODO

@app.route('/view-table-filter/<table>/<qry>', methods=['GET'])
def viewTableFilter(qry, table):
    # Retrieve Table Body
    body = db.query(qry)
    
    # Retrieve Table Header
    sql = f'''SHOW COLUMNS FROM {table} '''
    header = db.query(sql)

    return render_template('view-table.html', header=header, body=body, table=table)




#### TODO Delete this ####
@app.route('/hooray', methods=['GET', 'POST'])
def hooray():
    return render_template('hooray.html')

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
    global con
    patient_form_create = PatientForm()
    if patient_form_create.validate_on_submit():
        form_data = patient_form_create.data 
        qry = db.patient_insert_sql(form_data)
        db.insert(qry)
        flash('New patient record created', 'success')
        return redirect(f'/patient_created/{patient_form_create.patient_id.data}.html')
    return render_template('patient_create.html', template_form = patient_form_create)

@app.route('/patient_created/<new_patient_id>', methods=['GET', 'POST'])
def patient_created(new_patient_id):
    sql = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    table = 'patient'
    # res = db.query(sql) 
    # return render_template('patient_created.html', res=res)
    return redirect(f'/view-table-filter/{table}/{sql}')

@app.route('/patient_locate', methods=['GET', 'POST'])
@app.route('/patient_locate/<status>', methods=['GET', 'POST'])
def patient_locate(status=""):
    patient_locate_form = PatientLocateForm()
    if patient_locate_form.validate_on_submit():
        patient_id = patient_locate_form.patient_id.data
        qry = f"SELECT * FROM patient WHERE patient_id = '{patient_id}'"
        res = db.query(qry)
        if (res):
            patient_form_update = PatientForm()
            patient_form_update.patient_id.data = res[0][0]
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
    # Initialize form from forms.py
    patient_form_update = PatientForm()

    if patient_form_update.validate_on_submit():
        form_data = patient_form_update.data
        qry = db.patient_update_sql(form_data)
        db.insert(qry)
        return redirect(f'/patient_updated/{patient_form_update.patient_id.data}.html')
    return render_template('patient_update.html', template_form = patient_form_update)

##### TODO - pre-populated form doesn't fill in radio button values ####

@app.route('/edit-patient-data/<id>', methods=['GET', 'POST'])
def editPatientData(id):
    # Initialize form from forms.py
    patient_form_update = PatientForm()

    # get values for this row from the database
    sql = f"SELECT * FROM patient WHERE patient_id = '{id}'"
    res = db.query(sql)

    # if form is sent back (POST) to the server
    if patient_form_update.validate_on_submit():
        # capture data from form
        form_data = patient_form_update.data
        # build SQL query in update table
        qry = db.patient_update_sql(form_data)
        # update table with new data
        try:
            db.insert(qry)
        except:
            flash('Not able to update patient record', 'warning')
            return render_template(f'edit-patient-data.html', template_form = patient_form_update, id=id)
        # redirect user to patient updated page
        return redirect(f'/patient_updated/{patient_form_update.patient_id.data}.html')

    # populate values to the form
    patient_form_update.patient_id.data = res[0][0]
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

    return render_template('edit-patient-data.html', template_form=patient_form_update, id=id)


@app.route('/patient_updated/<new_patient_id>', methods=['GET', 'POST'])
def patient_updated(new_patient_id):
    qry = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    res = db.query(qry)
    return render_template('patient_updated.html', res=res)

@app.route('/patient_view', methods=['GET', 'POST'])
def patient_view():
    patient_form_view = PatientSearchForm()
    if patient_form_view.validate_on_submit():
        form_data = patient_form_view.data
        if len(form_data) > 2:
            qry = db.patient_search_sql(form_data)
            res = db.query(qry)
            return render_template('/patient_view_results.html', res=res)     
    return render_template('patient_view.html', template_form = patient_form_view)

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

