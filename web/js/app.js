// API base URL
const API_BASE = '';

// Global state
let channels = [];
let currentChannelId = null;
let playlistItemCounter = 0;

// DOM elements
const channelList = document.getElementById('channelList');
const channelModal = document.getElementById('channelModal');
const channelForm = document.getElementById('channelForm');
const addChannelBtn = document.getElementById('addChannelBtn');
const cancelBtn = document.getElementById('cancelBtn');
const closeBtn = document.querySelector('.close');
const addPlaylistItemBtn = document.getElementById('addPlaylistItemBtn');
const playlistItemsContainer = document.getElementById('playlistItems');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadChannels();
    setupEventListeners();
});

function setupEventListeners() {
    addChannelBtn.addEventListener('click', () => openModal());
    cancelBtn.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);
    channelForm.addEventListener('submit', handleSubmit);
    addPlaylistItemBtn.addEventListener('click', addPlaylistItem);

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === channelModal) {
            closeModal();
        }
    });
}

async function loadChannels() {
    try {
        const response = await fetch(`${API_BASE}/api/channels`);
        channels = await response.json();
        renderChannels();
    } catch (error) {
        console.error('Error loading channels:', error);
        channelList.innerHTML = '<p class="loading">Error loading channels</p>';
    }
}

function renderChannels() {
    if (channels.length === 0) {
        channelList.innerHTML = '<p class="loading">No channels yet. Click "Add Channel" to create one.</p>';
        return;
    }

    channelList.innerHTML = channels.map(channel => `
        <div class="channel-card">
            <div class="channel-header">
                <div class="channel-info">
                    <h3>${escapeHtml(channel.name)}</h3>
                    <span class="channel-number">${channel.number}</span>
                    <div class="channel-status ${channel.enabled ? 'status-inactive' : 'status-disabled'}">
                        ${channel.enabled ? 'Enabled' : 'Disabled'}
                    </div>
                </div>
                ${channel.logo_url ? `<img src="${escapeHtml(channel.logo_url)}" alt="Logo" class="channel-logo">` : ''}
            </div>
            <div class="channel-details">
                <div><strong>Category:</strong> ${escapeHtml(channel.category)}</div>
                <div><strong>Playlist:</strong> ${channel.playlist.length} items</div>
                <div><strong>Loop:</strong> ${channel.loop ? 'Yes' : 'No'}</div>
            </div>
            <div class="channel-actions">
                <button class="btn btn-primary btn-small" onclick="editChannel('${channel.id}')">Edit</button>
                <button class="btn btn-danger btn-small" onclick="deleteChannel('${channel.id}')">Delete</button>
                <a href="/stream/${channel.id}/master.m3u8" class="btn btn-secondary btn-small" target="_blank">Play</a>
            </div>
        </div>
    `).join('');
}

function openModal(channelId = null) {
    currentChannelId = channelId;
    playlistItemCounter = 0;

    if (channelId) {
        // Edit mode
        const channel = channels.find(c => c.id === channelId);
        if (!channel) return;

        document.getElementById('modalTitle').textContent = 'Edit Channel';
        document.getElementById('channelId').value = channel.id;
        document.getElementById('channelName').value = channel.name;
        document.getElementById('channelNumber').value = channel.number;
        document.getElementById('channelCategory').value = channel.category;
        document.getElementById('channelLogo').value = channel.logo_url || '';
        document.getElementById('channelLoop').checked = channel.loop;
        document.getElementById('channelEnabled').checked = channel.enabled;

        // Stream settings
        document.getElementById('videoBitrate').value = channel.stream_settings.video_bitrate;
        document.getElementById('audioBitrate').value = channel.stream_settings.audio_bitrate;
        document.getElementById('resolution').value = channel.stream_settings.resolution;
        document.getElementById('transcodePreset').value = channel.stream_settings.transcode_preset;

        // Load playlist items
        playlistItemsContainer.innerHTML = '';
        channel.playlist.forEach(item => {
            addPlaylistItem(item);
        });
    } else {
        // Create mode
        document.getElementById('modalTitle').textContent = 'Add Channel';
        channelForm.reset();
        playlistItemsContainer.innerHTML = '';
        document.getElementById('channelId').value = '';

        // Set defaults
        document.getElementById('videoBitrate').value = 3000;
        document.getElementById('audioBitrate').value = 128;
        document.getElementById('resolution').value = '1280x720';
        document.getElementById('transcodePreset').value = 'software_fast';
    }

    channelModal.style.display = 'block';
}

