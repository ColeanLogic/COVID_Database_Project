CREATE schema COVID_Database;
USE COVID_Database;

CREATE TABLE login
(
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY(username)
);

CREATE TABLE county
(
    county_date VARCHAR (15) NOT NULL,
    county_name VARCHAR(75) NOT NULL,
    state_name VARCHAR(50) NOT NULL,
    county_id NUMERIC(5,0) NOT NULL,
    cases NUMERIC(7,0),
    deaths NUMERIC(7,0),
    PRIMARY KEY (county_id, county_date)
);

CREATE TABLE patient
(
    patient_id NUMERIC(6,0) NOT NULL,
    name VARCHAR(100) NOT NULL,
    address_street VARCHAR(100) NOT NULL,
    address_city VARCHAR(100) NOT NULL,
    address_state VARCHAR(100) NOT NULL,
    address_zip VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    admitted DATE,
    discharged DATE ,
    county_id NUMERIC(5,0) NOT NULL,
    health_info VARCHAR(100),
    age NUMERIC(3,0) NOT NULL,
    race VARCHAR(50),
    gender VARCHAR(20) NOT NULL,
    PRIMARY KEY(patient_id),
    foreign key (county_id) REFERENCES county(county_id)
);

CREATE TABLE hospital
(
    hospital_id NUMERIC(6,0) NOT NULL,
    name VARCHAR(75) NOT NULL,
    county_id NUMERIC(5,0) NOT NULL,
    PRIMARY KEY (hospital_id),
    foreign key (county_id) REFERENCES county(county_id)
);

CREATE TABLE case_no
(
    case_id NUMERIC(7,0) NOT NULL,
    patient_id NUMERIC(6,0) NOT NULL,
    county_id NUMERIC(5,0) NOT NULL,
    hospital_id NUMERIC(6,0) NOT NULL,
    status VARCHAR(15),
    name VARCHAR(100),
    PRIMARY KEY (case_id),
    foreign key (county_id) REFERENCES county(county_id),
    foreign key (patient_id) REFERENCES patient(patient_id),
    foreign key (hospital_id) REFERENCES hospital(hospital_id)
);

CREATE VIEW case_summary
AS
    SELECT status, COUNT(case_id)
    FROM case_no
    GROUP BY status;

CREATE VIEW county_summary
AS
    SELECT county_name, state_name, SUM(cases), SUM(deaths)
    FROM county
    GROUP BY county_id;

CREATE VIEW hospital_summary
AS
    SELECT name, status, COUNT(case_id)
    FROM case_no inner join hospital on (case_no.hospital_id = hospital.hospital_id)
    GROUP BY name, status;

CREATE VIEW comprehensive_summary
AS
    SELECT name, status, county_name, state_name, cases, deaths
    FROM case_no inner join hospital inner join county ON (case_no.hospital_id = hospital.hospital_id)
    WHERE case_no.county_id = county.county_id
    GROUP BY case_id;
