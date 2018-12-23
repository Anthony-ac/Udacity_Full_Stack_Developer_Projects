#!/usr/bin/env python3

"""Log Analysis Project"""

import psycopg2

"""Code"""
"""***********************************"""

"""Connects to the news database and returns a database cursor."""


def connect_to_database():
    try:
        database = psycopg2.connect("dbname=news")
        dbCursor = database.cursor()
        return dbCursor
    except DatabaseError:
        print("Unable to connect to the database")


"""Query and print: Most popular articles."""


def popularArticles(dbCursor):
    query = """
            select articles.title, count(*)from  log, articles
            where  log.path = '/article/' || articles.slug
            group by articles.title
            order by count(*) desc
            limit 3;
    """
    dbCursor.execute(query)
    x = dbCursor.fetchall()

    print()
    print()
    print('3 Most Popular Articles')
    print('**************************************************')

    for result in x:
        print('"{articleName}" - {viewCount} views'.format
              (articleName=result[0], viewCount=result[1]))

    print()

    return


"""Query and print: most popular authors."""


def popularAuthors(dbCursor):
    query = """
            select authors.name, count(*) from   log, articles, authors
            where  log.path = '/article/' || articles.slug
            and articles.author = authors.id
            group by authors.name
            order by count(*) desc;
    """
    dbCursor.execute(query)
    y = dbCursor.fetchall()

    print()
    print()
    print('Most Popular Authors')
    print('**************************************************')

    for result in y:
        print('{authorName} - {viewCount} views'.format
              (authorName=result[0], viewCount=result[1]))

    print()

    return


"""Query and print:Days error rate is greater than 1%."""


def daysGreaterThan1pError(dbCursor):
    query = """
            create view requests
            as select time::date as date, count(*) from log
            group by time::date
            order by time::date;

            create view errors
            as select time::date as date, count(*) from log
            where status != '200 OK'
            group by time::date
            order by time::date;

            create view requests_errors as
            select requests.date,
            errors.count::float / requests.count::float * 100
            as errorrate from requests, errors
            where requests.date = errors.date;


            select * from requests_errors where errorrate > 1;

    """
    dbCursor.execute(query)
    z = dbCursor.fetchall()

    print()
    print()
    print('Dates Error Rate is Greater than 1%')
    print('**************************************************')

    for result in z:
        print('{date:} - {errorRate:}% errors'.format
              (date=result[0], errorRate=result[1]))

    print()
    print()

    return


"""Call functions from code"""
"""***********************************"""


if __name__ == "__main__":
    dbCursor = connect_to_database()
    if dbCursor:
        popularArticles(dbCursor)
        popularAuthors(dbCursor)
        daysGreaterThan1pError(dbCursor)
        dbCursor.close()
