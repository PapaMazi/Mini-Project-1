import sqlite3
import time
from os.path import isfile, getsize
conn = None
cursor = None



def connect_db(dbname):
    global conn, cursor
    if not isfile(dbname):
        return False
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    conn.commit()
    return True
    


def main():
    exit_condition = True
    print("Welcome to this interface, here you can interact with our database system,\nplease enter your sqlite database path to continue:")
    dbname = input()
    while exit_condition:
        connectCheck = connect_db(dbname)
        if connectCheck == True:
            print("Database connected succesfully!")
            exit_condition = False
        else:
            print("an error occured! please try again:")
            dbname = input()
            continue
            
            
if __name__ == "__main__":
    main()