# Pulse
Pulse is a music trivia game that tests a user's knowledge of the music they listen to. 
First, Pulse will access the user's Spotify account. They will then be presented with multiple songs from their Spotify library and will be asked to guess the name of the song as fast as possible by ear.
The user can then view interesting statistics regarding their performance on the 'Game Data' page.

Below is a brief demo with audio:

https://github.com/drs0057/Pulse/assets/118777627/ab495f5d-bd15-4701-bcef-ecd0bb31bee7


# Spotify Authentification
Pulse operates by accessing a user's Spotify account and requesting the appropriate songs. Once a user creates an account with Pulse and navigates to the play tab, they will be redirected to Spotify to give Pulse consent to access their library and play music on their account's behalf:

![Spotify permission page]


# Account Creation and Spotify Authentication
Spotify only allows so many songs to be requested from a user's library at a time. This creates a 10+ second waiting time once an artist's name is submitted. A progress bar serves to show the user the time remaining for the backend to access the entirety of their library from the Spotify servers:

![Progress bar](README_pictures/progressBar.png)


# The Game
Below is a picture of the game in action:

![User is being asked to submit a song guess](README_pictures/songGuess.png)

The user is currently being asked to guess the name of the song as it plays through their speakers. The album cover that contains the song is displayed to aid the user. If the user knows the name of the song, they can input it in the text field and hit 'Submit'. They may optionally hit the 'Skip' button if they cannot remember the song. If the user does not guess the song within 20 seconds, the song is automatically skipped. Keyboard shortcuts are provided on the screen to aid the user in submitting their guesses as fast as possible.



# Song name normalization
Song titles can be complicated. Titles may contain symbols in place of words ($ for S, & for and), names of featured artists, or performance venues/dates in the case of live recordings.
This makes accurately guessing the exact song title very difficult.
Pulse removes this concern to create a more enjoyable playing experience.
Song names are normalized and stripped to only contain the title of the song in its most simple form. Below are some examples of song guesses that Pulse will look for. Note how long, complicated titles are greatly simplified:

![Normalized song names](README_pictures/normalizedNames.png)

These simple song names allow the user to focus more on guessing the actual name of the song, as opposed to worrying about the exact nature of their text input.
