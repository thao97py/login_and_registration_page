from flask import Flask, redirect, request, render_template, session, flash, url_for
from mysqlconnection import MySQLConnector
import re
import md5

EMAIL_REGEX= re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = '23ehrfjvuygr789ok'
mysql = MySQLConnector(app,'friendsdb')

@app.route('/')
def index():
    if "logged_id" in session:
        return redirect('/dashboard')
    return render_template('index_login.html')

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    confirm_password = request.form['confirm_password']
    valid = True
# valid name fields
    if (len(first_name)<2):
        flash("First name contains only letters and at least 2 characters")
        valid= False
    
    if (len(last_name)<2):
        flash("Last name contains only letters and at least 2 characters")
        valid= False
   
# validate email             
    if not EMAIL_REGEX.match(email):
        flash("Email is invalid!")
        valid = False
    if len(email)<1:
        flash("Email cannot be blank!")
        valid = False
    query = "SELECT * from login_and_registration WHERE email = :email LIMIT 1"
    email_registerring = mysql.query_db(query, {'email':email})
    if len(email_registerring) >0:
        valid = False
        flash("Email is already registered! ")
# validate password
    if len(request.form['password'])<8:
        flash("password includes at least 8 characters")
        valid = False
    if request.form['password'] != confirm_password:
        flash("password doesn't match")
        valid = False
#decide whether or not user succeeded registerring
    if not valid:
        return redirect('/')   #redirect to index page and render users' errors of registration information on the view
    else:
        flash("You has successfully registered and let's log in!")
        query = "INSERT INTO login_and_registration (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"
        data= {'first_name': first_name, 'last_name': last_name, 'email': email, 'password': password}
        mysql.query_db(query, data)   # save new registration into database
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    valid = True
    user_email = request.form['user_email']
    #validate whether or not the user's email and password are typed with correct form
    if (len(user_email) < 1 or len(request.form['user_password'])< 1) :
        valid = False
        flash('The field can not be blank!')    
    if not valid:
        return redirect('/')  #redirect to index page and render users' errors of loggin information on the view
    else:
        query = "SELECT * from login_and_registration WHERE email = :email LIMIT 1"
        data ={'email':user_email}
        user_data = mysql.query_db(query, data)
        user_password = md5.new(request.form['user_password']).hexdigest()
        if len(user_data)>0:   #check if the user'email is in database, meaning their email has aleardy registered
            user = user_data[0]
            if user['password'] == user_password: #check if their password matches with the one in database
                flash('you has sucessfully logged in!')
                session['logged_id']= user['id']
                return redirect('/dashboard') #redirect to the success page
        flash("Either your password or email is not correct!")
        return redirect('/') #redirect to index page and render users' errors of loggin information on the view

@app.route('/dashboard')
def dashboard():
    query = "SELECT * from login_and_registration where id = :id"
    data = {'id':session['logged_id']}
    logged_user = mysql.query_db(query, data)[0]
    return render_template('/success.html', user = logged_user)

@app.route('/clear')
def clear_session():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)