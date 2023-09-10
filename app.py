from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import bcrypt
import api
import json
from random import randint
# from database import db
# from models import Users
# source ~/.bashrc
# source .venv_music/bin/activate
# .venv_music/bin/python app.py

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


def add_token_to_session(code):
    """Adds the access token to the session."""
    if "access_token" in session:
        return
    else:
        access_token, refresh_token = api.request_access_refresh_token(code)
        session["access_token"] = access_token


progress = 0
@app.route('/progress')
def get_progress():
    """Returns progress used to make progress bar."""
    global progress
    return jsonify(progress=progress)


def songs_by_artist(artist, token):
    global progress
    progress = 0
    # Must gather the entire library then sort by the artist
    library_size = api.request_user_library_size(token)
    num_requests, last_limit_size = divmod(library_size, 50)
    progress_chunk = 100 / num_requests
    offset = 0
    songs = []
    for _ in range(num_requests):
        api.request_user_songs(token, offset, 50, songs)
        offset += 50
        progress += progress_chunk
    # Gather remainder of songs
    api.request_user_songs(token, offset, last_limit_size, songs)
    # songs[] contains entire library, now filter by artist
    return [song for song in songs if song["artist"] == artist]


@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        return redirect(api.user_access_url())  # Reroutes to /play
    else:
        if "username" in session:
            if "access_token" in session:
                return redirect(url_for("play"))
            else:
                return render_template("home.html")
        else:
            flash("You must log in first to play.")
            return redirect(url_for("login"))

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
        session.clear()
        flash(f"You have been logged out, {user.name}.", "info")
        return redirect(url_for("login"))
    else:
        flash("You are not logged in.")
        return redirect(url_for("login"))
    

@app.route("/play", methods=["POST", "GET"])
def play():
    code = request.args.get('code', '')
    add_token_to_session(code)
    if request.method == "POST":
        # if 'song-num-field' in request.form:
        #     print(f'Number: {request.form["song-num-field"]}')
        #     # session['song_num'] = request.form['number-field']
        #     # return jsonify(message="Number gathered successfully."), 200
        if 'artist-name-field' in request.form:
            session['artist-name-field'] = request.form['artist-name-field']
            return redirect(url_for("play_artist"))
        if 'shuffleLibrary' in request.form:
            return redirect(url_for("play_library"))
        else:
            flash("An error occurred. Please try again.")
            return redirect(url_for("play"))
    else:
        if "username" in session:
            profile_pic_url, display_name = api.request_user_info(session["access_token"])
            return render_template("play.html", profile_pic_url=profile_pic_url, \
            display_name=display_name)
        else:
            flash("You must log in first to play.")
            return redirect(url_for("login"))


@app.route("/play/artist", methods=["POST", "GET"])
def play_artist():
    if request.method == "POST":
        pass
    else:
        if "username" in session:
            # TOGGLE
            songs = songs_by_artist(session["artist-name-field"], session["access_token"])
            # songs = [{'name': 'The Age of Worry', 'uri': 'spotify:track:1RywwImkBFUEVcRTBmw7vL', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2733c6bbf44de57c6eb51818694'}, {'name': 'Shot in the Dark', 'uri': 'spotify:track:239yM7BAQ2CkNc61ogPGXo', 'image_url': 'https://i.scdn.co/image/ab67616d0000b273779063301154e835a91a35e0'}]
            if songs == []:
                flash(f'You do not have any liked songs by the artist "{session["artist-name-field"]}".')
                session.pop("artist-name-field", None)
                return redirect(url_for("play"))
            else:
                session.pop("artist-name-field", None)
                return render_template("play_artist.html", songs=songs, \
                token=session["access_token"])
        else:
            flash("You must log in first to play.")
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
    

