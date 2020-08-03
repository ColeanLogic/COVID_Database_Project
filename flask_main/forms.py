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
        ("Caucasian", "Caucasian"), 
        ("African American/Black","African American/Black"), 
        ("Hispanic/Latinx","Hispanic/Latinx"),
        ("Middle Eastern","Middle Eastern"),
        ("American Indian/Alaskan","American Indian/Alaskan"),
        ("Asian/Southeast Asian","Asian/Southeast Asian"),
        ("Multiracial/Other","Multiracial/Other"),
        ("No Answer","I prefer not to answer")
        ], validators=[DataRequired()])
    gender = RadioField("Gender", choices=[
        ("Female", "Female"), 
        ("Male","Male"), 
        ("Other","Other")
        ], validators=[DataRequired()])
    health_info = RadioField("Health Info", choices=[
        ("Diabetes","Diabetes"),
        ("Obesity","Obesity"),
        ("Asthma","Asthma"),
        ("Heart Disease","Heart Disease"),
        ("Smoking","Smoking"),
        ("Alcoholism","Alcoholism"),
        ("Travel","Travel")        
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
        ("Caucasian", "Caucasian"), 
        ("African American/Black","African American/Black"), 
        ("Hispanic/Latinx","Hispanic/Latinx"),
        ("Middle Eastern","Middle Eastern"),
        ("American Indian/Alaskan","American Indian/Alaskan"),
        ("Asian/Southeast Asian","Asian/Southeast Asian"),
        ("Multiracial/Other","Multiracial/Other"),
        ("No Answer","I prefer not to answer")
        ], validators=[Optional()])
    gender = RadioField("Gender", choices=[
        ("Female", "Female"), 
        ("Male","Male"), 
        ("Other","Other")
        ], validators=[Optional()])
    health_info = RadioField("Health Info", choices=[
        ("Diabetes","Diabetes"),
        ("Obesity","Obesity"),
        ("Asthma","Asthma"),
        ("Heart Disease","Heart Disease"),
        ("Smoking","Smoking"),
        ("Alcoholism","Alcoholism"),
        ("Travel","Travel")        
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
        ("Caucasian", "Caucasian"), 
        ("African American/Black","African American/Black"), 
        ("Hispanic/Latinx","Hispanic/Latinx"),
        ("Middle Eastern","Middle Eastern"),
        ("American Indian/Alaskan","American Indian/Alaskan"),
        ("Asian/Southeast Asian","Asian/Southeast Asian"),
        ("Multiracial/Other","Multiracial/Other"),
        ("No Answer","I prefer not to answer")
        ], validators=[DataRequired()])
    gender = RadioField("Gender", choices=[
        ("Female", "Female"), 
        ("Male","Male"), 
        ("Other","Other")
        ], validators=[DataRequired()])
    health_info = RadioField("Health Info", choices=[
        ("Diabetes","Diabetes"),
        ("Obesity","Obesity"),
        ("Asthma","Asthma"),
        ("Heart Disease","Heart Disease"),
        ("Smoking","Smoking"),
        ("Alcoholism","Alcoholism"),
        ("Travel","Travel")        
        ], validators=[Optional()])
    submit = SubmitField('Submit')

class CaseForm(FlaskForm):
    case_id = DecimalField('Case ID* ', places=0, validators=[DataRequired()])
    patient_id = DecimalField('Patient ID* ', places=0, validators=[DataRequired()])
    county_id = DecimalField('County ID* ', places=0, validators=[DataRequired()])
    hospital_id = DecimalField('Hospital ID* ', places=0, validators=[DataRequired()])
    status = RadioField("Status ", choices=[
        ("In Hopsital","In Hopsital"),
        ("At Home","At Home"),
        ("Recovered","Recovered"),
        ("Deceased","Deceased")], validators=[Optional()])
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
