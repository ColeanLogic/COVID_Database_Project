from pymongo import MongoClient
import mysql.connector
import os
from forms import CaseForm


class Database():
    def __init__(self, host, user, passwd, dbname):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.con = self.connect_to_mysql()
        self.mongo_con = self.connect_to_mongodb()
        self.use_db()

    def connect_to_mysql(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.host, user=self.user, passwd=self.passwd, autocommit=True)
        except mysql.connector.Error as E:
            print(E)
        return connection

    def create_tables(self):
        createScript = open(os.path.join('..', 'COVID_Table.sql'))
        sqlCmds = " ".join(createScript.readlines())
        csr = self.con.cursor()
        for res in csr.execute(sqlCmds, multi=True):
            pass
        self.con.commit()

    def load_tables(self):
        self.use_db()
        path_table = [('county_jan_to_april','county'),('county_may','county'),('county_jun','county'),('county_jul','county'),
            ('hospital','hospital'),('login','login'),('patients_april','patient'),('patients_may','patient'),('patients_june','patient'),
            ('patients_july','patient'),('patients_march','patient'),('case','case_no')]
        print("Populating tables please wait...")
        for i in path_table:
            county_path = os.path.join(os.getcwd(), '..', i[0]+'.csv')
            county_path = county_path.replace(r"/mnt/c", r"C:")
            if(i[1] != 'patient'):
                load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' IGNORE 1 LINES;".format(
                    county_path, i[1])
            else:
                load_data_query = "LOAD DATA INFILE '{0}' IGNORE INTO TABLE {1} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' IGNORE 1 LINES (patient_id, name, address_street, address_city, address_state, address_zip, phone, admitted, discharged, county_id, health_info, age,race,gender);".format(
                    county_path, i[1])
            csr = self.con.cursor()
            print(f"Loading {i[0]}.csv into {i[1]} table")
            csr.execute(load_data_query)
            self.con.commit()
        print("Complete!")

    def database_created(self):
        csr = self.con.cursor()
        csr.execute("SHOW DATABASES LIKE '" + self.dbname + "';")
        res = csr.fetchall()
        return len(res) != 0

    def use_db(self):
        if not self.database_created():
            self.create_tables()
            self.load_tables()

        csr = self.con.cursor()
        csr.execute("USE " + self.dbname)
        self.con.commit()

    def insert(self, sql):
        csr = self.con.cursor()
        csr.execute(sql)

    def query(self, query):
        csr = self.con.cursor()
        csr.execute(query)
        result = csr.fetchall()
        return result

# ---------------------------------------------------------
# Methods to build and return SQL queries
# ---------------------------------------------------------

    # Takes a dictionary of form data and returns an SQL insert statement for the patient table
    def patient_insert_sql(self, form_data):
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
        return qry

    # Takes a dictionary of form data and returns an SQL update statement for the patient table
    def patient_update_sql(self, form_data):
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
        return qry

    # Takes a dictionary of form data and returns an SQL select statement to search the patient table
    def patient_search_sql(self, form_data, role):
        qry = "SELECT * FROM patient WHERE "
        numeric_data = ('patient_id', 'county_id', 'age')
        for key, value in form_data.items():
            if key != 'submit' and key != 'csrf_token':
                if value:
                    if key in numeric_data:
                        qry = qry + f"{key} = {value} AND "
                    else:
                        qry = qry + f"{key} = '{value}' AND "
            else:
                continue
        if role not in ['doctor', 'hospital_admin']:
            qry = qry.replace(
                '*', 'patient_id, admitted, discharged, county_id, health_info, age, race, gender')
        qry = qry[:-4]
        qry = qry + ";"
        return qry

    # Takes a dictionary of form data and returns an SQL insert statement for the case_no table

    def case_insert_sql(self, form_data):
        qry = "INSERT INTO case_no (case_id, patient_id, county_id, hospital_id, status, hospital_name) VALUES ("
        numeric_data = ('case_id', 'patient_id', 'county_id', 'hospital_id')
        for key, value in form_data.items():
            if key != 'submit' and key != 'csrf_token':
                if value == None:
                    qry = qry + "'NULL', "
                else:
                    if key in numeric_data:
                        qry = qry + f"{value}, "
                    else:
                        qry = qry + f"'{value}', "
            else:
                continue
        qry = qry[:-2]
        qry = qry + ")"
        return qry

     # Takes a dictionary of form data and returns an SQL update statement for the case table

    def case_update_sql(self, form_data):
        qry = "UPDATE case_no SET "
        numeric_data = ('case_id', 'patient_id', 'county_id', 'hospital_id')
        for key, value in form_data.items():
            if key != 'submit' and key != 'csrf_token':
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
        qry = qry + f" WHERE case_id = {form_data['case_id']};"
        return qry

    # Takes a dictionary of form data and returns an SQL select statement for the case_no table

    def case_select_sql(self, form_data):
        qry = "SELECT * FROM case_no WHERE "
        numeric_data = ('case_id', 'patient_id', 'county_id', 'hospital_id')
        for key, value in form_data.items():
            if key != 'submit' and key != 'csrf_token':
                if value:
                    if key in numeric_data:
                        qry = qry + f"{key} = {value} AND "
                    else:
                        qry = qry + f"{key} = '{value}' AND "
            else:
                continue
        qry = qry[:-4]
        qry = qry + ";"
        return qry


# Takes a dictionary of form data and returns an SQL select statement to search the case table


    def case_search_sql(self, form_data):
        qry = "SELECT * FROM case_no WHERE "
        numeric_data = ('case_id', 'patient_id', 'county_id', 'hospital_id')
        for key, value in form_data.items():
            if key != 'submit' and key != 'csrf_token':
                if value:
                    if key in numeric_data:
                        qry = qry + f"{key} = {value} AND "
                    else:
                        qry = qry + f"{key} = '{value}' AND "
            else:
                continue
        qry = qry[:-4]
        qry = qry + ";"
        return qry


# ---------------------------------------------------------
# MongoDB
# ---------------------------------------------------------

    def connect_to_mongodb(self):
        # MongoClient("mongodb://" + mongo_host+':'+mongo_port)
        client = MongoClient('mongodb://127.0.0.1:27017')
        exists = False
        for db in client.list_databases():
            if db["name"] == "covid_db":
                exists = True
        if(exists == False):
            raise Exception(
                "You do not have a covid_db in your list of databases")
        return client.covid_db
