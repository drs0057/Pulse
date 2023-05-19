from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import bcrypt
# from database import db
# from models import Users


app = Flask(__name__)
app.secret_key = "Tigers-315700"
app.permanent_session_lifetime = timedelta(days=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Tigers-315700@localhost/music'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    username = db.Column(db.String(255))
    hash_pw = db.Column(db.String(255))

    def __init__(self, name, username, hash_pw):
        self.name = name
        self.username = username
        self.hash_pw = hash_pw

def duplicate_username(username):
    """Determines if a username already exists in the db."""
    users = Users.query.all()
    for user in users:
        if user.username == username:
            return True
    return False

def find_user(username):
    """Returns the corresponding user object from the db."""
    users = Users.query.all()
    for user in users:
        if user.username == username:
            return user
    return None

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    found_user = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        found_user = find_user(username)
        if found_user:
            # Check password against hash
            password_bytes = password.encode('utf-8')
            hash_bytes = found_user.hash_pw.encode('utf-8')
            is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
            if is_valid:
                session.permanent = True
                session["username"] = username
                flash("Login successful.")
                return redirect(url_for("home"))
            else:
                flash("Incorrect password.")
                return redirect(url_for("login"))
        else:
            flash("Incorrect username or password.")
            return redirect(url_for("login"))
        
    if request.method == "GET":
        if "username" in session:
            flash("Already logged in.")
            return redirect(url_for("home"))
        else:
            return render_template("login.html")
    
@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "username" in session:
        username = session["username"]
        user = find_user(username)
        session.pop("username", None)
        flash(f"You have been logged out, {user.name}.", "info")
        return redirect(url_for("login"))
    else:
        flash("You are not logged in.")
        return redirect(url_for("login"))

@app.route("/account", methods=["POST", "GET"])
def account():
    if "username" in session:
        user = find_user(session["username"])
        return render_template("account.html", user=user)
    else:
        flash("You must log in to view account information.")
        return redirect(url_for("login"))
    
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        if name == "" or username == "" or password == "":
            flash("You must fill out all fields.")
            return redirect(url_for("register"))
        elif duplicate_username(username):
            flash("This user already exists.")
            return redirect(url_for("register"))
        else:
            # Hash and salt password
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hash_pw = bcrypt.hashpw(password_bytes, salt)
            user = Users(name, username, hash_pw)
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created.")
            return redirect(url_for("home"))
    else:
        return render_template("register.html")
    
@app.route("/game_data")
def game_data():
    if "username" in session:
        user = find_user(session["username"])
        return render_template("game_data.html", user=user)
    else:
        flash("You must login before viewing game data.")
        return redirect(url_for("login"))
    
@app.route("/view_users")
def view_users():
    return render_template("view_users.html", users=Users.query.all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=8000, debug=True)
    

