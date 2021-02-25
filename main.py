from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

@app.route('/success')
def login_success():
    print("hit")
    return render_template("success.html")


@app.route('/',  methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
            return error
        else:
            return redirect(url_for('login_success'))
    return render_template("index.html")


