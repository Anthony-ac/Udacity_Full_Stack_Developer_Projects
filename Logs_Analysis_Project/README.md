# README for Udacity Logs Analysis Project

The file: **source.py** pulls a report answering the following 3 queries using the **news** database provided in the zip file below.

What are the most popular three articles of all time?


Who are the most popular article authors of all time?


On which days did more than 1% of requests lead to errors? 

## Installation

It is preferred for you to use the gitbash terminal you can download it [here](https://git-scm.com/downloads).

Install [virtual Box](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1).

Install [vagrant](https://www.vagrantup.com/downloads.html).

Download the [VM configuration](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip).

Download the [data](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip), this will provide you with the **news** database.

In order to start up your virtual machine from gitbash: `cd` into your Vagrant\FSND-Virtual-Machine\vagrant folder. Then input the following into your terminal (it may take a while as you attempt to bring your virtual machine up.):

```bash
vagrant up

vagrant ssh
```

## Usage

```python
import psycopg2 # imports PostgreSQL adapter for python

def connect_to_database():
 # function connects to the `news` db and returns the cursor.

def popularArticles(dbCursor): 
# Takes the cursor as parameter to execute query to retrieve and print the 3 most popular articles from the articles table.

def popularAuthors(dbCursor): 
# Takes the cursor as parameter to execute query to retrieve and print the most popular authors from the authors table.

def daysGreaterThan1pError(dbCursor):
# Takes the cursor as parameter to execute query to retrieve and print the Days the error rate is greater than 1%.

dbCursor.close() 
# Closes the cursor.

```
##### Views within `daysGreaterthan1pError()`:
```sql
/*Creates view "requests" (lists number of requests by date) that selects the time column from the log table and casts it to a date type while keeping count and grouping and ordering by time.*/
            create view requests    
            as select time::date as date, count(*) from log
            group by time::date
            order by time::date;
            
/*Creates view "errors" (lists all requests without the status '200 ok' from server and their number of requests by date) that selects the time column from the log table and casts it to a date type while keeping count where the status column is listed as not succesful. This is grouped and ordered by time.*/
            create view errors   
            as select time::date as date, count(*) from log
            where status != '200 OK'
            group by time::date
            order by time::date;
            
/*Creates view "requests_errors" that selects the date column from the requests view and calculates the error percentage as column errorrate by dividing the count from the errors view by the count in the request view (so long as the the date colums in the requests and errors views match). The code below gives the dates and percentages where the status was not succesful.
*/
            create view requests_errors
            as select requests.date, errors.count::float / requests.count::float * 100 
            as errorrate from requests, errors
            where requests.date = errors.date;

/*The select query below selects all columns from the "requests_errors" view where its errorrate column has values greater than 1.*/         
            select * from requests_errors where errorrate > 1;

```

## Contributing
Anthony Cordova and others welcome.

## References
[Udacity](https://www.udacity.com/)
[Programiz](https://www.programiz.com/python-programming/methods/string/format)
[Python Pep8 Style Guide](https://www.python.org/dev/peps/pep-0008/)