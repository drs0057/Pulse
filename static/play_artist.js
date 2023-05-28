var uri = "";
function chooseSong(songs) {
  length = songs.length;
  randomIndex = Math.floor(Math.random() * length);
  uri = songs[randomIndex].uri;
}
window.onload = () => {
  chooseSong(songs);
};
window.onSpotifyWebPlaybackSDKReady = () => {
  const token = "{{ token }}";
  const player = new Spotify.Player({
    name: "Web Playback SDK Quick Start Player",
    getOAuthToken: (cb) => {
      cb(token);
    },
    volume: 0.5,
  });

  // ERRORS:
  player.addListener("not_ready", ({ device_id }) => {
    console.log("Device ID has gone offline", device_id);
  });
  player.addListener("initialization_error", ({ message }) => {
    console.error(message);
  });
  player.addListener("authentication_error", ({ message }) => {
    console.error(message);
  });
  player.addListener("account_error", ({ message }) => {
    console.error(message);
  });
  // Ready
  player.addListener("ready", ({ device_id }) => {
    console.log("Ready with Device ID", device_id);
    playSong(device_id, uri);
  });
  document.getElementById("togglePlay").onclick = () => {
    player.togglePlay();
  };
  player.connect();
};

function playSong(deviceId, uri) {
  const songUri = uri;
  const token = "{{ token }}";
  fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
    method: "PUT",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ uris: [songUri] }),
  });
}
