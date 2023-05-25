window.onSpotifyWebPlaybackSDKReady = () => {
    const token = '{{ access_token }}';
    const player = new Spotify.Player({
        name: 'Web Playback SDK Quick Start Player',
        getOAuthToken: cb => { cb(token); },
        volume: 0.5
    });
    
    // ERRORS:
    player.addListener('not_ready', ({ device_id }) => {
        console.log('Device ID has gone offline', device_id);
    });
    player.addListener('initialization_error', ({ message }) => {
        console.error(message);
    });
    player.addListener('authentication_error', ({ message }) => {
        console.error(message);
    });
    player.addListener('account_error', ({ message }) => {
        console.error(message);
    });

    // Ready
    player.addListener('ready', ({ device_id}) => {
        console.log('Ready with Device ID', device_id);
        // playSong(device_id); // Call the function to play a specific song when the player is ready
    });
    
    document.getElementById('togglePlay').onclick = () => {
        player.togglePlay();
    };

    player.connect();
}

function playSong(deviceId) {
    const songUri = 'spotify:track:0tgBtQ0ISnMQOKorrN9HLX';
    const token = '{{ access_token }}';

    // Make a POST request to the Spotify Web API to play the specified song
    fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId}`, {
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ uris: [songUri] })
    })
        .then(response => {
            if (response.status === 204) {
                console.log('Song started playing.');
            } 
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
