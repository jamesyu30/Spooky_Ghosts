from flask import Flask, session, render_template, request, redirect
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(32)  #set up the session with a secret key
app.config['s'] = app.secret_key

DB_FILE="accounts.db"            
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()
c.execute("DROP TABLE if exists accounts")
command = f"CREATE TABLE accounts (username TEXT, password TEXT);"
c.execute(command)

STORY_DB_FILE="story.db"            
dbstory = sqlite3.connect(STORY_DB_FILE, check_same_thread=False)
s = dbstory.cursor()
s.execute("DROP TABLE if exists story")
command = f"CREATE TABLE story (title TEXT, story TEXT, edited TEXT);"
s.execute(command)

'''
def to_string(c):
    result = ""
    for i in c:
        string = "".join(i)
        result = result+string
'''   
    
@app.route("/")
def home():
    if not 'username' in session: #checks if session is empty
        return render_template('login.html')
    else:
        return redirect("/auth") #if there is a session, it sends you to /auth

@app.route("/login", methods=['GET', 'POST'])
def login(): #checks if inputs match
    if request.method == "POST":
        c.execute("SELECT * FROM accounts")
        accdata = c.fetchall()
        for data in accdata:
            if(data[0] == request.form['username'] and data[1] == request.form['password']):
                session['username'] = request.form['username'] #if they both match, create a session
                return redirect("/auth", code=307) #code 307 makes the redirect make a post request
        return "Invalid username and/or password"

           
@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route("/create", methods=['GET', 'POST'])
def verify():
    insert = f"INSERT INTO accounts VALUES (\"{request.form['createusername']}\", \"{request.form['createpassword']}\")"
    c.execute(insert)
    db.commit()
    """ PRINTS TABLE
    c.execute("SELECT * FROM accounts")
    rows = c.fetchall() 
    table = ""
    for row in rows:
        row2 = "".join(row)
       # print(row)
        table = table+row2
    #db.close()
    """
    return redirect("/")

@app.route("/auth", methods=['GET', 'POST'])
def auth():
    stitles = s.execute("SELECT title from story;")
    rows = s.fetchall()
    #print(rows) #prints titles
    #parsing titles
    
    return "<h1>Welcome, " + session['username'] +"</h1><br>" + render_template('landing.html')
    #post request makes session['username'] not return an error on refresh

@app.route("/logout")
def logout():
    try:
        session.pop('username') #gets rid of session
    except:
        return redirect("/") 
    return redirect("/")#goes home

@app.route("/story", methods=['GET', 'POST'])
def create():
    return render_template('story.html')

@app.route("/createstory", methods=['GET', 'POST'])
def story():
    try:
        titles = []
        for t in s.execute('SELECT title FROM story'): #turns data into list
            titles.append(t[0])
        #print(titles)
        if not request.form['title'] in titles: #checks for duplicates
            insert = f"INSERT INTO story VALUES (\"{request.form['title']}\", \"{request.form['story']}\", \"{session['username']}\")"
            s.execute(insert)
            dbstory.commit()
            #s.execute("SELECT * FROM story")
            #rows = s.fetchall()
            #print(rows)
        else:
            return "Title is already taken. Try another"
    except:
        return redirect("/")
    return "<h2>Created story!</h2> <br><form action=\"/\"><input type=\"submit\" value=\"Return home\"></form>"

if __name__ == "__main__": 
    app.debug = True
    app.run()    

'''
 s.execute("SELECT edited FROM story")
        e = s.fetchall()
        test=""
        for l in e:
            row2 = "".join(l)
            test = test+" "+row2+" "
        #insert = f"UPDATE story SET edited = '{q}' WHERE title = 123"
        print(test)
        #s.execute(insert)
'''