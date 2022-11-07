from flask import Flask, session, render_template, request, redirect
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)  #set up the session with a secret key
app.config['s'] = app.secret_key
user = "a"
passw = "1"

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
        if user != request.form['username']: #if username doesn't match
            return "Username is wrong"
        if passw != request.form['password']: #if password doesn't match
            return "Password is wrong"
        else:
            session['username'] = request.form['username'] #if they both match, create a session
            return redirect("/auth", code=307) #code 307 makes the redirect make a post request

@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template()

@app.route("/register2", methods=['GET', 'POST'])


@app.route("/auth", methods=['GET', 'POST'])
def auth():
    return "<h1>Welcome, " + session['username'] +"</h1><br>" + render_template('response.html')
    #post request makes session['username'] not return an error on refresh

@app.route("/logout")
def logout():
    session.pop('username') #gets rid of session
    return redirect("/")#goes home

if __name__ == "__main__": 
    app.debug = True 
    app.run()    
