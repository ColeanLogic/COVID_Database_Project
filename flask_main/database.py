from pymongo import MongoClient
import mysql.connector
import os


class Database():
    def __init__(self, host, user, passwd, dbname):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.con = self.connect_to_mysql()
        self.mongo_con = self.connect_to_mongodb
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
            csr = self.con.cursor()
            csr.execute(load_data_query)
            self.con.commit()

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

    def connect_to_mongodb(self):
        # MongoClient("mongodb://" + mongo_host+':'+mongo_port)
        client = MongoClient('mongodb://127.0.0.1:27017')
        if(self.mongo_con != None):
            # already connected
            return
        exists = False
        for db in client.list_databases():
            if db["name"] == "covid_db":
                exists = True
        if(exists == False):
            raise Exception(
                "You do not have a covid_db in your list of databases")
        return client.covid_db
