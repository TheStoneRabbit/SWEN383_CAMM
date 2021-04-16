from flask import Flask, render_template, redirect, url_for, request, session
import time 
import hashlib 
import getpass
import re
import mysql.connector
from mysql.connector.cursor import MySQLCursor
from flask_table import Table, Col
from localStoragePy import localStoragePy
from werkzeug import *

# Below is MySQL code once database is created
UPLOAD_FOLDER = 'uploads/'

# Enter the password for your MySQL database below
# Username SHOULD be 'root'
print("=================")
MySQL_PASSWORD = getpass.getpass(prompt='MYSQL DB PASSWORD> ')
print("=================")
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=MySQL_PASSWORD,
  database="myPLS"
)
# Assigns cursor to traverse through database values
mycursor = mydb.cursor(buffered=True)
# End MySQL code
userID = ""
email = ""
app = Flask(__name__)
app.secret_key = 'cammgroup'
firstName = ""
lastName = ""
courseID = ""
userCode = ""


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ LOGIN PROCESS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++
# START OF APP THAT REDIRECTS TO THE LOGIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/')
def start():
    session['logged_in'] = 'false'
    return redirect(url_for("login"))



# +++++++++++++++++++++++++++++++++++++++++++++
# REDIRECTING TO LOGIN PAGE
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/home',  methods=['GET', 'POST'])
def home():
    name = mydb.cursor(buffered=True)
    #print(userID)
    name.execute("SELECT firstName FROM user WHERE email = "+ "'" + userID + "'")
    firstName = name.fetchall()
    #print(firstName)
    firstName = re.sub("[()]|,|'", "", str(userID)) #Removes extra characters
    if session['logged_in'] != 'false':
        return "<h1 style='text-align:center;'>Welcome " + firstName + "</h1><br>" +render_template('index.html')
    else:
        return redirect(url_for("login"))



# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING THE LOGIN PAGE
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/login',  methods=['GET', 'POST'])
def login():
    mycursor.execute("SELECT email FROM user")
    numRows = mycursor.rowcount

    bad_chars = ["(", ")", ",", "\'"]
    if request.method == 'POST':
        rowsUser = mycursor.fetchall()
        # mycursor.close()
        newCursor = mydb.cursor(buffered=True)
        newCursor.execute("SELECT hashPassword FROM user")
        rowsPass = newCursor.fetchall()
        cred_pass_one = False
        cred_pass_two = False
        # newCursor.close()
        # These for loops test if username and password is in db.
        pos = 0
        subbed_one = ""
        # print(rowsUser)
        for x in rowsUser:
            subbed_one = re.sub("(|)|,|'", "", str(x))
            pos += 1
            if "(" + request.form['username']+ ")" == subbed_one :
                global email
                global userID
                userID = subbed_one
                email = request.form['username']
                cred_pass_one = True
                break
            else:
                cred_pass_one = False
        second_pos = 0
        for y in rowsPass:
            req_pass = str(request.form['password'])
            pass_encode = hashlib.sha256(req_pass.encode())
            subbed_two = re.sub("(|)|,|'", "", str(y))
            y = re.sub("(|)|,|'", "", str(y))
            second_pos += 1
            #print("("+str(pass_encode.hexdigest()) + ")")
            #print(str(second_pos) + " :: " + str(pos))
            #print(y)
            #print(subbed_two)
            if "(" + str(pass_encode.hexdigest())+ ")"  ==  subbed_two and second_pos == pos:
                cred_pass_two = True
                break
            else: 
                cred_pass_two = False
        #print(str(cred_pass_one) + " " + str(cred_pass_two))
        # If the password is in and the password matches then log in
        if cred_pass_one == True and cred_pass_two == True:
            session['logged_in'] = 'true'
            user_type = mydb.cursor(buffered=True)
            subbed_one = re.sub("[()]|,|'", "", str(subbed_one))
            #print(subbed_one)
            user_type.execute("SELECT typeU, userID FROM user WHERE email=" + "'" +subbed_one + "'")
            permission_level = user_type.fetchall()
            # global userCode
            # userCode = permission_level[1]
            subbed_permission = re.sub("(|)|,|'", "", str(permission_level[0]))
            userCodeX = subbed_permission.split(" ")
            global userCode
            userCode = userCodeX[1].replace(")", "")
            subbed_permission = subbed_permission.split(" ")[0] + ")"
            session["permission_level"] = subbed_permission
            if session["permission_level"] == "(0)":
                return redirect(url_for("admin_panel_index"))
            if session["permission_level"] == "(1)":
                return redirect(url_for("professor_panel_index"))
            return redirect(url_for('login_success'))
        else:
            return redirect(url_for('failure'))
                
    return render_template("sign_in.html")



