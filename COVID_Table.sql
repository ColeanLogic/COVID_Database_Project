CREATE schema COVID_Database;
USE COVID_Database;

CREATE TABLE login(
username VARCHAR(50)not null,
password VARCHAR(50) not null,
role VARCHAR(50) not null,
primary key(username)
);

CREATE TABLE county(
 county_id NUMERIC(5,0) not null,
 county_name VARCHAR(75) not null,
 state_name VARCHAR(50) not null,
 cases NUMERIC(7,0),
 deaths NUMERIC(7,0),
 primary key (county_id)
);

CREATE TABLE patient(
 patient_id NUMERIC(6,0) not null,
 name VARCHAR(100) not null,
 address VARCHAR(100) not null,
 phone VARCHAR(20) not null,
 admitted DATE,
 discharged DATE ,
 county_id NUMERIC(5,0) not null,
 health_info VARCHAR(100) not null,
 age NUMERIC(3,0) not null,
 race VARCHAR(50),
 gender VARCHAR(20) not null,
 primary key(patient_id),
 foreign key (county_id) references county(county_id)
);

CREATE TABLE hospital(
 hospital_id NUMERIC(6,0) not null,
 name VARCHAR(75) not null,
 county_id NUMERIC(5,0) not null,
 primary key (hospital_id),
 foreign key (county_id) references county(county_id)
);

CREATE TABLE case_no(
 case_id NUMERIC(7,0) not null,
 patient_id NUMERIC(6,0) not null,
 county_id NUMERIC(5,0) not null,
 hospital_id NUMERIC(6,0) not null,
 status VARCHAR(15),
 primary key (case_id),
 foreign key (county_id) references county(county_id),
 foreign key (patient_id) references patient(patient_id),
 foreign key (hospital_id) references hospital(hospital_id)
);
