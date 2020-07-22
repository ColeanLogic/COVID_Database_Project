CREATE schema COVID_Database;
USE COVID_Database;

Create table user(
username varchar(50) not null,
password varchar(50) not null,
role varchar(50) not null,
Primary key(username));