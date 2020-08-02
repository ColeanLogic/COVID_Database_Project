#here we create an abstract class that gives the views a way to update and query 
#data from the database in a database agnostic way.
#specific database implementations must implement these abstract methods

import abc
from enum import Enum
from bson.objectid import ObjectId

class DBTYPE(Enum):
    SQL = 1
    MongoDB = 2

class ROLES():
    media = "media"
    government = "government"
    doctor = "doctor"
    hospital_admin = "hospital_admin"

class DataBaseAbstraction(metaclass=abc.ABCMeta):
    conn = None
    @abc.abstractmethod
    def selectAllFromEntity(self, entity_name: str):
        raise NotImplementedError
        
    @abc.abstractmethod
    def summarizeStatusFromDemographic(self, status: str, category: str, demographic: str):
        raise NotImplementedError
        
    @abc.abstractmethod
    def updateEntity(self, id, entity_name: str,  attr, newVal):
        raise NotImplementedError
        
        
    @abc.abstractmethod
    def insertEntity(self, entity_name: str, data: []):
        raise NotImplementedError

    @abc.abstractmethod
    def getRole(self,username):
        raise NotImplementedError
        
    @abc.abstractmethod
    def __init__(self, connection): 
        self.conn = connection
        
class MongoDataBase(DataBaseAbstraction):
    def summarizeStatusFromDemographic(self, status, category, demographic):
        return self.conn.cases.find({"$and":[{'status':status},{'patient_info.' + category:demographic}]}).count()
    
    def selectDataFromSummary(self, status,fields):
        to_show_dict = {}
        to_show_dict["_id"] = 0
        _fields = fields.split(',')
        for f in _fields:
            to_show_dict[f.strip()] = 1
        return list(self.conn.cases.find({'status':status},to_show_dict))

    def __init__(self, connection):
        self.conn = connection
        
    def selectAllFromEntity(self, entity_name: str):
        #entity_name mapping
        embedded = False
        if entity_name == "patient":
            entity_name = "patient_info"
            embedded = True
        elif entity_name == "hospital":
            embedded = True
        elif entity_name == 'case_no':
            entity_name = 'cases'
        if embedded:
            return list(self.conn.cases.find({},{ "_id": 0,entity_name:1}) ) #embedded in cases
        else:
            return list(getattr(self.conn,entity_name).find({}))
            
    
    def updateEntity(self, id, entity_name: str, attr, newVal):
        self.conn.cases.update({'_id':ObjectId(id.strip())},{"$set":{attr:newVal}})

    def getRole(self, username):
        return self.conn.login.find_one({'username':username})["role"]

    def insertEntity(self, id, entity_name: str, fieldValues):
        getattr(self.conn,entity_name).insert_one(fieldValues)
    
class SQLDataBase(DataBaseAbstraction):
    def summarizeStatusFromDemographic(self, status, category, demographic):
        csr = self.conn.cursor()
        print(status)
        print(category)
        print(demographic)
        csr.execute("select count(*) from case_no join patient on case_no.patient_id=patient.patient_id where status='" + status.lower() + "' and " + category + " LIKE '" + demographic.lower()+"%" + "';")    
        return csr.fetchall()[0][0] #first in list, first part of tuple is the int
    
    def __init__(self, connection): #using covid_database
        self.conn = connection
        
    def selectAllFromEntity(self, entity_name: str):
        csr = self.conn.cursor()
        csr.execute("SELECT * FROM " + entity_name + ";")
        return csr.fetchall() #returns list of tuples of (val, val, val)
        
    def updateEntity(self, _id,entity_name: str,  attr, newVal):
        csr = self.conn.cursor()
        csr.execute("UPDATE CASE_NO SET "+attr+"='"+newVal+"' WHERE '"+_id+"'=case_id;")
        self.conn.commit()
    
    def insertEntity(self, entity_name: str, fieldValues):
        csr = self.conn.cursor()
        fieldsList = ""
        valuesList = ""
        for i in fieldValues.items():
            fieldsList += i[0].strip() 
            fieldsList +=","
            valuesList += i[1].strip()
            valuesList +=","
        valuesList = "("+valuesList[:-1]+")"
        fieldsList = "("+fieldsList[:-1]+")"
        csr.execute("INSERT INTO " + entity_name + fieldsList + " VALUES " + valuesList + ";")
        self.conn.commit()

    def selectDataFromSummary(self, status,fields):
        fields_str = ""
        _fields = fields.split(',')
        for f in _fields:
            fields_str += f.strip()
            fields_str += ","
        fields_str = fields_str[:-1]
        csr = self.conn.cursor()
        csr.execute("select " + fields_str + " from case_no join patient on case_no.patient_id=patient.patient_id where status='" + status.lower() + "'" + ";")
        return csr.fetchall()

    def getRole(self, username):
        csr = self.conn.cursor()
        csr.execute("select role from login where username='"+ username +"';")
        return csr.fetchall()[0]
    
    
class DataBaseFactory():
    databaseType = None
    mongo_conn = None
    sql_conn = None
    
    @staticmethod
    def GetDataBaseObject():
        if DataBaseFactory.databaseType is DBTYPE.MongoDB:
            return MongoDataBase(DataBaseFactory.mongo_conn)
        elif DataBaseFactory.databaseType is DBTYPE.SQL:
            return SQLDataBase(DataBaseFactory.sql_conn)
        else:
            raise "databaseType is None"
            
#TODO:
#mapping case_no to cases
#county to county 
#hospital to embedded cases.hospital
#patient to embedded cases.patient_info
    
    