function closeModal() {
    channelModal.style.display = 'none';
    currentChannelId = null;
}

function addPlaylistItem(item = null) {
    const itemId = playlistItemCounter++;
    const itemDiv = document.createElement('div');
    itemDiv.className = 'playlist-item';
    itemDiv.dataset.itemId = itemId;

    itemDiv.innerHTML = `
        <div class="playlist-item-header">
            <strong>Item ${itemId + 1}</strong>
            <button type="button" class="btn btn-danger btn-small" onclick="removePlaylistItem(${itemId})">Remove</button>
        </div>
        <input type="text" placeholder="File Path (e.g., D:/media/video.mp4)" class="playlist-file-path" value="${item ? escapeHtml(item.file_path) : ''}" required>
        <input type="number" placeholder="Duration (seconds)" class="playlist-duration" min="1" value="${item ? item.duration : ''}" required>
        <input type="text" placeholder="Title" class="playlist-title" value="${item ? escapeHtml(item.title) : ''}" required>
        <input type="text" placeholder="Description (optional)" class="playlist-description" value="${item ? escapeHtml(item.description || '') : ''}">
    `;

    playlistItemsContainer.appendChild(itemDiv);
}

function removePlaylistItem(itemId) {
    const itemDiv = document.querySelector(`[data-item-id="${itemId}"]`);
    if (itemDiv) {
        itemDiv.remove();
    }
}

async function handleSubmit(e) {
    e.preventDefault();

    // Collect playlist items
    const playlistItems = [];
    const itemDivs = playlistItemsContainer.querySelectorAll('.playlist-item');

    itemDivs.forEach(itemDiv => {
        const filePath = itemDiv.querySelector('.playlist-file-path').value;
        const duration = parseInt(itemDiv.querySelector('.playlist-duration').value);
        const title = itemDiv.querySelector('.playlist-title').value;
        const description = itemDiv.querySelector('.playlist-description').value;

        playlistItems.push({
            file_path: filePath,
            duration: duration,
            title: title,
            description: description
        });
    });

    // Build channel object
    const channelData = {
        id: currentChannelId || '',
        name: document.getElementById('channelName').value,
        number: parseInt(document.getElementById('channelNumber').value),
        category: document.getElementById('channelCategory').value,
        logo_url: document.getElementById('channelLogo').value || null,
        playlist: playlistItems,
        loop: document.getElementById('channelLoop').checked,
        start_time: null,
        stream_settings: {
            video_bitrate: parseInt(document.getElementById('videoBitrate').value),
            audio_bitrate: parseInt(document.getElementById('audioBitrate').value),
            segment_duration: 6,
            playlist_size: 10,
            transcode_preset: document.getElementById('transcodePreset').value,
            resolution: document.getElementById('resolution').value
        },
        enabled: document.getElementById('channelEnabled').checked
    };

    try {
        let response;
        if (currentChannelId) {
            // Update
            response = await fetch(`${API_BASE}/api/channels/${currentChannelId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(channelData)
            });
        } else {
            // Create
            response = await fetch(`${API_BASE}/api/channels`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(channelData)
            });
        }

        if (response.ok) {
            closeModal();
            loadChannels();
        } else {
            const error = await response.json();
            alert('Error saving channel: ' + JSON.stringify(error));
        }
    } catch (error) {
        console.error('Error saving channel:', error);
        alert('Error saving channel: ' + error.message);
    }
}

async function editChannel(channelId) {
    openModal(channelId);
}

async function deleteChannel(channelId) {
    const channel = channels.find(c => c.id === channelId);
    if (!channel) return;

    if (!confirm(`Delete channel "${channel.name}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/channels/${channelId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadChannels();
        } else {
            alert('Error deleting channel');
        }
    } catch (error) {
        console.error('Error deleting channel:', error);
        alert('Error deleting channel: ' + error.message);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
