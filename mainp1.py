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


def convertTuple(tup):
    str = ''.join(tup)
    return str


def main_menu(user):
    # TODO: need to implement logout functionality
    general_menu_condition = True
    task = input("Select the task you would like to perform:\n (P) Post a question\n (S) Search for posts\n (0) Exit program: ")
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
            print("Invalid Input. Please try again.")
            task = input("Select the task you would like to perform:\n (P) Post a question\n (S) Search for posts\n (0) Exit program: ")
            continue


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
            if condition:
                user = get_uid_from_name(user)
                user = convertTuple(user)
                main_menu(user)
                login_condition = False
            else:
                continue
        elif oper == "2":
            user = register()
            print("User successfully registered.")
            login_condition = False
            main_menu(user)
        elif oper == "0":
            quit()
        else:
            continue


def sign_in(name, passw): # user signs into program
    sign_in_condition = True
    # verifyList = []
    uid = get_uid_from_name(name)
    uid = convertTuple(uid)
    verifyList = [uid.upper(),passw]
    cursor.execute(" select name from users WHERE upper(uid) = ? AND pwd = ?;", verifyList)
    if cursor.fetchone():
        print("user login successful")
    else:
        print("user login unsuccessful")
        sign_in_condition = False

    return sign_in_condition


def specific_menu(user, pid):
    specific_menu_condition = True
    post_task = input("""Select the post task you would like to perform or 'R' to return to main menu:\n 
    (A): Answer a question\n 
    (V): Vote on a post\n 
    (M): Mark accepted answer (privileged users only)\n 
    (G): Give a badge to a user (privileged users only)\n 
    (T): Add a tag to a post (privileged users only)\n 
    (E): Edit the title or body of a post (privileged users only)\n
    (L): Logout\n""")
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
        elif post_task.upper() == 'L':
            specific_menu_condition = False
            login_menu()
        else:
            post_task = input("you inputted an incorrect choice, please try again: ")
            continue


def register():  # user registers for program
    register_condition= True
    while register_condition:
        user_id = input("Enter your user id in this format (ex: u001): ")
        cursor.execute(" SELECT uid from users WHERE uid = ?;", (user_id,))
        if cursor.fetchone():
            print("the user_id you entered already exists, please try another one")
        else:
            register_condition = False
    user_name = input("Enter your name: ")
    user_city = input("Enter your city of residence: ")
    user_password = getpass.getpass(prompt="Enter Password (case-sensitive) : ")
    usersList = [user_id.upper(), user_name.upper(), user_password, user_city.upper()]
    cursor.execute(""" insert into users values (?,?, ?, ?, date('now')); """, usersList);
    conn.commit()
    return user_id


def get_uid_from_name(name): # get the uid for a given username
    name = name.upper()
    cursor.execute("SELECT uid from users WHERE upper(name) = ?;", (name,))
    uid = cursor.fetchone()
    return uid


def check_privileged(user):  # check if user is a privileged user
    user = user.upper()
    privileged_user = False
    rows = cursor.execute("SELECT uid FROM privileged")
    rows = cursor.fetchall()
    for elem in rows:
        if elem[0].upper() == user:
            priveleged_user = True
            return priveleged_user
            # break
    return privileged_user


def add_question(user): # U query 1 '1. Post a question'
    p_string = 'p'
    post_title = input("Enter your post title: ")
    post_body = input("Enter your post body: ")
    new_id = randint(200,999)
    new_id = p_string + str(new_id)
    new_id = new_id.upper()
    verifyexist = [new_id]
    cursor.execute(" SELECT pid from posts WHERE upper(pid) = ?; ", verifyexist)
    if cursor.fetchone():
        new_id = randint(200,999)
        new_id = p_string + str(new_id)
    else:
        pass
    postList = [new_id.upper(), post_title.upper(), post_body.upper(), user]
    cursor.execute(" INSERT INTO posts (pid,pdate, title, body, poster) VALUES (?,date('now'), ?,?,?); ",postList)
    conn.commit()
    questionList = [new_id]
    cursor.execute("INSERT INTO questions (pid) VALUES (?)", questionList)
    conn.commit()
    print("post successfully added")


