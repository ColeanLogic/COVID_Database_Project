<a href="https://github.com/bigcoffeemug/COVID-Database"><img src="https://images.unsplash.com/photo-1584744982493-704a9eea4322?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80" title="COVID-Database" alt="Mask"></a>

# COVID-Database

> Final Project Repository. CSC 545: Advanced Database Systems. Southern Connecticut State University. Summer 2020.

> Presented by: Tom Birmingham, Jack Bonadies, David Boyer, David Coelho and Sara Cole

[![Application](http://g.recordit.co/weDg8VESBZ.gif)]()

---

## Table of Contents

> Our `README` has a lot of info, so we thought a table of contents might be nice.

- [Objective] (#objective)
- [Significance] (#significance)
- [Mission] (#mission)
- [Installation](#installation)
- [Features](#features)
- [Contributing](#contributing)
- [Team](#team)
- [FAQ](#faq)
- [Support](#support)
- [License](#license)


---


## Objective and Motivation

The objective of this project is to design both a relational database and a non-relational database to store
public health data relating to COVID 19, which may include the number of active infections, the location of
those cases, and the status and demographics of patients. This data should be accessible to viewers at the
hospital, city, county, state, and federal level, but should restrict access to private medical information.
Implementation of the databases will include a website that allows the appropriate users to create new
records, update or view existing records or aggregate information, and delete records. We will compare the
design, implementation, and testing phases of the two different types of database. The motivation for this
project is to improve our understanding of database design and user interface design, and to better understand
the advantages and drawbacks of relational and non-relational databases.

## Significance and Application

A public health database that includes up-to-date information from all over the country is useful to a wide array
of individuals and agencies in government, healthcare, media, and more. Government agencies, mayors,
governors, scientists, and doctors who are tasked with issuing guidance to the public, making decisions about
next steps at the local and national level, and drawing conclusions about how the virus spreads or where the
next outbreak might occur, need easy access to the most current data. Our user interface will provide different
views for hospital personnel and for government officials and agencies at the city, state, and federal level.
Users will be able to access the information they need without compromising the privacy of individual medical
records.


---


## Mission Statement

The purpose of the Covid Virus Public Health database system is to maintain an up-to-date database to assist
government agencies, the general public, and health specialists in making appropriate decisions and guidance,
and to empower users with the ability to analyze and draw conclusions with the data.


---


## Installation

- All the `code` required to get started
- Commands are given in BASH and work on Windows 10 using Windows Subsystem for Linux (WSL)
- They may work on some installations using Linux or macOS

### Dependencies

The application was tested on Windows 10 with XAMPP and Python. Please install the latest version of XAMPP (7.4.8) <a href="https://www.apachefriends.org/download.html">here</a>. Python can be installed via the web or most package managers. The latetst version can be found <a href="https://www.python.org/downloads/">here</a>.

### Clone

- Clone this repo to your local machine using `https://github.com/bigcoffeemug/COVID-Database.git`

> open a new folder in the terminal and execute the following command

```shell
$ git clone https://github.com/bigcoffeemug/COVID-Database.git
```

### Setup

- We'll be using Python virtual environment to containerize the required packages and libraries

> Create and activate the virtual environment

```shell
$ python -m venv venv
$ source venv/bin/activate
```

> now change to the flask_main directory in the project folder

```shell
$ cd COVID-Database/flask_main/
```

> Install the required libraries from requirements.txt

```shell
pip install -r requirements.txt
```

### Create Databases

- Execute the script to create and populate the MongoDB database

```shell
powershell.exe ../populateMongoDB.ps1
```

- MySQL Database is built automatically when the Python Flask server is initially run
- Data is populated from the included CSV's

---


## Features

- Maintain individual patient data and demographics
- Maintain the number of confirmed cases of COVID-19 by date for the US, state, and each county.
- Report on number of new cases by date
- Report on number of resolved cases by date
- Allow for data science and understanding of demographics of different regions
- Report on why some regions have more cases and are unable to “flatten the curve”
- Report on factors (health, cultural, etc.) which cause the virus to spread more than others


---


## Team

| <a href="https://github.com/tbirms" target="_blank">**Tom Birmingham**</a> | <a href="https://github.com/ColeanLogic" target="_blank">**ColeanLogic**</a> | <a href="https://github.com/jackBonadies" target="_blank">**jackBonadies**</a> | <a href="https://github.com/bigcoffeemug" target="_blank">**David D Boyer**</a> | <a href="https://github.com/dcoelho7" target="_blank">**dclelho7**</a> |
| :---: |:---:| :---:|:---:|:---:|
| [![Tom Birmingham](https://avatars1.githubusercontent.com/u/31289104?s=460&u=c59c1b012275b375ebdce3f6733e63e0e08e81b5&v=4&s=200)](https://github.com/tbirms)    | [![ColeanLogic](https://avatars1.githubusercontent.com/u/47699463?s=460&u=1bd7d7110528166abf1d40f9e1811a67d75bfe36&v=4&s=200)](https://github.com/ColeanLogic) | [![jackBonadies](https://avatars1.githubusercontent.com/u/13188205?s=460&u=27ffc4f07ceaac5101453bbf4e804d298bb61ed1&v=4&s=200)](https://github.com/jackBonadies)  | [![David D Boyer](https://avatars1.githubusercontent.com/u/13188205?s=460&u=27ffc4f07ceaac5101453bbf4e804d298bb61ed1&v=4&s=200)](https://github.com/bigcoffeemug)  | [![dclelho7](https://avatars1.githubusercontent.com/u/32175581?s=460&v=4&s=200)](https://github.com/dcoelho7)  |
| <a href="https://github.com/tbirms" target="_blank">`github.com/tbirms`</a> | <a href="http://github.com/ColeanLogic" target="_blank">`github.com/ColeanLogic`</a> | <a href="http://github.com/jackBonadies" target="_blank">`github.com/jackBonadies`</a> | <a href="http://github.com/bigcoffeemug" target="_blank">`github.com/bigcoffeemug`</a> | <a href="http://github.com/dcoelho7" target="_blank">`github.com/dcoelho7`</a> |
