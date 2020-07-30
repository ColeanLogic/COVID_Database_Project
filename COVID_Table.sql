CREATE schema COVID_Database;
USE COVID_Database;

CREATE TABLE login
(
    username VARCHAR(50)not null,
    password VARCHAR(50) not null,
    role VARCHAR(50) not null,
    primary key(username)
);

CREATE TABLE county
(
    county_date VARCHAR (15) not null,
    county_name VARCHAR(75) not null,
    state_name VARCHAR(50) not null,
    county_id NUMERIC(5,0) not null,
    cases NUMERIC(7,0),
    deaths NUMERIC(7,0),
    primary key (county_id, county_date)
);

CREATE TABLE patient
(
    patient_id NUMERIC(6,0) not null,
    name VARCHAR(100) not null,
    address_street VARCHAR(100) not null,
    address_city VARCHAR(100) not null,
    address_state VARCHAR(100) not null,
    address_zip VARCHAR(100) not null,
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

CREATE TABLE hospital
(
    hospital_id NUMERIC(6,0) not null,
    name VARCHAR(75) not null,
    county_id NUMERIC(5,0) not null,
    primary key (hospital_id),
    foreign key (county_id) references county(county_id)
);

CREATE TABLE case_no
(
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

create view case_summary
as
    select status, COUNT(case_id)
    from case_no
    group by status;

create view county_summary
as
    select county_name, state_name, SUM(cases), SUM(deaths)
    from county
    GROUP BY county_id;

create view hospital_summary
as
    select name, status, COUNT(case_id)
    from case_no inner join hospital on (case_no.hospital_id = hospital.hospital_id)
    group by name, status;

create view comprehensive_summary
as
    select name, status, county_name, state_name, cases, deaths
    from case_no inner join hospital inner join county ON (case_no.hospital_id = hospital.hospital_id) 
    WHERE case_no.county_id = county.county_id
    GROUP BY case_id;
