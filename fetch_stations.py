import os
import yaml# execute pip install pyyaml
from getpass import getpass
from mysql.connector import connect, Error # execute pip install mysql-connector-python

# database connection #######################################
global connection, connectionPlanner
connection = connect(
        # creating a database connection
        host="localhost", # host name
        user="root",      # database user name
        password="",      # database password
        database="layout",# database name
    )
connectionPlanner = connect(
        # creating a database connection
        host="localhost", # host name
        user="root",      # database user name
        password="",      # database password
        database="Planner",# database name
    )

def checkExistence(name):
    with connectionPlanner.cursor() as cursor:
        check_query = "SELECT COUNT(*) FROM stations WHERE `name` = %s"
        cursor.execute(check_query, [name])
        existing_count = cursor.fetchone()[0]
        return existing_count

def insert_data(name, project):
    with connectionPlanner.cursor() as cursor:
        insert_with_id = "INSERT INTO stations (`name`, `project_id`) VALUES (%s, %s)"
        values = (name, project)
        cursor.execute(insert_with_id,values)
        connectionPlanner.commit()
# database connection #######################################
with connectionPlanner.cursor() as cursor:
    projects_table = "SELECT name, id FROM `projects`" 
    cursor.execute(projects_table)
    projects = cursor.fetchall()

with connection.cursor() as cursor:
    for project in projects:
        station_table = "SELECT name FROM `station` WHERE name LIKE %s" 
        cursor.execute(station_table, [f"%{project[0].upper()}%"])
        stations = cursor.fetchall()
        if(len(stations)):
            for i in stations:
                if(checkExistence(i[0]==0)):
                    insert_data(i[0], project[1])
        else:
            cursor.execute(station_table, ["%"])
            allStations = cursor.fetchall()
            for i in allStations:
                if(checkExistence(i[0]==0)):
                    insert_data(i[0], project[1])

    # ######
        # print(values)
