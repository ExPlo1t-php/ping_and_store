import os
import yaml
from ping_and_store import ping_store, clear_file#importing the ping state related functions from the ping_and_store file
from getpass import getpass
from mysql.connector import connect, Error

# database connection #######################################
global connection
connection = connect(
        # creating a database connection
        host="localhost", # host name
        user="root",      # database user name
        password="",      # database password
        database="layout",# database name
    )
# database connection #######################################

# a function that fetches data from 3 databases tables
# then puts them in 3 separate files\
def fetch_data(query, file=None, type=None):
    with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            if type == None and file == None:
                 return result
            else:
                with open(file, 'w+') as storage:
                    id = 0
                    for row in result:
                        # removing the items that have :
                        # - pinging disabled (state = 1)
                        # - items that have no ip address
                        if row[2] == 1 or row[1] == None:
                            continue
                        else:
                            dict = {id:{"name":row[0],"type":type, "ip_address":row[1],}}
                            id+=1
                            yaml.safe_dump(dict, storage, sort_keys=False)

# a function that takes the data from the elements file
# and inserts it into the ping table + their state(online=1/offline=0)
def insert_data(name, type, ip_address, state):
    with connection.cursor() as cursor:
        query = "INSERT INTO ping (name, `type`, ipAddr, state) VALUES (%s, %s, %s, %s);"
        values = (name, type, ip_address, state)
        cursor.execute(query,values)
        connection.commit()

def update_data(ip_address, state):
    with connection.cursor() as cursor:
        query = f"UPDATE ping SET state = '{state}' WHERE ipAddr='{ip_address}';"
        cursor.execute(query)
        connection.commit()

# fetching data  for pinging ##############################################################################
try:
        # writing the required queries
        switch_table = "SELECT switchName, ipAddr, state FROM `switch`"
        station_table = "SELECT SN, mainIpAddr, state FROM `station`"
        equipment_table = "SELECT name, IpAddr, state FROM `equipment`"
        # fetching data using the queries
        fetch_data(switch_table, 'switches.yaml', 'switch')
        fetch_data(station_table, 'stations.yaml', 'station')
        fetch_data(equipment_table, 'equipments.yaml', 'equipment')
        # pinging on the fetched data
        ping_store("switches.yaml", "sw")
        ping_store("stations.yaml", "st")
        ping_store("equipments.yaml", "eq")
except Error as err:
    with open('queries.log', "a+") as log:
        log.write(f"{err}\n")

# fetching data for pinging ##############################################################################

# fetching data  for inserting/updating ##############################################################################
try:
    # fetch ip@ and state from the ping table
    ping_table_fetch_query = "SELECT ipAddr, state FROM `ping`"
    # fetched content
    ping_table_content = fetch_data(ping_table_fetch_query)
    # looping through the content to check if each instance already exists
    with open("elements.yaml", "r+") as elements:
        yaml_elements = yaml.safe_load(elements)
        if yaml_elements is not None:
            for i in yaml_elements:
                # elements values
                name = yaml_elements[i]['name']
                type = yaml_elements[i]['type']
                ip = yaml_elements[i]["ip_address"]
                state = yaml_elements[i]["state"]
                # checking if the instance already exists
                instance_existence_query = f"SELECT EXISTS(SELECT 1 FROM ping WHERE ipAddr='{ip}') AS ip;"
                with connection.cursor() as cursor:
                    cursor.execute(instance_existence_query)
                    existence_status = cursor.fetchall()[0][0]
                    if bool(existence_status):
                        #  if the ip_address exists update it's state
                        update_data(ip, state)
                    else:
                        # else insert it
                        insert_data(name, type, ip, state)
        else:
            print("the file is empty")
except Error as err:
     with open('queries.log', "a+") as log:
        log.write(f"{err}\n")

# fetching data  for inserting/updating ##############################################################################
