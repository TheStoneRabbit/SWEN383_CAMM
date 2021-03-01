from flask import Flask, render_template, redirect, url_for, request, session
import time 
import hashlib 
import re
import mysql.connector
from mysql.connector.cursor import MySQLCursor
# Below is MySQL code once database is created


# Enter the password for your MySQL database below
# Username SHOULD be 'root'
MySQL_PASSWORD = "Madison4@"

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=MySQL_PASSWORD,
  database="myPLS"
)
mycursor = mydb.cursor(buffered=True)
# End MySQL code
userID = ""
app = Flask(__name__)
app.secret_key = 'cammgroup'

@app.route('/logout',  methods=['GET', 'POST'])
def logout():
    session['logged_in'] = 'false'
    return redirect(url_for("login"))


# Main admin page
@app.route('/adminpanelindex',  methods=['GET', 'POST'])
def admin_panel_index():
    if session["permission_level"] == "(0)":
        return render_template("index_admin.html")
    else:
        return render_template("failure")

#admin add user page
@app.route('/adminpaneladd',  methods=['GET', 'POST'])
def admin_panel_add():
    if session["permission_level"] == "(0)":
        if request.method == 'POST':
            insertinto = mydb.cursor(buffered=True)
            sql = "INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values (%s, %s, %s, %s, %s, %s)"
            req_pass = str(request.form['password'])
            pass_encode = hashlib.sha256(req_pass.encode())
            values = (request.form["firstname"], request.form["lastname"],int(request.form["userID"]), request.form["email"], pass_encode.hexdigest(), int(request.form["type"]))
            insertinto.execute(sql, values)
            mydb.commit()
            return render_template("entries_added.html")
        return render_template("adminpaneladd.html")
    else: 
        return redirect(url_for("failure"))

#admin remove user page 
@app.route('/adminpanelremove',  methods=['GET', 'POST'])
def admin_panel_remove():
    if session["permission_level"] == "(0)":
        if request.method == 'POST':
            deletefrom = mydb.cursor(buffered=True)
            sql = "delete from user where userID = " + str(int(request.form["username"]))
            values = int(request.form["username"])
            deletefrom.execute(sql)
            mydb.commit()
            return render_template("entries_removed.html")
        return render_template("adminpanelremove.html")
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
    name.execute("select firstName from user where userID = "+ userID)
    firstName = name.fetchall()
    firstName = re.sub("[()]|,|'", "", str(firstName[0])) #Removes extra characters
    if session['logged_in'] != 'false':
        return "<h1 style='text-align:center;'>Welcome " + firstName + "</h1><br>" +render_template('index.html')
    else:
        return redirect(url_for("login"))


# Login page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    mycursor.execute("select userID from user")
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
        for x in rowsUser:
            subbed_one = re.sub("(|)|,|'", "", str(x))
            pos += 1
            if "(" + request.form['username']+ ")" == subbed_one :
                print("User Found: "+ subbed_one)
                global userID
                userID = subbed_one
                cred_pass_one = True
                break
            else:
                cred_pass_one = False
        second_pos = 0
        for y in rowsPass:
            req_pass = str(request.form['password'])
            pass_encode = hashlib.sha256(req_pass.encode())
            subbed_two = re.sub("(|)|,|'", "", str(y))
            second_pos += 1
            # print("("+str(pass_encode.hexdigest()) + ")")
            if "(" + str(pass_encode.hexdigest())+ ")"  ==  subbed_two and second_pos == pos:
                print("Password Hashes Match!")
                cred_pass_two = True
                break
            else: 
                cred_pass_two = False
        #print(str(cred_pass_one) + " " + str(cred_pass_two))
        # If the password is in and the password matches then log in
        if cred_pass_one == True and cred_pass_two == True:
            print("Login Success!") 
            session['logged_in'] = 'true'
            user_type = mydb.cursor(buffered=True)
            user_type.execute("select typeU from user where userID = " + subbed_one)
            permission_level = user_type.fetchall()
            subbed_permission = re.sub("(|)|,|'", "", str(permission_level[0]))
            session["permission_level"] = subbed_permission
            if subbed_permission == "(0)":
                return redirect(url_for("admin_panel_index"))
            return redirect(url_for('login_success'))
        else:
            print("User not Authenticated.  Login Failure")
            return redirect(url_for('failure'))
                
    return render_template("sign_in.html")

# myPLS Start page
# As of right now this just redirects to login
@app.route('/')
def start():
    session['logged_in'] = 'false'
    return redirect(url_for("login"))


