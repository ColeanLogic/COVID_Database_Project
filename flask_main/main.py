from flask import Flask, render_template, request, session, redirect, url_for
from forms import PatientFormCreate
from database import Database

# Database Configurations
host = '192.168.64.2'
mongo_host = '127.0.0.1'
mongo_port = '20717'
user = 'tom'
passwd = 'tom'
dbname = 'COVID_Database'

db = Database(host, user, passwd, dbname)

app = Flask(__name__)
app.secret_key = b'helloworld'


@app.route('/switch_db')
def switch_db():
    if "use_mongo" in session:
        session.pop('use_mongo', None)
    else:
        session['use_mongo'] = True
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
        sql = "SELECT * FROM " + tblname + ";"
        res = db.query(sql)
        return render_template('results.html', res=res, name=tblname)


@app.route('/hooray', methods=['GET', 'POST'])
def hooray():
    return render_template('hooray.html')

# Patient Routes


@app.route('/patient_created/<new_patient_id>', methods=['GET', 'POST'])
def patient_created(new_patient_id):
    sql = f'''SELECT * FROM patient WHERE patient_id = "{new_patient_id}"'''
    res = query(sql)
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
