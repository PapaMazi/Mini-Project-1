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
    conn.row_factory = lambda cursor, row: row
    cursor = conn.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    conn.commit()
    return True


def login_menu(): # user can log in or register for program
    login_condition = True
    operations = ["1. Login", "2. Register"]
    while login_condition:
        for i in range(len(operations)):
            print(operations[i])
        oper = input("Please select operation or enter 0 to exit: ")
        if oper == "1":
            user = input("Enter Username: ")
            passw = getpass.getpass(prompt="Enter Password: ")
            condition = sign_in(user, passw)
            if condition == True:
                main_menu(user)
                login_condition = False
            else:
                continue
        elif oper == "2":
            user = register()
            print("user succesfully registered.")
            login_condition = False
            main_menu(user)
        elif oper == "0":
            quit()
        else:
            continue

def sign_in(name, passw): # user signs into program
    sign_in_condition = True
    verifyList = []
    verifyList.append(name)
    verifyList.append(passw)
    cursor.execute(" select name from users WHERE uid = ? AND pwd = ?;", verifyList)
    if cursor.fetchone():
        print("user login successful")
    else:
        print("user login unsuccessful")
        sign_in_condition = False
    return sign_in_condition

def register():  # user registers for program
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
    return user_id

def specific_menu(user, pid):
    specific_menu_condition = True
    post_task = input("""Select the post task you would like to perform or 'R' to return to main menu:\n 
    (A): Answer a question\n 
    (V): Vote on a post\n 
    (M): Mark accepted answer (privileged users only)\n 
    (G): Give a badge to a user (privileged users only)\n 
    (T): Add a tag to a post (privileged users only)\n 
    (E): Edit the title or body of a post (privileged users only)\n""")
    while specific_menu_condition:
        if post_task.upper() == 'A':
            specific_menu_condition = False
            add_answer(user, pid)
        elif post_task.upper() == 'V':
            specific_menu_condition = False
            add_vote(user, pid)
        elif post_task.upper() == 'M':
            specific_menu_condition = False
            mark_as_accepted(user, pid)
        elif post_task.upper() == 'G':
            specific_menu_condition = False
            give_badge(user, pid)
        elif post_task.upper() == 'T':
            specific_menu_condition = False
            add_tag(user, pid)
        elif post_task.upper() == 'E':
            specific_menu_condition = False
            edit_post(user, pid)
        elif post_task.upper() == 'R':
            specific_menu_condition = False
            main_menu(user)
        else:
            post_task = input("you inputted an incorrect choice, please try again: ")

def main_menu(user):
    general_menu_condition = True
    task = input("Select the task you would like to perform:\n (P) Post a question\n (S) Search for posts\n or enter 0 to exit")
    while general_menu_condition:
        if task.upper() == 'P':
            add_question(user)
            general_menu_condition = False
        elif task.upper() == 'S':
            search_posts(user)
            #call specific_menu from search posts with selected pid
            general_menu_condition = False
        elif task.upper() == '0':
            quit()
        else:
            task = input("you inputted an incorrect choice, please try again: ")
            continue

def get_uid_from_name(name):
    print(name)
    cursor.execute("SELECT uid from users WHERE name = ?;", (name,))
    uid = cursor.fetchone()
    return uid

def add_question(user): # U query 1 '1. Post a question'
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

def search_posts(user): # U query 2 '2. Search for posts'
    # TODO: test if results are ordered based on #of kw
    # TODO: test case insensitivity
    # TODO: test partial matching (see: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=1537384)
    # TODO: need to implement error checking (if pids is empty then make user try again)
    kw_check = True
    keywords = ''
    while kw_check:
        if not keywords:
            keywords = input("Please enter keywords separated by a comma: ")
        else:
            kw_check = False
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
        search_posts()
    else:  # if pids[] not empty then:
        pid_count = {i:pids.count(i) for i in pids}  #counts # https://stackoverflow.com/questions/23240969/python-count-repeated-elements-in-the-list/23240989
        pid_count = sorted(pid_count.items(), key=lambda v: v[1], reverse=True)  #orders based on # of kw  # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        results = []
        for pid in pid_count:
            cursor.execute('SELECT * FROM posts WHERE pid=?;', (pid[0],))  # fetches results
            results.append(cursor.fetchone())
        print_results(results, user)  # print results

def print_results(data, user):  # handle printing search results here
    # TODO: test listing 5 results at a time
    # TODO: need to implement selection of posts
    table = PrettyTable(['PID', 'Post Date', 'Title', 'Body', 'Poster', 'Votes', 'Answers'])

    check = True
    while check:
        for i in range(0, len(data), 5):
            print_table(data[i:i+5])
            ind = input("Would you like to see next page? (Y/N) or enter pid: ")
            if ind.lower() == "y":
                continue
            elif ind.lower() == 'n':
                break
                # check = False
            elif re.match('[a-zA-Z]{1}\d{3}', ind):
                specific_menu(user, ind)
                continue
            else:
                ind = input("Invalid Input. Please try again: ")
                check = True
            if i >= (len(data) - 5):
                break
        check = False

def print_table(data):
    table = PrettyTable(['PID', 'Post Date', 'Title', 'Body', 'Poster', 'Votes', 'Answers'])
    for i in data:  # prints data in table format (prints all results)
        cursor.execute('SELECT count(pid) FROM votes WHERE pid=?', (i[0],))  # gets number of votes
        i = i + cursor.fetchone()
        cursor.execute('SELECT count(qid) FROM answers WHERE qid =?', (i[0],))  # gets number of answers if question
        i = i + cursor.fetchone()
        table.add_row(i)
    print(table)

