from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Column, Integer, ForeignKey, Boolean
db = SQLAlchemy()


class Users(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)


class Artists(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    artist_name = Column(String(255), nullable=False)


class Albums(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    album_name = Column(String(255), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)


class Games(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Songs(db.Model):
    spotify_id = Column(String(255), primary_key=True, nullable=False)
    song_name = Column(String(255), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)


class Guesses(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    time_to_guess = Column(Integer)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    spotify_id = Column(String(255), ForeignKey("songs.spotify_id"), nullable=False)





