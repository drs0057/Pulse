from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Column, Integer, ForeignKey, Boolean
db = SQLAlchemy()


class Users(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)


class Games(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Guesses(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    time_to_guess = Column(Integer, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)


class Artists(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    artist_name = Column(String(255), nullable=False)


class Albums(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    album_name = Column(String(255), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)


class Songs(db.Model):
    id = Column(Integer, primary_key=True, nullable=False)
    song_name = Column(String(255), nullable=False)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)






