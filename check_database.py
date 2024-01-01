# -----Example Python Program to add new columns to an existing SQLite Table-----


# import the module sqlite3

import sqlite3

def select_all_games(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM game")

    rows = cur.fetchall()

    for row in rows:
        print(row)
        
# Make a connection to the SQLite DB

dbCon = sqlite3.connect(".data/pokemon.sqlite")


# Obtain a Cursor object to execute SQL statements

cur = dbCon.cursor()


# Add a new column to student table

# addColumn = "ALTER TABLE student ADD COLUMN Address varchar(32)"

# cur.execute(addColumn)


# Add a new column to teacher table

# addColumn = "ALTER TABLE teacher ADD COLUMN Address varchar(32)"

# cur.execute(addColumn)


# Retrieve the SQL statment for the tables and check the schema

masterQuery = "select * from sqlite_master"

cur.execute(masterQuery)

tableList = cur.fetchall()


for table in tableList:
    print("Database Object Type: %s" % (table[0]))

    print("Database Object Name: %s" % (table[1]))

    print("Table Name: %s" % (table[2]))

    print("Root page: %s" % (table[3]))

    print("**SQL Statement**: %s" % (table[4]))

select_all_games(dbCon)
# close the database connection

dbCon.close()
