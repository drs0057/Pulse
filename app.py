from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from models import db, Users, Games, Guesses, Artists, Albums, Songs
import bcrypt
import api
import json
from random import shuffle
from config import Config

# Configure
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
testing = True


def add_gamedata_to_DB(gameData):
    """Adds all game data from a recently finished session to the database."""
    print(gameData)
    user = db.session.query(Users).filter(Users.username == session['username'])
    new_game = Games(user_id=user.id)
    db.session.add(new_game)

    for guess in gameData['guesses']:
        # Log each guess
        new_guess = Guesses(
                    game_id=new_game.id, song_uri=guess['song_uri'],
                    time_to_guess=guess['time_to_guess'])
        db.session.add(new_guess)

        # Log the artist, album, and song associated with each guess
        # TODO: Gather artist, album for each song and create entries in each table
        artist = Artists(artist_name=artistName)
        album = Albums()
    
    db.session.commit()


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
    access_token, refresh_token = api.request_access_refresh_token(code)
    session["access_token"] = access_token


progress = 0
@app.route('/progress')
def get_progress():
    """Returns progress used to make progress bar."""
    global progress
    return jsonify(progress=progress)


def songs_by_artist(artist, token):
    """ Must gather the entire library then sort by the artist. """
    global progress
    progress = 0
    library_size = api.request_user_library_size(token)
    num_requests, last_limit_size = divmod(library_size, 50)
    progress_chunk = 100 / num_requests
    offset = 0
    songs = []
    for _ in range(num_requests):
        api.request_user_songs(token, offset, 50, songs)
        offset += 50
        progress += progress_chunk
    if last_limit_size:     #  Gather remainder of songs
        api.request_user_songs(token, offset, last_limit_size, songs)
    return [song for song in songs if song["artist"].lower() == artist.lower().strip()]


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
            hash_bytes = found_user.password_hash.encode('utf-8')
            is_valid = bcrypt.checkpw(password_bytes, hash_bytes)
            if not is_valid:
                flash("Incorrect password.")
                return redirect(url_for("login"))
            
            session.permanent = True
            session["username"] = username
            flash("Login successful.")
            return redirect(url_for("home"))  
        else:
            flash("Incorrect username or password.")
            return redirect(url_for("login"))
        
    if request.method == "GET":
        if "username" not in session:
            return render_template("login.html")
        flash("Already logged in.")
        return redirect(url_for("home"))
            

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "username" not in session:
        flash("You are not logged in.")
        return redirect(url_for("login"))
    
    username = session["username"]
    user = find_user(username)
    session.clear()
    flash(f"You have been logged out, {user.name}.", "info")
    return redirect(url_for("login"))
    

@app.route("/play", methods=["POST", "GET"])
def play():
    code = request.args.get('code', '')
    add_token_to_session(code)

    if request.method == "POST":
        if 'artist-name-field' not in request.form:
            flash("An error occurred. Please try again.")
            return redirect(url_for("play"))
        session['songNum'] = request.form['song-num-field']
        session['artistName'] = request.form['artist-name-field']
        return redirect(url_for("play_artist"))
    else:
        if "username" not in session:
            flash("You must log in first to play.")
            return redirect(url_for("login"))

        profile_pic_url, display_name = api.request_user_info(session["access_token"])
        return render_template("play.html", profile_pic_url=profile_pic_url, \
        display_name=display_name)
            

