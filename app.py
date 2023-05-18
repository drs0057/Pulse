from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
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
    password = db.Column(db.String(255))

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = Users.query.all()
        for user in users:
            if user.username == username and user.password == password:
                found_user = user
        if found_user:
            session.permanent = True
            session["username"] = username
            flash("Login successful.")
            return redirect(url_for("home"))
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
        flash(f"You have been logged out, {username}", "info")
        session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/account", methods=["POST", "GET"])
def account():
    if "username" in session:
        username = session["username"]
        return render_template("account.html", username=username)
    else:
        flash("You are not logged in.")
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
        else:
            user = Users(name, username, password)
            db.session.add(user)
            db.session.commit()
            flash("Your account has been created.")
            return redirect(url_for("home"))
    else:
        flash("Music Trivia the Game requires a connection to your Spotify account. Please enter your Spotify login and password below:")
        return render_template("register.html")
    
@app.route("/game_data")
def game_data():
    if "username" in session:
        username = session["username"]
        return render_template("game_data.html", username=username)
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