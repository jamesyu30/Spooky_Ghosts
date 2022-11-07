from flask import Flask, session, render_template, request, redirect
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(32)  #set up the session with a secret key
app.config['s'] = app.secret_key
user = "a"
passw = "1"

DB_FILE="accounts.db"            
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

@app.route("/")
def home():
    #session['username'] = "a"
    if not 'username' in session: #checks if session is empty
        return render_template('login.html')
    else:
        return redirect("/auth") #if there is a session, it sends you to /auth

@app.route("/login", methods=['GET', 'POST'])
def login(): #checks if inputs match
    if request.method == "POST":
        c.execute("SELECT username FROM accounts")
        user1 = c.fetchone()
        print(user1[0])
        if user != request.form['username']: #if username doesn't match
            return "Invalid username"
        if passw != request.form['password']: #if password doesn't match
            return "Invalid password"
        else:
            session['username'] = request.form['username'] #if they both match, create a session
            return redirect("/auth", code=307) #code 307 makes the redirect make a post request

@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route("/create", methods=['GET', 'POST'])
def verify():
    c.execute("DROP TABLE if exists accounts")
    command = f"CREATE TABLE accounts (username TEXT, password TEXT);"          # test SQL stmt in sqlite3 shell, save as string
    c.execute(command) 
    insert = f"INSERT INTO accounts VALUES (\"{request.form['createusername']}\", \"{request.form['createpassword']}\")"
    c.execute(insert)
    db.commit()
    c.execute("SELECT * FROM accounts")
    rows = c.fetchall() #prints table
    table = ""
    for row in rows:
        row2 = "".join(row)
        print(row)
        table = table+row2
    #db.close()
    return table 
"""
@app.route("/auth", methods=['GET', 'POST'])
def auth():
    return "<h1>Welcome, " + session['username'] +"</h1><br>" + render_template('response.html')
    #post request makes session['username'] not return an error on refresh

@app.route("/logout")
def logout():
    session.pop('username') #gets rid of session
    return redirect("/")#goes home
"""
if __name__ == "__main__": 
    app.debug = True 
    app.run()    
