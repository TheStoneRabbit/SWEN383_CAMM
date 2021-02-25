from flask import Flask, render_template, redirect, url_for, request
import time 
# Below is MySQL code once database is created

# import mysql.connector

# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="dbpassword",
#   database="mydatabase"
# )
# mycursor = mydb.cursor()

# End MySQL code

app = Flask(__name__)

# Successful login page
@app.route('/success')
def login_success():
    print("hit")
    return render_template("success.html")

# Login failed page
@app.route('/invalidcredentials')
def failure():
    return render_template("failure.html")

# Login page
@app.route('/login',  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
            return redirect(url_for('failure'))
        else:
            return redirect(url_for('login_success'))
    return render_template("sign_in.html")

# myPLS Start page
# As of right now this just redirects to login
@app.route('/')
def start():
    return redirect(url_for("login"))

