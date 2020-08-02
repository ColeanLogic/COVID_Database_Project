from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, SelectField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class PatientFormCreate(FlaskForm):
    patient_id = StringField('Patient ID* ', validators=[DataRequired()])
    name = StringField('Patient Name* ', validators=[DataRequired()])
    address_street = StringField('Street Address ')
    address_city = StringField('City ')
    address_state = StringField('State ')
    address_zip = StringField('Zip Code ')
    county_id = StringField('County ID* ', validators=[DataRequired()])
    phone = StringField('Phone* ', validators=[DataRequired()])
    age = StringField('Age* ', validators=[DataRequired()])
    admitted = DateField('Date Admitted ', format='%Y-%m-%d')
    discharged = DateField('Date Discharged ', format='%Y-%m-%d')
    race = RadioField("Race/Ethnicity", choices=[
        ("Caucasian", "Caucasian"),
        ("African American/Black", "African American/Black"),
        ("Hispanic/Latinx", "Hispanic/Latinx"),
        ("Middle Eastern", "Middle Eastern"),
        ("American Indian/Alaskan", "American Indian/Alaskan"),
        ("Asian/Southeast Asian", "Asian/Southeast Asian"),
        ("Multiracial/Other", "Multiracial/Other"),
        ("No Answer", "I prefer not to answer")
    ])
    gender = RadioField("Gender", choices=[
        ("Female", "Female"),
        ("Male", "Male"),
        ("Other", "Other")
    ])
    health_info = RadioField("Health Info", choices=[
        ("Diabetes", "Diabetes"),
        ("Obesity", "Obesity"),
        ("Asthma", "Asthma"),
        ("Heart Disease", "Heart Disease"),
        ("Smoking", "Smoking"),
        ("Alcoholism", "Alcoholism"),
        ("Travel", "Travel")
    ])
    submit = SubmitField('Submit')


class AddCountyData(FlaskForm):
    date = DateField('Date ', format='%Y-%m-%d',
                     validators=[DataRequired()])
    county = SelectField("County", validators=[
        DataRequired()], choices=[])
    state = SelectField("State", validators=[DataRequired()], choices=[])
    cases = IntegerField("Cases", validators=[DataRequired()])
    deaths = IntegerField("Deaths", validators=[DataRequired()])
    submit = SubmitField('Submit')