# +++++++++++++++++++++++++++++++++++++++++++++
# SUCCESSFUL LOGIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/success')
def login_success():
    if session['logged_in'] != 'false':
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))



# +++++++++++++++++++++++++++++++++++++++++++++
# FAILED LOGIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/invalidcredentials')
def failure():
    session['logged_in'] = 'false'
    return render_template("failure.html")



# +++++++++++++++++++++++++++++++++++++++++++++
# REDIRECTS TO LOGOUT
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/logout',  methods=['GET', 'POST'])
def logout():
    session['logged_in'] = 'false'
    return redirect(url_for("login"))



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ ADMIN SYSTEM ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING THE DEFAULT ADMIN COURSE DASH
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/adminpanelindex',  methods=['GET', 'POST'])
def admin_panel_index():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            courseData = mydb.cursor(buffered=True)
            courseData.execute("SELECT * FROM course")
            items = courseData.fetchall()
            htmlRender = [] 
            piece = []
            count  = 0
            for x in items:
                for i in x:
                    if count == 4 or count == 3:
                        i = str(i)
                        i = i.split(", ")
                    piece.append(i)
                    count += 1
                htmlRender.append(piece)
                piece = []
                count = 0
            userName = mydb.cursor(buffered=True)
            userName.execute("SELECT firstName, lastName, userID FROM user WHERE email='"+ email+ "'")
            names = userName.fetchall()
            nameRender = []
            for x in names:
                for i in x:
                    nameRender.append(i)
            global firstName
            global lastName
            
            if request.method == 'POST':
                deletefromEnrollment = mydb.cursor(buffered=True)
                sqlTwo = "DELETE FROM enrollment WHERE courseID='" + request.form.get("course") + "'"
                
                deletefromEnrollment.execute(sqlTwo)
                deletefrom = mydb.cursor(buffered=True)
                sql = "DELETE FROM course WHERE courseID='" + request.form.get("course") + "'"
                deletefrom.execute(sql)
                mydb.commit()
                return redirect(url_for("admin_panel_index"))
           
            lastName = nameRender[1]
            firstName = nameRender[0]
            return render_template("admin_dash.html", listy=htmlRender, first=nameRender[0], last=nameRender[1])
          
        else: 
            return redirect(url_for("failure"))
    else:
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# ADDING A USER TO THE SYSTEM
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/adminpaneladd',  methods=['GET', 'POST'])
def admin_panel_add():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                insertinto = mydb.cursor(buffered=True)
                sql = "INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) VALUES (%s, %s, %s, %s, %s, %s)"
                req_pass = str(request.form['password'])
                pass_encode = hashlib.sha256(req_pass.encode())
                try:
                    values = (request.form["firstname"], request.form["lastname"],int(request.form["userID"]), request.form["email"], pass_encode.hexdigest(), int(request.form["type"]))
                    insertinto.execute(sql, values)
                    mydb.commit()
                    return render_template("entries_added.html")
                except:
                    return render_template("query_error.html")
            return render_template("adminpaneladd.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# REMOVING A USER FROM THE SYSTEM
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/adminpanelremove',  methods=['GET', 'POST'])
def admin_panel_remove():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                deletefromStudentGroups = mydb.cursor(buffered=True)
                sql = "DELETE FROM studentGroups WHERE userID = " + str(int(request.form["username"]))
                # values = int(request.form["username"])
                deletefromStudentGroups.execute(sql)
                deletefromEnrollment = mydb.cursor(buffered=True)
                sqlThree = "DELETE FROM enrollment WHERE userID = " + str(int(request.form["username"]))
                deletefromEnrollment.execute(sqlThree)
                deletefromUser = mydb.cursor(buffered=True)
                sqlTwo = "DELETE FROM user WHERE userID = " + str(int(request.form["username"]))
                deletefromUser.execute(sqlTwo)
                mydb.commit()
                return render_template("entries_removed.html")
            return render_template("adminpanelremove.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING THE ADMIN USER DASH
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/admin_user_dash', methods=['GET', 'POST'])
def admin_user_dash():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            allData = mydb.cursor(buffered=True)
            allData.execute("SELECT firstName, lastName, userID, email FROM user WHERE typeU=0")
            items = allData.fetchall()
            htmlRender = []
            numOfItems = len(items)
            lenX = 4
            for x in items:
                for i in x:
                    htmlRender.append(i)
            allData.execute("SELECT firstName, lastName, userID, email FROM user WHERE typeU=1")
            items1 = allData.fetchall()
            numOfItems1 = len(items1)
            lenX1 = 4
            for x1 in items1:
                for i1 in x1:
                    htmlRender.append(i1)
            allData.execute("SELECT firstName, lastName, userID, email FROM user WHERE typeU=2")
            items2 = allData.fetchall()
            numOfItems2 = len(items1)
            lenX2 = 4
            for x2 in items2:
                for i2 in x2:
                    htmlRender.append(i2)
            allData.execute("SELECT firstName, lastName FROM user WHERE email='"+ email+ "'")
            names = allData.fetchall()
            nameRender = []
            for x in names:
                for i in x:
                    nameRender.append(i)
            global firstName
            if nameRender[0] != "":
                firstName = nameRender[0]
            global lastName
            if nameRender[1] != "":
                lastName = nameRender[1]
            return render_template("admin_dash_user.html", htmlRender=htmlRender, items=items, x=lenX, items1=items1, x1=lenX1, items2=items2, x2=lenX2, first=firstName, last=lastName)
        else:
            return redirect(url_for("failure"))  
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# ADDING A COURSE
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/addcourse',  methods=['GET', 'POST'])
def admin_course():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                insertinto = mydb.cursor(buffered=True)
                sql = "INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) VALUES (%s, %s, %s, %s, %s)"
                try:
                    values = (request.form["courseID"], request.form["courseName"],int(request.form["capacity"]), request.form["Location"], request.form["times"])
                    insertinto.execute(sql, values)
                    mydb.commit()
                    return render_template("entries_added.html")
                except:
                    return render_template("query_error.html")
            return render_template("add_course.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# REMOVING A COURSE
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++ 
@app.route('/removecourse',  methods=['GET', 'POST'])
def remove_course():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            
            return render_template("entries_removed.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING UP A SPECIFIC COURSE PAGE
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/tocourse/<course>', methods=['GET', 'POST'])
def to_course(course):
    global courseID
    courseID = course
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            getSpecificCourseData = mydb.cursor(buffered=True)
            getSpecificCourseData.execute("SELECT courseID, courseName, capacity, courseLoc, courseTimes, firstName, LastName, typeU FROM course JOIN enrollment USING(courseID) JOIN user ON enrollment.userID = user.userID WHERE courseID='"+ course+ "' ORDER BY typeU ASC;")
            items = getSpecificCourseData.fetchall()
            classinfo = []
            outerList = []
            count = 0
            for x in items:
                for i in x:
                    if count == 4:
                        i = str(i)
                        i = i.split(", ")
                    classinfo.append(i)
                    count += 1
                outerList.append(classinfo)
                classinfo = []
                count = 0
            if outerList == []:
                return redirect(url_for("failure"))
            else:
                return render_template("course.html", courseinfo=outerList)
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# ADDING A USER TO A SPECIFIC COURSE
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/addusertocourse', methods=['GET', 'POST'])
def admin_add_user_to_course():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                insertinto = mydb.cursor(buffered=True)
                sql = "INSERT INTO enrollment (courseID, userID) VALUES (%s, %s)"
                try:
                    values = (courseID, int(request.form["userID"]))
                    insertinto.execute(sql, values)
                    mydb.commit()
                    return render_template("entries_added.html")
                except:
                    return render_template("query_error.html")
            return render_template("add_user_to_course.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# REMOVING A USER FROM A SPECIFIC COURSE
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/removeuserfromcourse', methods=['GET', 'POST'])
def admin_remove_user_from_course():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                removefrom = mydb.cursor(buffered=True)
                sql = "DELETE FROM enrollment WHERE courseID = '" + courseID + "' AND userID = " + str(int(request.form["userID"]))
                removefrom.execute(sql)
                mydb.commit()
                return render_template("entries_removed.html")
            return render_template("remove_user_from_course.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING THE ADMIN GROUP DASH
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route("/admin_dash_group")
def admin_group_dash():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            groupData = mydb.cursor(buffered=True)
            sql = "SELECT studentGroups.groupID, group_concat(studentGroups.userID) AS 'Users in Group', title, group_description FROM user_group JOIN studentGroups ON studentGroups.groupID = user_group.groupID JOIN user ON studentGroups.userID = user.userID WHERE user.userID = studentGroups.userID GROUP BY user_group.groupID"
            groupData.execute(sql)
            items = groupData.fetchall()
            htmlRender = []
            numOfItems = len(items)
            piece = []
            existing_groups = []
            usersHold = []
            userNums = []
            count = 0
            appendItems = False
            mySplit = False
            out = [k for t in items for k in t]
            j = []
            k = [out[i:i + 4] for i in range(0, len(out), 4)]
            htmlRender = k
            for i in range(0, len(htmlRender)):
                for x in htmlRender[i][1].split(","):
                    if x not in userNums:
                        userNums.append(x)
                usersHold.append(userNums)
                userNums = []
            print(usersHold)
            return render_template("admin_dash_group.html", userGroupData=htmlRender, items=items, last=lastName, first=firstName, userGroupNums=usersHold)
        else: 
            return redirect(url_for("failure"))
    else:
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING UP A SPECIFIC GROUP PAGE
# PERMISSION LEVEL: ADMIN
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/togroup/<group>', methods=['GET', 'POST'])
def to_group(group):
    global groupID
    groupID = group
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            getSpecificGroupData = mydb.cursor(buffered=True)
            getSpecificGroupData.execute("SELECT groupID, title, group_description, group_concat(studentGroups.userID) AS Users FROM user_group JOIN studentGroups USING(groupID) JOIN user ON studentGroups.userID = user.userID WHERE groupID='"+ group+ "' GROUP BY title ORDER BY typeU ASC;")
            items = getSpecificGroupData.fetchall()
            groupInfo = []
            outerList = []
            usersForGroup = []
            count = 0
            for x in items:
                for i in x:
                    if count == 4:
                        i = str(i)
                        i = i.split(", ")
                    groupInfo.append(i)
                    count += 1
                outerList.append(groupInfo)
                groupInfo = []
                count = 0
            for l in outerList[0][3].split(","):
                if l not in usersForGroup:
                    usersForGroup.append(l)
            if outerList == []:
                return redirect(url_for("failure"))
            else:    
                if request.method == 'POST':
                    print(outerList)
                    deletefrom = mydb.cursor(buffered=True)
                    sql = "INSERT INTO studentGroups (userID, groupID, post) VALUES (%s, %s, %s)"
                    try:
                        insertinto = mydb.cursor(buffered=True)
                        values = (userCode, groupID, request.form["makePostInput"])
                        insertinto.execute(sql, values)
                        mydb.commit()
                        return render_template("entries_added.html")
                    except:
                        return render_template("query_error.html")
                    return redirect(url_for("group"))
                return render_template("group.html", groupUsers=usersForGroup, groupInfo=outerList)
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# I'm Not Sure What This is - May be Old
@app.route('/group',  methods=['GET', 'POST'])
def add_group():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            groupData = mydb.cursor(buffered=True)
            groupData.execute("SELECT * FROM user_group")
            items = groupData.fetchall()
            htmlRender = [] 
            piece = []
            count  = 0
            for x in items:
                for i in x:
                    if count == 4 or count == 3:
                        i = str(i)
                        i = i.split(", ")
                    piece.append(i)
                    count += 1
                htmlRender.append(piece)
                piece = []
                count = 0
            userName = mydb.cursor(buffered=True)
            userName.execute("SELECT firstName, lastName FROM user WHERE email='" + email + "'")
            names = userName.fetchall()
            nameRender = []
            for x in names:
                for i in x:
                    nameRender.append(i)
            global firstName
            
            global lastName
            
            if request.method == 'POST':
                insertinto = mydb.cursor(buffered=True)
                sql = "INSERT INTO studentGroups (userID, groupID, userPost) VALUES (%s, %s, %s)"
                try:
                    values = (5876, groupID, request.form["makePostInput"])
                    insertinto.execute(sql, values)
                    mydb.commit()
                    return render_template("entries_added.html")
                except:
                    return render_template("query_error.html")
                return redirect(url_for("group"))
            try:
                lastName = nameRender[1]
                firstName = nameRender[0]
                return render_template("group.html", listy=htmlRender, first=nameRender[0], last=nameRender[1])
            except:
                return redirect(url_for("failure"))
            return render_template("group.html")
            
        else: 
            return redirect(url_for("failure"))
    else:
        return redirect(url_for("failure"))



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ PROFESSOR SYSTEM ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING THE DEFAULT PROFESSOR COURSE DASH
# PERMISSION LEVEL: PROFESSOR
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/professorpanelindex',  methods=['GET', 'POST'])
def professor_panel_index():
    if session["permission_level"] == "(1)":
        if session["logged_in"] != 'false':
            userName = mydb.cursor(buffered=True)
            userName.execute("SELECT firstName, lastName, userID FROM user WHERE email='"+ email+ "'")
            names = userName.fetchall()
            nameRender = []
            for x in names:
                for i in x:
                    nameRender.append(i)
            global firstName
            global userCode
            global lastName

            courseData = mydb.cursor(buffered=True)
            courseData.execute("SELECT * FROM course JOIN enrollment USING(courseID) JOIN user USING(userID) WHERE userID=" + str(userCode))
            items = courseData.fetchall()
            htmlRender = [] 
            piece = []
            count  = 0
            for x in items:
                for i in x:
                    if count == 5 or count == 4:
                        i = str(i)
                        i = i.split(", ")
                    piece.append(i)
                    if count == 1:
                        global courseID
                        courseID=i
                    count += 1

                htmlRender.append(piece)
                piece = []
                count = 0
            
            if request.method == 'POST':
                deletefromEnrollment = mydb.cursor(buffered=True)
                sqlTwo = "DELETE FROM enrollment WHERE courseID='" + request.form.get("course") + "'"

                deletefromEnrollment.execute(sqlTwo)
                deletefrom = mydb.cursor(buffered=True)
                sql = "DELETE FROM course WHERE courseID='" + request.form.get("course") + "'"
                deletefrom.execute(sql)
                mydb.commit()
                return redirect(url_for("professor_panel_index"))
           
            lastName = nameRender[1]
            firstName = nameRender[0]
            userCode = nameRender[2]
            return render_template("professor_dash.html", listy=htmlRender, first=nameRender[0], last=nameRender[1])
          
        else: 
            return redirect(url_for("failure"))
    else:
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING UP A SPECIFIC COURSE PAGE
# PERMISSION LEVEL: PROFESSOR
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/toprofessorcourse/<course>', methods=['GET', 'POST'])
def to_professor_course(course):
    courseID = course
    if session["permission_level"] == "(1)":
        if session["logged_in"] != 'false':
            getSpecificCourseData = mydb.cursor(buffered=True)
            #getSpecificCourseData.execute("SELECT lessonNum, multimediaFile FROM multimedia GROUP BY lessonNum WHERE courseID='" + courseID + "' ORDER BY lessonNum ASC")
            getSpecificCourseData.execute("SELECT courseID, courseName, capacity, courseLoc, courseTimes, firstName, LastName, typeU FROM course JOIN enrollment USING(courseID) JOIN user ON enrollment.userID = user.userID WHERE courseID='"+ courseID + "' ORDER BY typeU ASC;")
            items = getSpecificCourseData.fetchall()
            classinfo = []
            outerList = []
            count = 0
            for x in items:
                for i in x:
                    if count == 4:
                        i = str(i)
                        i = i.split(", ")
                    classinfo.append(i)
                    count += 1
                outerList.append(classinfo)
                classinfo = []
                count = 0
            else:
                return render_template("professor_course.html", courseinfo=outerList)
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# ADDING CONTENT TO A SPECIFIC COURSE
# PERMISSION LEVEL: PROFESSOR
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/addcontenttocourse', methods=['GET', 'POST'])
def professor_add_content_to_course():
    if session["permission_level"] == "(1)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                insertinto = mydb.cursor(buffered=True)
                sql_lesson = "INSERT INTO lesson (courseID, lessonNum, quiz) VALUES (%s, %s, %s)"
                sql_multimedia = "INSERT INTO multimedia (courseID, lessonNum, multimediaFile, fileType) VALUES (%s, %s, %s, %s)"
                try:
                    values_lesson = (courseID, int(request.form["lessonNum"]), "")
                    insertinto.execute(sql_lesson, values_lesson)
                    mydb.commit()
                    
                    insertinto = mydb.cursor(buffered=True)
                    values_multimedia = (courseID, int(request.form["lessonNum"]), request.form["fileName"], 1)
                    insertinto.execute(sql_multimedia, values_multimedia)
                    mydb.commit()
                    return render_template("entries_added_professor.html")
                except mysql.connector.Error as err:
                    return render_template("query_error_professor.html")
            return render_template("add_content_to_course.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files["file"]
        f.save("uploads/"+ f.filename)
    return render_template("entries_added_professor.html")



# +++++++++++++++++++++++++++++++++++++++++++++
# REMOVING CONTENT FROM A SPECIFIC COURSE
# PERMISSION LEVEL: PROFESSOR
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/removecontentfromcourse', methods=['GET', 'POST'])
def professor_remove_content_from_course():
    if session["permission_level"] == "(1)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                removefrom = mydb.cursor(buffered=True)
                sql_multimedia = "REMOVE FROM multimedia WHERE courseID=" + courseID
                removefrom.execute(sql_multimedia)
                mydb.commit()
                return render_template("entries_removed_professor.html")
            else: 
                return redirect(url_for("failure"))
        else: 
            return redirect(url_for("failure"))



# +++++++++++++++++++++++++++++++++++++++++++++
# SETTING THE PROFESSOR FEEDBACK DASH
# PERMISSION LEVEL: PROFESSOR
# +++++++++++++++++++++++++++++++++++++++++++++
@app.route('/professor_dash_ratings', methods=['GET', 'POST'])
def professor_dash_ratings():
    if session["permission_level"] == "(1)":
        if session["logged_in"] != 'false':
            allData = mydb.cursor(buffered=True)
            allData.execute("SELECT firstName, lastName, userID, professorRating, courseRating FROM user JOIN enrollment USING(userID) WHERE courseID='" + courseID + "' AND typeU=2")
            items = allData.fetchall()
            htmlRender = []
            numOfItems = len(items)
            lenX = 5
            for x in items:
                for i in x:
                    htmlRender.append(i)
            return render_template("professor_dash_ratings.html", htmlRender=htmlRender, items=items, x=lenX, first=firstName, last=lastName)
        else:
            return redirect(url_for("failure"))  
    else: 
        return redirect(url_for("failure"))
