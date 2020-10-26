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

def login_menu():
    login_condition = True
    operations = ["1. Login", "2. Register"]
    while login_condition:
        for i in range(len(operations)):
            print(operations[i])
        oper = input("Please select operation or enter 0 to exit: ")
        if oper == "1":
            user = input("Enter Username: ")
            passw = input("Enter Password: ")  # NEED TO HIDE THIS. DO LATER
            signin(user, passw)
            login_condition = False
        elif oper == "2":
            register()
            login_condition = False
        elif oper == "0":
            quit()
        else:
            oper = input("Incorrect input. Please select operation or enter 0 to exit: ")
            continue

def signin(user, passw):  # Handle user signin here
    pass
  
def register():  # handle user registration here
    pass


def main():
    exit_condition = True

    dbname = input("Welcome to this interface, here you can interact with our database system,\nplease enter your sqlite database path to continue: ")
    while exit_condition:
        connectCheck = connect_db(dbname)
        if connectCheck == True:
            print("Database connected succesfully!")
            exit_condition = False
            
        else:
            print("an error occured! please try again:")
            dbname = input()
            continue

    login_menu()

if __name__ == "__main__":
    main()