def add_answer(user, qpost):  # U query 3 '3. Post action-Answer'
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


def add_vote(user, pid):  # U query 4 '4. Post action-Vote'
    cursor.execute('SELECT count(pid) FROM votes WHERE pid=?', (pid,))  # gets number of votes
    votes = cursor.fetchone()
    vno = votes[0] + 1
    vote_list = [pid, vno, user]
    cursor.execute(" INSERT INTO votes (pid, vno, vdate, uid) VALUES (?,?,date('now'),?); ", vote_list)
    conn.commit()
    print("Vote successfully added")

def check_privileged(user):  # check if user is a privileged user
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


def check_badge(badgename):
    badgeList = [badgename]
    cursor.execute("SELECT bname from badges WHERE bname = ?;", badgeList)
    if cursor.fetchone():
        return True
    else:
        return False
    
    
def give_badge(user, pid): # PU query 2 '2. Post action-Give a badge'
    badge_name = input("please input the badge name you would like to give: ")
    badge_condition = True
    while badge_condition:
        if check_badge(badge_name) == True:
            badge_condition = False
        else:
            badge_name = input("you inputted an incorrect badge name, please try again: ")
            continue
    
    checkList = [pid]
    cursor.execute(" SELECT poster from posts WHERE pid = ?;", checkList)
    poster = cursor.fetchone()
    checkList = [poster, badge_name]
    cursor.execute(" INSERT OR REPLACE INTO ubadges (uid, bdate, bname) VALUES (?, date('now'), ?); ",checkList)
    conn.commit()
    print("badge succesfully added")
    

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
    uid = get_uid_from_name(user)
    print(uid)
    privileged_user = checkprivileged(user)
    print(privileged_user)
    if privileged_user == False:
        print("You are not allowed to use this function\n")
        specific_menu(user, pid)
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


def give_badge(user, pid): # PU query 2 '2. Post action-Give a badge'
    privileged_user = check_privileged(user)
    if privileged_user == False:
        print("You are not allowed to use this function\n")
        specific_menu(user, pid)

    badge_name = input("please input the badge name you would like to give: ")
    badge_condition = True
    while badge_condition:
        if check_badge(badge_name) == True:
            badge_condition = False
        else:
            badge_name = input("you inputted an incorrect badge name, please try again: ")
            continue
    
    checkList = [pid]
    cursor.execute(" SELECT poster from posts WHERE pid = ?;", checkList)
    poster = cursor.fetchone()
    checkList = [poster, badge_name]
    cursor.execute(" INSERT OR REPLACE INTO ubadges (uid, bdate, bname) VALUES (?, date('now'), ?); ",checkList)
    conn.commit()
    print("badge succesfully added")
    specific_menu(user, pid)

def check_badge(badgename):
    badgeList = [badgename]
    cursor.execute("SELECT bname from badges WHERE bname = ?;", badgeList)
    if cursor.fetchone():
        return True
    else:
        return False
    

def add_tag(user, pid):  # PU query 3 '3. Post action-Add a tag'
    privileged_user = check_privileged(user)
    if privileged_user == False:
        print("You are not allowed to use this function\n")
    else:  # add their tag to table
        #check that tag does not already exist
        tag_duplicate = True;
        new_tag = input("Type the tag you would like to add:\n")
        while tag_duplicate:
            rows = cursor.execute("SELECT tag FROM tags")
            rows = cursor.fetchall()
            tag_duplicate = False
            for elem in rows:
                if elem[0].upper() == new_tag.upper():
                    tag_duplicate = True
                    new_tag = input("That tag already exists, try adding different one:\n")
        tagList = [pid, new_tag]
        cursor.execute("INSERT INTO tags VALUES (?, ?);", tagList)
        conn.commit()
        print("Tag added successfully\n")
    specific_menu(user, pid)



def edit_post(user, pid):  # PU query 4 '4. Post Action-Edit'
    privileged_user = check_privileged(user)
    if privileged_user == False:
        print("You are not allowed to use this function\n")
        specific_menu(user, pid)

    else:  # change title and/or body of post
        user_choice = input("Would you like to edit the title of this post? (Y) or (N)\n")
        if user_choice == 'Y':
            new_title = input("What would you like the new title to be?\n")
            titleList [new_title, pid]
            cursor.execute(""" UPDATE posts 
                        SET title = ?
                        WHERE pid = ? ;""", titleList)
            print("Title changed successfully\n")

        user_choice = input("Would you like to edit the body of this post? (Y) or (N)\n")
        if user_choice == 'Y':
            new_body = input("What would you like the new body to be?\n")
            bodyList = [new_body, pid]
            cursor.execute(""" UPDATE posts 
                        SET body = ?
                        WHERE pid = ? ;""", bodyList)
            conn.commit()
            print("Body changed successfully\n")

    specific_menu(user, pid)

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

    #login_menu()
    mark_as_accepted("u069","p004")
    # usertasks("u069")
    # give_badge("u069","p004")
    # search_posts()  # test remove later
    # add_vote("u069", "p020")  # test remove later
    # add_answer("u069", "p001")  # test remove later


if __name__ == "__main__":
    main()
