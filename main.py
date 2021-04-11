from flask import Flask, render_template, redirect, url_for, request, session
import time 
import hashlib 
import getpass
import re
import mysql.connector
from mysql.connector.cursor import MySQLCursor
from flask_table import Table, Col
# Below is MySQL code once database is created


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

# Logs a user out
@app.route('/logout',  methods=['GET', 'POST'])
def logout():
    session['logged_in'] = 'false'
    return redirect(url_for("login"))

# Main admin page. Checks if user is admin and returns admin page, 
# otherwise returns failure page
@app.route('/adminpanelindex',  methods=['GET', 'POST'])
def admin_panel_index():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            courseData = mydb.cursor(buffered=True)
            courseData.execute("select * from course")
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
            userName.execute("select firstName, lastName from user where email='"+ email+ "'")
            names = userName.fetchall()
            nameRender = []
            for x in names:
                for i in x:
                    nameRender.append(i)
            global firstName
            
            global lastName
            
            if request.method == 'POST':
                deletefromEnrollment = mydb.cursor(buffered=True)
                sqlTwo = "delete from enrollment where courseID='" + request.form.get("course") + "'"
                
                deletefromEnrollment.execute(sqlTwo)
                deletefrom = mydb.cursor(buffered=True)
                sql = "delete from course where courseID='" + request.form.get("course") + "'"
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

#admin add user page. Checks permission of user and returns admin add page if admin,
# otherwise returns failure page
@app.route('/adminpaneladd',  methods=['GET', 'POST'])
def admin_panel_add():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                insertinto = mydb.cursor(buffered=True)
                sql = "INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values (%s, %s, %s, %s, %s, %s)"
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

#admin remove user page 
@app.route('/adminpanelremove',  methods=['GET', 'POST'])
def admin_panel_remove():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                deletefromStudentGroups = mydb.cursor(buffered=True)
                sql = "delete from studentGroups where userID = " + str(int(request.form["username"]))
                # values = int(request.form["username"])
                deletefromStudentGroups.execute(sql)
                deletefromEnrollment = mydb.cursor(buffered=True)
                sqlThree = "delete from enrollment where userID = " + str(int(request.form["username"]))
                deletefromEnrollment.execute(sqlThree)
                deletefromUser = mydb.cursor(buffered=True)
                sqlTwo = "delete from user where userID = " + str(int(request.form["username"]))
                deletefromUser.execute(sqlTwo)
                mydb.commit()
                return render_template("entries_removed.html")
            return render_template("adminpanelremove.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))

# Successful login page
# this redirects to the homepage
# Do login tasks here
@app.route('/success')
def login_success():
    if session['logged_in'] != 'false':
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

# Login failed page
@app.route('/invalidcredentials')
def failure():
    session['logged_in'] = 'false'
    return render_template("failure.html")
    
# Home Page
@app.route('/home',  methods=['GET', 'POST'])
def home():
    name = mydb.cursor(buffered=True)
    #print(userID)
    name.execute("select firstName from user where email = "+ "'" + userID + "'")
    firstName = name.fetchall()
    #print(firstName)
    firstName = re.sub("[()]|,|'", "", str(userID)) #Removes extra characters
    if session['logged_in'] != 'false':
        return "<h1 style='text-align:center;'>Welcome " + firstName + "</h1><br>" +render_template('index.html')
    else:
        return redirect(url_for("login"))

# Login page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    mycursor.execute("select email from user")
    numRows = mycursor.rowcount

    bad_chars = ["(", ")", ",", "\'"]
    if request.method == 'POST':
        rowsUser = mycursor.fetchall()
        # mycursor.close()
        newCursor = mydb.cursor(buffered=True)
        newCursor.execute("select hashPassword from user")
        rowsPass = newCursor.fetchall()
        cred_pass_one = False
        cred_pass_two = False
        # newCursor.close()
        # These for loops test if username and password is in db.
        pos = 0
        subbed_one = ""
     #   print(rowsUser)
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
            user_type.execute("select typeU from user where email=" + "'" +subbed_one + "'")
            permission_level = user_type.fetchall()
            #print(permission_level)
            subbed_permission = re.sub("(|)|,|'", "", str(permission_level[0]))
            #print(subbed_permission)
            session["permission_level"] = subbed_permission
            if session["permission_level"] == "(0)":
                return redirect(url_for("admin_panel_index"))
            return redirect(url_for('login_success'))
        else:
            return redirect(url_for('failure'))
                
    return render_template("sign_in.html")

    # View Format for user table 

@app.route('/admin_user_dash', methods=['GET', 'POST'])
def admin_user_dash():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            allData = mydb.cursor(buffered=True)
            allData.execute("select firstName, lastName, userID, email from user WHERE typeU=0")
            items = allData.fetchall()
            htmlRender = []
            numOfItems = len(items)
            lenX = 4
            for x in items:
                for i in x:
                    htmlRender.append(i)
            allData.execute("select firstName, lastName, userID, email from user WHERE typeU=1")
            items1 = allData.fetchall()
            numOfItems1 = len(items1)
            lenX1 = 4
            for x1 in items1:
                for i1 in x1:
                    htmlRender.append(i1)
            allData.execute("select firstName, lastName, userID, email from user WHERE typeU=2")
            items2 = allData.fetchall()
            numOfItems2 = len(items1)
            lenX2 = 4
            for x2 in items2:
                for i2 in x2:
                    htmlRender.append(i2)
            allData.execute("select firstName, lastName from user where email='"+ email+ "'")
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


# Navigating to A Course Page
@app.route('/tocourse/<course>', methods=['GET', 'POST'])
def to_course(course):
    global courseID
    courseID = course
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            getSpecificCourseData = mydb.cursor(buffered=True)
            getSpecificCourseData.execute("select courseID, courseName, capacity, courseLoc, courseTimes, firstName, LastName, typeU from course join enrollment using(courseID) join user on enrollment.userID = user.userID where courseID='"+ course+ "' order by typeU asc;")
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


# for the group page
@app.route("/admin_dash_group")
def admin_group_dash():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            groupData = mydb.cursor(buffered=True)
            sql = "select studentGroups.groupID, group_concat(studentGroups.userID) as 'Users in Group', title, group_description from user_group  join studentGroups on studentGroups.groupID = user_group.groupID join user on studentGroups.userID = user.userID where user.userID = studentGroups.userID group by user_group.groupID"
            groupData.execute(sql)
            items = groupData.fetchall()
            htmlRender = []
            numOfItems = len(items)
            piece = []
            existing_groups = []
            count = 0
            appendItems = False
            mySplit = False
            out = [k for t in items for k in t]
            j = []
            k = [out[i:i + 4] for i in range(0, len(out), 4)]
            htmlRender = k

                
# l = ['a',' b',' c',' d',' e']
# c_index = l.index("c")
# l2 = l[:c_index]
                # if count == 0:
                #     j = str(x).replace("'", "").split(", ")
                #     mySplit = True 
                #     count += 1
                #     htmlRender.append(j)
            
                
            return render_template("admin_dash_group.html", userGroupData=htmlRender, items=items, last=lastName, first=firstName)
        else: 
            return redirect(url_for("failure"))
    else:
        return redirect(url_for("failure"))
    

@app.route('/addcourse',  methods=['GET', 'POST'])
def admin_course():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            if request.method == 'POST':
                insertinto = mydb.cursor(buffered=True)
                sql = "INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) values (%s, %s, %s, %s, %s)"
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


# myPLS Start page
# As of right now this just redirects to login
@app.route('/')
def start():
    session['logged_in'] = 'false'
    return redirect(url_for("login"))

#admin remove course 
@app.route('/removecourse',  methods=['GET', 'POST'])
def remove_course():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            
            return render_template("entries_removed.html")
        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))


