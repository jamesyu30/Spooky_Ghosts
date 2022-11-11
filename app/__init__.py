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
    usern = []
    for name in c.execute('SELECT username FROM accounts'): #turns data into list
        usern.append(name[0])
    if not request.form['createusername'] in usern:
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
    else:
        return "Username is already taken <br><form action=\"/\"><input type=\"submit\" value=\"Back\"></form>"
    return redirect("/")

@app.route("/auth", methods=['GET', 'POST'])
def auth():
    display = "<form action=\"/view\" method='POST'>"
    editable = "<form action=\"/edit\" method='POST'>"
    titles = []
    edited = []
    for t in s.execute(f"SELECT title FROM story WHERE edited GLOB \"{session['username']}\""): #turns data into list
        titles.append(t[0])#list of all of the stories
    for e in s.execute(f"SELECT title FROM story WHERE edited NOT GLOB \"{session['username']}\""):
        edited.append(e[0])#list of stories the user hasn't edited
    #print(titles) #prints titles
    #parsing titles
    #print(edited)
    for t in titles:
        display = display + f"<input type=\"radio\" id=\"{t}\" name=\"stories\" value=\"{t}\" required> <label for=\"{t}\">{t}</label>"
    for e in edited:
        editable = editable + f"<input type=\"radio\" id=\"{e}\" name=\"edit\" value=\"{e}\" required> <label for=\"{e}\">{e}</label>"
    #hides the edit/view button to not cause any errors
    if len(display)>35 and len(editable)>35:
        return "<h1>Welcome, " + session['username'] +"</h1><hr><h2>View stories you've contributed to</h2>" \
           + display + "<br><input type=\"submit\" value=\"View\"></form><br>" \
           + "<h2>Edit a story</h2>" + editable + \
           "<br><input type=\"submit\" value=\"Edit\"></form><br>"+render_template('landing.html')
    elif len(display)>35:
        return "<h1>Welcome, " + session['username'] +"</h1><hr><h2>View stories you've contributed to</h2>" \
           + display + "<br><input type=\"submit\" value=\"View\"></form><br>" \
           + "<h2>Edit a story</h2>"+render_template('landing.html')
    elif len(editable)>35:
        return "<h1>Welcome, " + session['username'] +"</h1><hr><h2>View stories you've contributed to</h2>" \
           + "<h2>Edit a story</h2>" + editable + \
           "<br><input type=\"submit\" value=\"Edit\"></form><br>"+render_template('landing.html')
    else:
        return "<h1>Welcome, " + session['username'] +"</h1><hr><br><h2>View stories you've contributed to</h2>" + "<br><h2>Edit a story</h2>" + render_template('landing.html')
    #post request makes session['username'] not return an error on refresh

@app.route("/logout")
def logout():
    try:
        session.pop('username') #gets rid of session
    except:
        return redirect("/")
    #db.close()
    #dbstory.close()
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

@app.route("/view", methods=['GET', 'POST'])
def view():
    com = f"SELECT * FROM story WHERE title = \"{request.form['stories']}\""
    s.execute(com)
    #s.execute('SELECT * FROM story')
    title = ""
    story = ""
    for data in s.fetchall():
        title = data[0]
        story = data[1]
    return f"<h1>{title}</h1><hr>{story}<br><br><form action=\"/auth\" method='POST'>"\
           +"<input type=\"submit\" value=\"Back\"></form>"

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    return "<h1 contenteditable=\"true\">test</h1>"

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