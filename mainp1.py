import sqlite3
import time
import getpass
import sys
from os.path import isfile, getsize
#db_name = sys.argv[1]
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
            passw = getpass.getpass(prompt = "Enter Password: ") 
            signin(user, passw)
            login_condition = False
        elif oper == "2":
            register()
            login_condition = False
        elif oper == "0":
            quit()
        else:
            oper = input("Incorrect input. Please select an operation or enter 0 to exit: ")
            continue

def usertasks(user):
    general_menu_condition = True
    specific_menu_condition = True
    task = input("Select the task you would like to perform:\n (P) Post a question\n (S) Search for posts\n (O) Other post actions\n")
    while general_menu_condition:
        if task.upper() == 'P':
            general_menu_condition = False
        elif task.upper() == 'S':
            general_menu_condition = False
        elif task.upper() =='O':
            general_menu_condition = False
            pid = input("Type the post id of the post you want to interact with: \n")
            post_task = input("""Select the post task you would like to perform:\n 
(A): Answer a question\n 
(V): Vote on a post\n 
(M): Mark accepted answer (privileged users only)\n 
(G): Give a badge to a user (privileged users only)\n 
(T): Add a tag to a post (privileged users only)\n 
(E): Edit the title or body of a post (privileged users only)\n""")
            while specific_menu_condition:
                if post_task.upper() == 'A':
                    specific_menu_condition = False
                elif post_task.upper() == 'V':
                    specific_menu_condition = False
                elif post_task.upper() == 'M':
                    specific_menu_condition = False
                elif post_task.upper() == 'G':
                    specific_menu_condition = False
                elif post_task.upper() == 'T':
                    specific_menu_condition = False
                    addtag(user, pid)
                elif post_task.upper() == 'E':
                    specific_menu_condition = False
                    editpost(user, pid)
                else:
                    post_task = input("you inputted an incorrect choice, please try again: ")
        else:
            task = input("you inputted an incorrect choice, please try again: ")
            continue


def signin(name, passw):  # Handle user signin here
    cursor.execute(" SELECT name,pwd from users ")
    rows = cursor.fetchone()
  
def register():  # handle user registration here
    usersList = []
    user_id = input("Enter your user id in this format (ex: u001): ")
    usersList.append(user_id)
    user_name = input("Enter your name: ")
    usersList.append(user_name)
    user_city = input("Enter your city of residence: ")
    user_password = getpass.getpass(prompt = "Enter Password: ")
    usersList.append(user_password)
    usersList.append(user_city)
    cursor.execute(""" insert into users values (?,?, ?, ?, date('now')); """,usersList);
    conn.commit()
    
    

def checkprivileged(user):  #check if user is a  privileged user
    privileged_user = False
    rows = cursor.execute("SELECT uid FROM privileged")
    for elem in rows:
        if elem[0] == user:
            priveleged_user = True
            break

    return privileged_user

def addtag(user, pid):
    privileged_user = checkprivileged(user)

    if privileged_user == False:
        print("You are not allowed to use this function\n")
        usertasks(user)
    else:  #add their tag to table
        tag = input("Type the tag you would like to add:\n")
        cursor.execute("INSERT INTO tags VALUES (:pid , :tag)")
        conn.commit()
        print("Tag added successfully\n")


def editpost(user, pid):

    privileged_user = checkprivileged(user)

    if privileged_user == False:
        print("You are not allowed to use this function\n")
        usertasks(user)

    else:  #change title and/or body of post
        user_choice = input("Would you like to edit the title of this post? (Y) or (N)\n")
        if user_choice == 'Y':
            new_title = input("What would you like the new title to be?\n")
            c.execute(""" UPDATE posts 
                        SET title = :new_title
                        WHERE pid = :pid """)
            print("Title changed successfully\n")

        user_choice = input("Would you like to edit the body of this post? (Y) or (N)\n")
        if user_choice == 'Y':
            new_body = input("What would you like the new body to be?\n")
            c.execute(""" UPDATE posts 
                        SET body = :new_body
                        WHERE pid = :pid """)
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
        
    #usertasks("u001")
    login_menu()

if __name__ == "__main__":
    main()
