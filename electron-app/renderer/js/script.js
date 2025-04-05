const videoInput = document.querySelector('#video');
const videoUploadSection = document.querySelector('#video-upload-section');
const videoSection = document.querySelector('#video-section');
const videoPlayer = document.querySelector('#video-player');
const team1Btn = document.querySelector('#team1');
const team2Btn = document.querySelector('#team2');
const playerInfoBody = document.querySelector('#player-info-body');
const cancelButton = document.querySelector('#cancel-button');
const loadingIndicator = document.createElement('div');

// Setup loading indicator
loadingIndicator.className = 'loading';
loadingIndicator.innerHTML = '<div class="spinner"></div><p>Processing video...</p>';
loadingIndicator.style.display = 'none';
document.body.appendChild(loadingIndicator);

videoInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    
    if (file && file.type.startsWith('video/')) {
        try {
            // Show loading indicator
            loadingIndicator.style.display = 'flex';
            videoUploadSection.style.display = 'none';
            
            const formData = new FormData();
            formData.append('video', file);
            
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Set the processed video source
            videoPlayer.src = data.processed_video_url;
            
            // Hide loading indicator and show video section
            loadingIndicator.style.display = 'none';
            videoSection.classList.remove('hidden');
            
            // Fetch player data (you'll need to implement this endpoint)
            const playerResponse = await fetch('http://localhost:5000/player-data');
            const playerData = await playerResponse.json();
            
            // Store player data for team selection
            window.playerData = playerData;
            
        } catch (error) {
            console.error("Error:", error);
            alert(`Error processing video: ${error.message}`);
            loadingIndicator.style.display = 'none';
            videoUploadSection.style.display = 'flex';
        }
    } else {
        alert('Please select a valid video file.');
    }
});

// Handle team selection
team1Btn.addEventListener('click', () => {
    displayPlayerInfo('team1');
});

team2Btn.addEventListener('click', () => {
    displayPlayerInfo('team2');
});

function displayPlayerInfo(team) {
    if (!window.playerData || !window.playerData[team]) {
        console.error('Player data not available');
        return;
    }
    
    const players = window.playerData[team];
    playerInfoBody.innerHTML = '';
    
    players.forEach(player => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-4 py-2">${player.player}</td>
            <td class="px-4 py-2">${player.speed} km/h</td>
            <td class="px-4 py-2">${player.headAngle}°</td>
            <td class="px-4 py-2">${player.backAngle}°</td>
            <td class="px-4 py-2">
                <div class="fatigue-bar" style="width: ${player.fatigueLevel}%;"></div>
                ${player.fatigueLevel}%
            </td>
        `;
        playerInfoBody.appendChild(row);
    });
}

cancelButton.addEventListener('click', () => {
    videoPlayer.src = '';
    videoPlayer.pause();
    videoUploadSection.classList.remove('hidden');
    videoSection.classList.add('hidden');
    videoInput.value = '';
    window.playerData = null;
});