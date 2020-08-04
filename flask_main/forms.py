from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional
from wtforms.fields.html5 import DateField


class PatientForm(FlaskForm):
    patient_id = StringField('Patient ID* ', validators=[DataRequired()])
    name = StringField('Patient Name* ', validators=[DataRequired()])
    address_street = StringField('Street Address ')
    address_city = StringField('City ', validators=[Optional()])
    address_state = StringField('State ', validators=[Optional()])
    address_zip = StringField('Zip Code ', validators=[Optional()])
    county_id = StringField('County ID* ', validators=[DataRequired()])
    phone = StringField('Phone* ', validators=[DataRequired()])
    age = StringField('Age* ', validators=[DataRequired()])
    admitted = DateField('Date Admitted ', format='%Y-%m-%d', validators=[Optional()])
    discharged = DateField('Date Discharged ', format='%Y-%m-%d', validators=[Optional()])
    race = RadioField("Race/Ethnicity", choices=[
        ("caucasian", "Caucasian"), 
        ("african american/black","African American/Black"), 
        ("hispanic/latinx","Hispanic/Latinx"),
        ("middle eastern","Middle Eastern"),
        ("american indian/alaskan","American Indian/Alaskan"),
        ("asian/southeast asian","Asian/Southeast Asian"),
        ("multiracial/other","Multiracial/Other"),
        ("no answer","I prefer not to answer")
        ], validators=[DataRequired()])
    gender = RadioField("Gender", choices=[
        ("female", "Female"), 
        ("male","Male"), 
        ("other","Other")
        ], validators=[DataRequired()])
    health_info = RadioField("Health Info", choices=[
        ("diabetes","Diabetes"),
        ("obesity","Obesity"),
        ("asthma","Asthma"),
        ("heart disease","Heart Disease"),
        ("smoking","Smoking"),
        ("alcoholism","Alcoholism"),
        ("travel","Travel")        
        ], validators=[Optional()])
    submit = SubmitField('Submit')


class PatientLocateForm(FlaskForm):
    patient_id = StringField('Patient ID* ', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PatientSearchForm(FlaskForm):
    patient_id = StringField('Patient ID* ', validators=[Optional()])
    name = StringField('Patient Name* ', validators=[Optional()])
    address_street = StringField('Street Address ')
    address_city = StringField('City ', validators=[Optional()])
    address_state = StringField('State ', validators=[Optional()])
    address_zip = StringField('Zip Code ', validators=[Optional()])
    county_id = StringField('County ID* ', validators=[Optional()])
    phone = StringField('Phone* ', validators=[Optional()])
    age = StringField('Age* ', validators=[Optional()])
    admitted = DateField('Date Admitted ', format='%Y-%m-%d', validators=[Optional()])
    discharged = DateField('Date Discharged ', format='%Y-%m-%d', validators=[Optional()])
    race = RadioField("Race/Ethnicity", choices=[
        ("caucasian", "Caucasian"), 
        ("african american/black","African American/Black"), 
        ("hispanic/latinx","Hispanic/Latinx"),
        ("middle eastern","Middle Eastern"),
        ("american indian/alaskan","American Indian/Alaskan"),
        ("asian/southeast asian","Asian/Southeast Asian"),
        ("multiracial/other","Multiracial/Other"),
        ("no answer","I prefer not to answer")
        ], validators=[Optional()])
    gender = RadioField("Gender", choices=[
        ("female", "Female"), 
        ("male","Male"), 
        ("other","Other")
        ], validators=[Optional()])
    health_info = RadioField("Health Info", choices=[
        ("diabetes","Diabetes"),
        ("obesity","Obesity"),
        ("asthma","Asthma"),
        ("heart disease","Heart Disease"),
        ("smoking","Smoking"),
        ("alcoholism","Alcoholism"),
        ("travel","Travel")        
        ], validators=[Optional()])
    submit = SubmitField('Submit')


class PatientEditForm(FlaskForm):
    name = StringField('Patient Name* ', validators=[DataRequired()])
    address_street = StringField('Street Address ')
    address_city = StringField('City ', validators=[Optional()])
    address_state = StringField('State ', validators=[Optional()])
    address_zip = StringField('Zip Code ', validators=[Optional()])
    county_id = StringField('County ID* ', validators=[DataRequired()])
    phone = StringField('Phone* ', validators=[DataRequired()])
    age = StringField('Age* ', validators=[DataRequired()])
    admitted = DateField('Date Admitted ', format='%Y-%m-%d', validators=[Optional()])
    discharged = DateField('Date Discharged ', format='%Y-%m-%d', validators=[Optional()])
    race = RadioField("Race/Ethnicity", choices=[
        ("caucasian", "Caucasian"), 
        ("african american/black","African American/Black"), 
        ("hispanic/latinx","Hispanic/Latinx"),
        ("middle eastern","Middle Eastern"),
        ("american indian/alaskan","American Indian/Alaskan"),
        ("asian/southeast asian","Asian/Southeast Asian"),
        ("multiracial/other","Multiracial/Other"),
        ("no answer","I prefer not to answer")
        ], validators=[DataRequired()])
    gender = RadioField("Gender", choices=[
        ("female", "female"), 
        ("male","Male"), 
        ("other","Other")
        ], validators=[DataRequired()])
    health_info = RadioField("Health Info", choices=[
        ("diabetes","Diabetes"),
        ("obesity","Obesity"),
        ("asthma","Asthma"),
        ("heart disease","Heart Disease"),
        ("smoking","Smoking"),
        ("alcoholism","Alcoholism"),
        ("travel","Travel")        
        ], validators=[Optional()])
    submit = SubmitField('Submit')


class CaseForm(FlaskForm):
    case_id = DecimalField('Case ID* ', places=0, validators=[DataRequired()])
    patient_id = DecimalField('Patient ID* ', places=0, validators=[DataRequired()])
    county_id = DecimalField('County ID* ', places=0, validators=[DataRequired()])
    hospital_id = DecimalField('Hospital ID* ', places=0, validators=[DataRequired()])
    status = RadioField("Status ", choices=[
        ("in hospital ","In Hospital"),
        ("at home","At Home"),
        ("recovered","Recovered"),
        ("deceased","Deceased")], validators=[Optional()])
    hospital_name = StringField('Hospital Name ', validators=[Optional()])
    submit = SubmitField('Submit')


class CaseEditForm(FlaskForm):
    case_id = DecimalField('Case ID* ', places=0, validators=[Optional()])
    patient_id = DecimalField('Patient ID* ', places=0, validators=[Optional()])
    county_id = DecimalField('County ID* ', places=0, validators=[Optional()])
    hospital_id = DecimalField('Hospital ID* ', places=0, validators=[Optional()])
    status = RadioField("Status ", choices=[
        ("in hospital ","In Hospital"),
        ("at home","At Home"),
        ("recovered","Recovered"),
        ("deceased","Deceased")], validators=[Optional()])
    hospital_name = StringField('Hospital Name ', validators=[Optional()])
    submit = SubmitField('Submit')


class CaseLocateForm(FlaskForm):
    case_id = DecimalField('Case ID ', places=0, validators=[DataRequired()])


class AddCountyData(FlaskForm):
    date = DateField('Date ', format='%Y-%m-%d',
                     validators=[DataRequired()])
    county = SelectField("County", validators=[
        DataRequired()], choices=[])
    state = SelectField("State", validators=[DataRequired()], choices=[])
    cases = IntegerField("Cases", validators=[DataRequired()])
    deaths = IntegerField("Deaths", validators=[DataRequired()])
    submit = SubmitField('Submit')