# Group page
@app.route('/group',  methods=['GET', 'POST'])
def add_group():
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            groupData = mydb.cursor(buffered=True)
            groupData.execute("select * from user_group")
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
            userName.execute("select firstName, lastName from user where email='" + email + "'")
            names = userName.fetchall()
            nameRender = []
            for x in names:
                for i in x:
                    nameRender.append(i)
            global firstName
            
            global lastName
            
            if request.method == 'POST':
                deletefrom = mydb.cursor(buffered=True)
                sql = "INSERT INTO studentGroups (userID, groupID, userPost) values (%s, %s, %s)"
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

# Navigating to A group Page
@app.route('/togroup/<group>', methods=['GET', 'POST'])
def to_group(group):
    global groupID
    groupID = group
    if session["permission_level"] == "(0)":
        if session["logged_in"] != 'false':
            getSpecificGroupData = mydb.cursor(buffered=True)
            getSpecificGroupData.execute("select groupID, title, group_description from user_group join studentGroups using(groupID) join user on studentGroups.userID = user.userID where groupID='"+ group+ "' order by typeU asc;")
            items = getSpecificGroupData.fetchall()
            groupInfo = []
            outerList = []
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
            if outerList == []:
                return redirect(url_for("failure"))
            else:    
                
                # lets see
                if request.method == 'POST':
                    print(request.form["makePostInput"])
                    deletefrom = mydb.cursor(buffered=True)
                    sql = "INSERT INTO studentGroups (userID, groupID, post) values (%s, %s, %s)"
                    try:
                        insertinto = mydb.cursor(buffered=True)
                        values = (5876, groupID, request.form["makePostInput"])
                        insertinto.execute(sql, values)
                        mydb.commit()
                        return render_template("entries_added.html")
                    except:
                        return render_template("query_error.html")
                    return redirect(url_for("group"))

                return render_template("group.html", groupInfo=outerList)

        else: 
            return redirect(url_for("failure"))
    else: 
        return redirect(url_for("failure"))
