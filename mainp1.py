import sqlite3
import time
import getpass
from os.path import isfile, getsize

conn = None
cursor = None

def connect_db(dbname):
    global conn, cursor
    #if not isfile(dbname):
    #    return False
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
            passw = getpass.getpass(prompt = "Enter Password: ")  # NEED TO HIDE THIS. DO LATER
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

def usertasks(user):
    task = input("""Select the task you would like to perform:\n
                    (P) Post a question\n
                    (S) Search for posts\n
                    (O) Other post actions\n
                    """)
    if task == 'P':
        #add code
    if task == 'S':
        #add code
    if task =='O':
        pid = input("Type the post id of the post you want to interact with")
        post_task = input("""Select the post task you would like to perform:\n)
                            (A) Answer a question\n
                            (V) Vote on a post\n
                            (M) Mark accepted answer (priviledged users only)\n
                            (G) Give a badge to a user (priviledged users only)\n
                            (T) Add a tag to a post (priviledged users only)\n
                            (E) Edit the title or body of a post (priviledged users only)\n""")
   
    if task == 'A':
        #add code
    if task == 'V':
        #add code
    if task == 'M':
        #add code
    if task == 'G':
        #add code
    if task == 'T':
        addtag(user, pid)
    if task == 'E':
        editpost(user, pid)


def signin(user, passw):  # Handle user signin here
    pass
  
def register():  # handle user registration here
    pass

def checkprivileged(user):  #check if user is a  privileged user
    privileged_user = False
    c.execute("SELECT uid FROM privileged")
    rows = c.fetchone()
    for elem in rows
        if elem[0] == user:
            priveleged_user = True
            break

    return privileged_user

def addtag(user, pid):
    privileged_user = checkprivileged(user)

    if priveleged_user == False:
        print("You are not allowed to use this function\n")
        usertasks(user)

    else:  #add their tag to table
        tag = input("Type the tag you would like to add:\n")
        c.execute("INSERT INTO tags VALUES (:pid , :tag)")
        print("Tag added successfully\n")


def editpost(user, pid):

    privileged_user = checkprivileged(user)

    if priveleged_user == False:
        print("You are not allowed to use this function\n")
        usertasks(user)

    else:  #change title and/or body of post
        user_choice = input("Would you like to edit the title of this post? (Y) or (N)\n")
        if user_choice == 'Y':
            new_title = input("What would you like the new title to be?\n")
            c.execute(""UPDATE posts 
                        SET title = :new_title 
                        WHERE pid = :pid"")
            print("Title changed successfully\n")

        user_choice = input("Would you like to edit the body of this post? (Y) or (N)\n")
        if user_choice == 'Y':
            new_body = input("What would you like the new body to be?\n")
            c.execute(""UPDATE posts 
                        SET body = :new_body
                        WHERE pid = :pid"")
            print("Body changed successfully\n")

        usertasks(user)


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
