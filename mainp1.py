import sqlite3
import time
import getpass
from random import randint
from prettytable import PrettyTable
import re
import sys
from os.path import isfile, getsize

# db_name = sys.argv[1]
conn = None
cursor = None


def connect_db(dbname):  # init db cursor
    global conn, cursor

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
            passw = getpass.getpass(prompt="Enter Password: ")
            condition = signin(user, passw)
            if condition == True:
                usertasks(user)
                login_condition = False
            else:
                continue
        elif oper == "2":
            register()
            print("user succesfully registered.")
            login_condition = False
        elif oper == "0":
            quit()
        else:
            continue


def usertasks(user):
    general_menu_condition = True
    specific_menu_condition = True
    task = input(
        "Select the task you would like to perform:\n (P) Post a question\n (S) Search for posts\n (O) Other post actions\n")
    while general_menu_condition:
        if task.upper() == 'P':
            general_menu_condition = False
            add_post(user)
        elif task.upper() == 'S':
            search_posts()
            general_menu_condition = False
        elif task.upper() == 'O':
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
                    mark_as_accepted(user, pid)
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


def search_posts():  # '2. Search for posts'
    # TODO: test if results are ordered based on #of kw
    # TODO: test case insensitivity
    # TODO: test partial matching (see: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=1537384)
    keywords = input("Please enter keywords separated by a comma: ")
    keywords = keywords.split(", ")
    cursor.execute("SELECT p.pid, p.title, p.body, t.tag FROM posts p, tags t WHERE p.pid = t.pid;")
    posts = cursor.fetchall()
    pids = []

    for item in keywords:  # for each keyword the user entered
        for row in posts:  # for each row from posts
            for field in row:  # for each field in row
                if item.lower() in field.lower():  # check if keyword is in the field
                    pids.append(row[0])  # if kw is in row then add pid to pid[]

    if not pids:  # if pids[] is empty
        print("Couldn't find any matches")
    else:  # if pids[] not empty then:
        pid_count = {i:pids.count(i) for i in pids}  #counts # https://stackoverflow.com/questions/23240969/python-count-repeated-elements-in-the-list/23240989
        pid_count = sorted(pid_count.items(), key=lambda v: v[1], reverse=True)  #orders based on # of kw  # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        results = []
        for pid in pid_count:
            cursor.execute('SELECT * FROM posts WHERE pid=?;', (pid[0],))  # fetches results
            results.append(cursor.fetchone())
        print_results(results)  # print results


def print_results(data):  # handle printing search results here
    # TODO: need to implement listing 5 results at a time
    table = PrettyTable(['PID', 'Post Date', 'Title', 'Body', 'Poster', 'Votes', 'Answers'])

    for i in data:  # prints data in table format (prints all results)
        cursor.execute('SELECT count(pid) FROM votes WHERE pid=?', (i[0],))  # gets number of votes
        i = i + cursor.fetchone()
        cursor.execute('SELECT count(qid) FROM answers WHERE qid =?', (i[0],))  # gets number of answers if question
        i = i + cursor.fetchone()
        table.add_row(i)
    print(table)

    # j = 0  # this code block prints 5 resutls at a time
    # for i in data:  # prints data in table format
    #     if j <= 4:
    #         cursor.execute('SELECT count(pid) FROM votes WHERE pid=?', (i[0],))  # gets number of votes
    #         i = i + cursor.fetchone()
    #         cursor.execute('SELECT count(qid) FROM answers WHERE qid =?', (i[0],))  # gets number of answers if question
    #         i = i + cursor.fetchone()
    #         table.add_row(i)
    #         # print(j)
    #         j = j + 1
    # print(table)


def add_answer(user, qpost):  # allows user to add answer to qpost
    postList = []
    verifyexist = []
    p_string = 'p'
    post_title = input("Enter your post title: ")
    post_body = input("Enter your post body: ")
    new_id = randint(200,999)
    new_id = p_string + str(new_id)
    verifyexist.append(new_id)
    cursor.execute(" SELECT pid from posts WHERE pid = ?; ", verifyexist)
    if cursor.fetchone():
        new_id = randint(200,999)
        new_id = p_string + str(new_id)
    else:
        pass
    postList.append(new_id)
    postList.append(post_title)
    postList.append(post_body)
    postList.append(user)
    cursor.execute(" INSERT INTO posts (pid,pdate, title, body, poster) VALUES (?,date('now'), ?,?,?); ",postList)
    conn.commit()
    questionList = [new_id, qpost]
    cursor.execute("INSERT INTO answers (pid, qid) VALUES (?,?)", questionList)
    conn.commit()
    print("Answer successfully added")


def add_vote(user, pid):  # allows user to add vote to pid
    # check is user already voted
    cursor.execute('SELECT * FROM votes WHERE pid=? AND uid=?', (pid, user,))
    if cursor.fetchone():
        print("You have already voted on this post")
        return None
    else:
        cursor.execute('SELECT count(pid) FROM votes WHERE pid=?', (pid,))  # gets number of votes
        votes = cursor.fetchone()
        vno = votes[0] + 1
        vote_list = [pid, vno, user]
        cursor.execute(" INSERT INTO votes (pid, vno, vdate, uid) VALUES (?,?,date('now'),?); ", vote_list)
        conn.commit()
        print("Vote successfully added")