@app.route("/play/artist", methods=["POST", "GET"])
def play_artist():
    if request.method == "POST":  # Game was finished
        gameData = request.json
        add_gamedata_to_DB(gameData)
        flash(f"You recognized {gameData['correctGuesses']} out of {gameData['totalSongs']} songs!")
        return jsonify({'redirectURL': url_for('play')})
    else:
        if "username" not in session:
            flash("You must log in first to play.")
            return redirect(url_for("login"))

        # TOGGLE SONGS FOR TESTING
        songs = songs_by_artist(session["artistName"], session["access_token"]) if not testing else [{'name': 'Daughters - Home Demo', 'artist': 'John Mayer', 'uri': 'spotify:track:0q39nyBjL54ghLeDNNEWz0', 'image_url': 'https://i.scdn.co/image/ab67616d0000b273e4a9075cc5c6b947aedc100d'}, {'name': 'Assassin', 'artist': 'John Mayer', 'uri': 'spotify:track:6OXt9aSIr4DSxSR3Qjrtgp', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2731e3dbe4453ed61633c472fbe'}, {'name': 'Stop This Train', 'artist': 'John Mayer', 'uri': 'spotify:track:3E6iea9uEmB7gRru4lyP6h', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2737af5fdc5ef048a68db62b85f'}, {'name': 'Who Did You Think I Was - Live at the House of Blues, Chicago, Illinois, September 22, 2005', 'artist': 'John Mayer', 'uri': 'spotify:track:00gvX9sFwh19OH88f4v4jW', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2732c044b0dec365f990af906ad'}, {'name': 'Helpless', 'artist': 'John Mayer', 'uri': 'spotify:track:701DK0It9f7iurRnzKvF0y', 'image_url': 'https://i.scdn.co/image/ab67616d0000b273c6bfaf942ed981d5c4c922e4'}, {'name': 'Friends, Lovers or Nothing', 'artist': 'John Mayer', 'uri': 'spotify:track:1wkaoS4jTVXYMUWHKVFZTk', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2731e3dbe4453ed61633c472fbe'}, {'name': 'Last Train Home - Ballad Version', 'artist': 'John Mayer', 'uri': 'spotify:track:60CQpHremwdzRXIzoaufDF', 'image_url': 'https://i.scdn.co/image/ab67616d0000b273a58988c792a68f20d204a4ad'}, {'name': 'Dear Marie', 'artist': 'John Mayer', 'uri': 'spotify:track:5Aq5TIy9jVK70aL7xcE9oa', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2738e3ab1cbd76d15dc64450a13'}, {'name': 'Heartbreak Warfare', 'artist': 'John Mayer', 'uri': 'spotify:track:4gs07VlJST4bdxGbBsXVue', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2731e3dbe4453ed61633c472fbe'}, {'name': 'Good Love Is On the Way - Live at the Nokia Theatre, Los Angeles, CA - December 2007', 'artist': 'John Mayer', 'uri': 'spotify:track:6V3Sd5FVnf83LLA6VMP15F', 'image_url': 'https://i.scdn.co/image/ab67616d0000b2735b9c332f9f76cabc137e400f'}]        
        if not songs:
            flash(f'You do not have any liked songs by the artist "{session["artistName"]}".')
            session.pop("artistName", None)
            return redirect(url_for("play"))

        songNum = int(session['songNum'])
        if len(songs) < songNum: 
            flash(f"You only have {len(songs)} songs by {session['artistName']}.")
        shuffle(songs)
        songs = songs[:songNum]
        session.pop("songNum", None)
        session.pop("artistName", None)
        return render_template("play_artist.html", songs=songs, \
        token=session["access_token"])
        

@app.route("/account", methods=["POST", "GET"])
def account():
    if "username" not in session:
        flash("You must log in to view account information.")
        return redirect(url_for("login"))
    
    user = find_user(session["username"])
    return render_template("account.html", user=user)
        

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

        # Hash and salt password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        user = Users(name=name, username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created.")
        return redirect(url_for("home"))
    else:
        return render_template("register.html")
    

@app.route("/game_data")
def game_data():
    if "username" not in session:
        flash("You must login before viewing game data.")
        return redirect(url_for("login"))
    
    user = find_user(session["username"])
    return render_template("game_data.html", user=user)
        
    
@app.route("/view_users")
def view_users():
    return render_template("view_users.html", users=Users.query.all())


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=8000, debug=True)
    