def search_posts(user):  # U query 2 '2. Search for posts'
    # TODO: test if results are ordered based on #of kw
    # TODO: test case insensitivity
    # TODO: test partial matching (see: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=1537384)
    user = user.upper()

    kw_check = True
    keywords = ''
    while kw_check:
        if not keywords:
            keywords = input("Please enter keywords separated by a comma (press 0 to return to main menu): ")
        else:
            kw_check = False
    if keywords.lower() == '0':
        main_menu(user)
    keywords = "".join(keywords.split())
    keywords = keywords.split(",")
    cursor.execute("SELECT pid, title, body, tag FROM posts LEFT OUTER JOIN tags USING (pid);")
    posts = cursor.fetchall()
    pids = []

    for item in keywords:  # for each keyword the user entered
        for row in posts:  # for each row from posts
            for field in row:  # for each field in row
                if field is not None:
                    if item.upper() in field.upper():  # check if keyword is in the field
                        pids.append(row[0])  # if kw is in row then add pid to pid[]

    if not pids:  # if pids[] is empty
        print("Couldn't find any matches")
        search_posts(user)
    else:  # if pids[] not empty then:
        pid_count = {i:pids.count(i) for i in pids}  #counts # https://stackoverflow.com/questions/23240969/python-count-repeated-elements-in-the-list/23240989
        pid_count = sorted(pid_count.items(), key=lambda v: v[1], reverse=True)  #orders based on # of kw  # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        results = []
        for pid in pid_count:
            if pid[0] is not None:
                cursor.execute('SELECT * FROM posts WHERE upper(pid)=?;', (pid[0].upper(),))  # fetches results
                results.append(cursor.fetchone())
        print_results(results, user)  # print results


def print_results(data, user):  # handle printing search results here
    # TODO: actually data independent? what if pid is not pXXX?

    print(len(data), "results found.")  # prints # of results found
    for i in range(0, len(data), 5):  # iterates 5 at a time, printing results
        print_table(data[i:i + 5])
        valid_input = True
        if len(data[i:i + 5]) == 5:
            user_input = input("Press enter to see next page or enter pid for post actions (press 0 to return to main menu): ")
        else:
            user_input = input("Enter pid for post actions (press 0 to return to main menu): ")
        while valid_input:  # while loop checks if user enters valid inputs
            if re.match('[a-zA-Z]{1}\d{3}', user_input):  # if user enters a pid, call specific_menu(user, pid)
                valid_input = False
                specific_menu(user, user_input)
                main_menu(user)
            elif user_input == '':  # if users presses enter, show next page of results
                if len(data[i:i + 5]) != 5:
                    user_input = input("Enter pid for post actions (press 0 to return to main menu): ")
                else:
                    valid_input = False
                    continue
            elif user_input.lower() == '0':  # pressing 0 takes user back to main menu
                valid_input = False
                main_menu(user)
            else:
                print("Invalid Input. Please try again.")
                user_input = input("Press enter to see next page or enter pid for post actions (press 0 to return to main menu): ")


def print_table(data): # handle printing the table here
    table = PrettyTable(['PID', 'Post Date', 'Title', 'Body', 'Poster', 'Votes', 'Answers'])
    for i in data:  # prints data in table format (prints all results)
        cursor.execute('SELECT count(pid) FROM votes WHERE pid=?', (i[0],))  # gets number of votes
        i = i + cursor.fetchone()
        cursor.execute('SELECT count(qid) FROM answers WHERE qid =?', (i[0],))  # gets number of answers if question
        i = i + cursor.fetchone()
        table.add_row(i)
    print(table)


def add_answer(user, qpost):  # U query 3 '3. Post action-Answer'
    # postList = []
    verifyexist = []
    p_string = 'p'
    post_title = input("Enter your post title: ")
    post_body = input("Enter your post body: ")
    new_id = randint(200,999)
    new_id = p_string + str(new_id)
    verifyexist.append(new_id)
    cursor.execute(" SELECT pid from posts WHERE upper(pid) = ?; ", verifyexist)
    if cursor.fetchone():
        new_id = randint(200,999)
        new_id = p_string + str(new_id)
    else:
        pass
    postList = [new_id.upper(), post_title.upper(), post_body.upper(),user]
    cursor.execute(" INSERT INTO posts (pid,pdate, title, body, poster) VALUES (?,date('now'), ?,?,?); ",postList)
    conn.commit()
    cursor.execute('SELECT pid FROM posts WHERE lower(pid) = ?', (qpost.lower(),))
    qpost = cursor.fetchone()
    answerList = [new_id, qpost[0]]
    cursor.execute("INSERT INTO answers (pid, qid) VALUES (?,?)", answerList)
    conn.commit()
    print("Answer successfully added")


