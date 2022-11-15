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
command = "CREATE TABLE accounts (username TEXT, password TEXT);"
c.execute(command)

STORY_DB_FILE="story.db"            
dbstory = sqlite3.connect(STORY_DB_FILE, check_same_thread=False)
s = dbstory.cursor()
s.execute("DROP TABLE if exists story")
command = "CREATE TABLE story (title TEXT, story TEXT, edited TEXT, newestedit TEXT);"
s.execute(command)

#DEMO ACCOUNT
#username: demo
#password: 123

storytitle=""
    
@app.route("/")
def home():
    if not 'username' in session: #checks if session is empty
        return render_template('login.html')
    else:
        return redirect("/auth") #if there is a session, it sends you to /auth

@app.route("/login", methods=['GET', 'POST'])
def login(): #checks if inputs match
    try:
        c.execute("INSERT INTO accounts VALUES(?,?)", ["demo","123"])
        if request.method == "POST":
            c.execute("SELECT * FROM accounts")
            accdata = c.fetchall()
            for data in accdata:
                if(data[0] == request.form['username'] and data[1] == request.form['password']):
                    session['username'] = request.form['username'] #if they both match, create a session
                    return redirect("/auth", code=307) #code 307 makes the redirect make a post request
        return "Invalid username and/or password"
    except:
        return redirect("/")

           
@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route("/create", methods=['GET', 'POST'])
def verify():
    try:
        usern = []#list of all existing usernames
        for name in c.execute('SELECT username FROM accounts'): #turns data into list
            usern.append(name[0])
        if not request.form['createusername'] in usern and not " " in request.form['createusername']:
            #insert = f"INSERT INTO accounts VALUES (\"{request.form['createusername']}\", \"{request.form['createpassword']}\")"
            #print(request.form['createusername'], request.form['createpassword'])
            data = [request.form['createusername'], request.form['createpassword']]
            #? is a placeholder for information in a list of data, make sure data is a list, make sure columns match
            c.execute("INSERT INTO accounts VALUES(?,?)", data)
            db.commit()
        elif " " in request.form['createusername']:
            return "Username can't have any spaces"
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
    except:
        return redirect("/")
    return redirect("/")

@app.route("/auth", methods=['GET', 'POST'])
def auth():
    try:
        display = "<form action=\"/view\" method='POST'>"
        editable = "<form action=\"/edit\" method='POST'>"
        titles = []
        edited = []
        s.execute("SELECT title FROM story")
        #print(s.fetchall())
        #for f in s.fetchall():
        #    print("".join(f))
        for t in s.fetchall(): #parse every title
            #print(t)
            t2 = "".join(t) #tostring of t(titles)
            #print(t2)
            #titles.append(t[0])#list of all of the stories
            for i in s.execute("SELECT edited FROM story WHERE title = (?)", [t2]): # select people who have edited of every story
                #print(i)
                i2 ="".join(i)
                if session['username'] in i2:
                    titles.append(t2)
                else:
                    edited.append(t2)
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
    except:
        return redirect("/")

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
            s.execute("INSERT INTO story VALUES(?,?,?,?)", [request.form['title'], request.form['story'], session['username']+" ", request.form['story']])
            dbstory.commit()
            #s.execute("SELECT * FROM story")
            #rows = s.fetchall()
            #print(rows)
        else:
            return "Title is already taken. Try another"
        return "<h2>Created story!</h2> <br><form action=\"/\"><input type=\"submit\" value=\"Return home\"></form>"
    except:
        return redirect("/")

@app.route("/view", methods=['GET', 'POST'])
def view():
    try:
        s.execute("SELECT * FROM story WHERE title = (?)", [request.form['stories']])
        #s.execute('SELECT * FROM story')
        title = ""
        story = ""
        for data in s.fetchall():
            title = data[0]
            story = data[1]
    except:
        return redirect("/")
    return f"<h1>{title}</h1><hr>{story}<br><br><form action=\"/auth\" method='POST'>"\
           +"<input type=\"submit\" value=\"Back\"></form>"

@app.route("/edit", methods=['GET', 'POST'])
def edit():
    try:
        s.execute("SELECT * FROM story WHERE title = (?)", [request.form['edit']])
        title = ""
        story = ""
        for data in s.fetchall():
            title = data[0]
            story = data[3]
            session['title'] = title
            session['story'] = data[1]
    except:
        return redirect("/")
    return render_template('edit.html', t=title, s=story)

@app.route("/add", methods=['GET', 'POST'])
def add():
    try:
        #print(session['title'])
        s.execute("SELECT edited FROM story WHERE title = (?)", [session['title']])
        edited = s.fetchall()
        name = ""
        for user in edited:
            name = name+"".join(user)
        s.execute("UPDATE story SET story = (?), newestedit = (?) , edited = (?) WHERE title = (?)", [session['story'] + request.form['edits'], request.form['edits'], name + session['username']+" ",session['title']])
        session.pop('story')
        session.pop('title')
    except:
        return redirect("/")
    return redirect("/")

if __name__ == "__main__": 
    app.debug = True
    app.run()    