def signin(name, passw): # Handle user signin here
    sign_in_condition = True
    verifyList = []
    verifyList.append(name)
    verifyList.append(passw)
    cursor.execute(" select name from users WHERE name = ? AND pwd = ?;", verifyList)
    if cursor.fetchone():
        print("user login successful")
    else:
        print("user login unsuccessful")
        sign_in_condition = False
    return sign_in_condition


def register():  # handle user registration here
    usersList = []
    user_id = input("Enter your user id in this format (ex: u001): ")
    usersList.append(user_id)
    user_name = input("Enter your name: ")
    usersList.append(user_name)
    user_city = input("Enter your city of residence: ")
    user_password = getpass.getpass(prompt="Enter Password (case-sensitive) : ")
    usersList.append(user_password)
    usersList.append(user_city)
    cursor.execute(""" insert into users values (?,?, ?, ?, date('now')); """, usersList);
    conn.commit()


def checkprivileged(user):  # check if user is a  privileged user
    privileged_user = False
    rows = cursor.execute("SELECT uid FROM privileged")
    rows = cursor.fetchall()
    for elem in rows:
        if elem[0] == user:
            priveleged_user = True
            return priveleged_user
            # break
    return privileged_user


def add_post(user):
    postList = []
    verifyexist = []
    p_string = 'p'
    post_title = input("Enter your post title: ")
    post_body = input("Enter your post body: ")
    new_id = randint(200,999)
    new_id = p_string + str(new_id)
    verifyexist.append(new_id)
    cursor.execute(" SELECT pid from posts WHERE pid = ?; ", verifyexist)
    if cursor.fetchone():
        new_id = randint(200,999)
        new_id = p_string + str(new_id)
    else:
        pass    
    postList.append(new_id)
    postList.append(post_title)
    postList.append(post_body)
    postList.append(user)    
    cursor.execute(" INSERT INTO posts (pid,pdate, title, body, poster) VALUES (?,date('now'), ?,?,?); ",postList)
    conn.commit()
    print("post successfully added")
    

def addtag(user, pid):  # PU query 3 '3. Post action-Add a tag'
    privileged_user = checkprivileged(user)
    if privileged_user == False:
        print("You are not allowed to use this function\n")
        usertasks(user)
    else:  # add their tag to table
        tag = input("Type the tag you would like to add:\n")
        cursor.execute("INSERT INTO tags VALUES (:pid , :tag)")
        conn.commit()
        print("Tag added successfully\n")


def get_uid_from_name(name):
    print(name)
    cursor.execute("SELECT uid from users WHERE name = ?;", (name,))
    uid = cursor.fetchone()
    return uid


def mark_as_accepted(user, pid):  # PU query 1 '1. Post action-Mark as the accepted'
    accepted_condition = True
    acceptedList = []
    # uid = get_uid_from_name(user)
    # print(uid)
    privileged_user = checkprivileged(user)
    print(privileged_user)
    if privileged_user == False:
        print("Access denied")
        usertasks(user)
    else:
        while accepted_condition:
            answerID = input("please select the answer ID you would like to be marked as accepted: ")
            cursor.execute(" SELECT pid from answers WHERE pid = :answerID; ")
            if cursor.fetchone():
                cursor.execute(" SELECT theaid from questions WHERE pid = ?; ", pid)
                if cursor.fetchone():
                    double_check = input(
                        "this questions seems to already have an accepted answer, would you like to overwrite the current answer (y/n)?: ")
                    if double_check.upper() == "Y":
                        acceptedList.append(answerID)
                        acceptedList.append(pid)
                        cursor.execute(""" UPDATE questions 
                        SET theaid = ?
                        WHERE pid = ?; """, acceptedList)
                        conn.commit()
                        print("answer marked successfully")
                    elif double_check.upper() == "N":
                        break
                    else:
                        print("invalid input, please try again!")
                        continue
                else:
                    acceptedList.append(answerID)
                    acceptedList.append(pid)
                    cursor.execute(""" UPDATE questions 
                    SET theaid = ?
                    WHERE pid = ?; """, acceptedList)
                    conn.commit()
                    print("answer marked successfully")
            else:
                print("the ID you provided does not correspond to an answer, try again!")
                continue


def editpost(user, pid):  # PU query 4 '4. Post Action-Edit'
    privileged_user = checkprivileged(user)

    if privileged_user == False:
        print("You are not allowed to use this function\n")
        usertasks(user)

    else:  # change title and/or body of post
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
    dbname = input(
        "Welcome to this interface, here you can interact with our database system,\nplease enter your sqlite database path to continue: ")
    # dbname = sys.argv[1]  # Handles command line sys arguments (can pass db in terminal)
    while exit_condition:
        connectCheck = connect_db(dbname)
        if connectCheck == True:
            print("Database connected succesfully!")
            exit_condition = False

        else:
            print("an error occured! please try again:")
            dbname = input()
            continue

    # login_menu()
    # usertasks("u069")
    # search_posts()  # test remove later
    add_vote("u069", "p020")  # test remove later
    # add_answer("u069", "p001")  # test remove later


if __name__ == "__main__":
    main()