def add_vote(user, pid):  # U query 4 '4. Post action-Vote'
    cursor.execute('SELECT count(pid) FROM votes WHERE lower(pid) = ?', (pid.lower(),))  # gets number of votes
    votes = cursor.fetchone()
    cursor.execute('SELECT pid FROM posts WHERE lower(pid) = ?', (pid.lower(),))
    match_pid = cursor.fetchone()  # actual pid to enforce foreign key constraints
    vno = votes[0] + 1
    vote_list = [match_pid[0], vno, user]
    cursor.execute(" INSERT INTO votes (pid, vno, vdate, uid) VALUES (?,?,date('now'),?); ", vote_list)
    conn.commit()
    print("Vote successfully added")


def check_badge(badgename): # checks if badge name is valid
    badgeList = [badgename]
    cursor.execute("SELECT bname from badges WHERE bname = ?;", badgeList)
    if cursor.fetchone():
        return True
    else:
        return False


def mark_as_accepted(user, pid):  # PU query 1 '1. Post action-Mark as the accepted'
    accepted_condition = True
    acceptedList = []
    uid = get_uid_from_name(user)
    privileged_user = check_privileged(user)
    if privileged_user == False:
        print("You are not allowed to use this function\n")
        specific_menu(user, pid)
    else:
        while accepted_condition:
            answerID = input("please select the answer ID you would like to be marked as accepted: ")
            answerList = [answerID.upper()]
            cursor.execute(" SELECT pid from answers WHERE upper(pid) = ?; ",answerList)
            if cursor.fetchone():
                pidList = [pid.upper()]
                cursor.execute(" SELECT theaid from questions WHERE upper(pid) = ?; ", pidList)
                if cursor.fetchone():
                    double_check = input(
                        "this questions seems to already have an accepted answer, would you like to overwrite the current answer (y/n)?: ")
                    if double_check.upper() == "Y":
                        acceptedList = [answerID.upper(), pid.upper()]
                        cursor.execute(""" UPDATE questions 
                        SET theaid = ?
                        WHERE pid = ?; """, acceptedList)
                        conn.commit()
                        print("answer marked successfully")
                        accepted_condition = False
                    elif double_check.upper() == "N":
                        break
                    else:
                        print("Invalid Input. Please try again.")
                        continue
                else:
                    acceptedList = [answerID.upper(), pid.upper()]
                    cursor.execute(""" UPDATE questions 
                    SET theaid = ?
                    WHERE upper(pid) = ?; """, acceptedList)
                    conn.commit()
                    print("answer marked successfully")
                    accepted_condition = False
            else:
                print("the ID you provided does not correspond to an answer, try again!")
                continue
    specific_menu(user, pid)


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

    checkList = [pid.upper()]
    cursor.execute(" SELECT poster from posts WHERE upper(pid) = ?;", checkList)
    poster = cursor.fetchone()
    poster = convertTuple(poster)
    checkList = [poster, badge_name]
    cursor.execute(" INSERT OR REPLACE INTO ubadges (uid, bdate, bname) VALUES (?, date('now'), ?); ",checkList)
    conn.commit()
    print("badge succesfully added")
    specific_menu(user, pid)


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
        if user_choice.upper() == 'Y':
            new_title = input("What would you like the new title to be?\n")
            titleList = [new_title, pid]
            cursor.execute(""" UPDATE posts 
                        SET title = ?
                        WHERE pid = ? ;""", titleList)
            conn.commit()
            print("Title changed successfully\n")

        user_choice = input("Would you like to edit the body of this post? (Y) or (N)\n")
        if user_choice.upper() == 'Y':
            new_body = input("What would you like the new body to be?\n")
            bodyList = [new_body.upper(), pid]
            cursor.execute(""" UPDATE posts 
                        SET body = ?
                        WHERE pid = ? ;""", bodyList)
            conn.commit()
            print("Body changed successfully\n")

    specific_menu(user, pid)


def main():
    exit_condition = True
    dbname = input("Enter your sqlite database path to continue: ")  # DELETE BEFORE SUBMISSION
    # dbname = sys.argv[1]  # Handles command line sys arguments (can pass db in terminal)
    while exit_condition:
        connectCheck = connect_db(dbname)
        if connectCheck:
            print("Database connected succesfully!")
            exit_condition = False
        else:
            print("an error occured! please try again:")
            dbname = input()
            continue
    login_menu()
    # main_menu()


if __name__ == "__main__":
    main()
