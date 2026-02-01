// API base URL
const API_BASE = '';

// Global state
let channels = [];
let currentChannelId = null;
let playlistItemCounter = 0;
let currentMediaPath = '';
let currentPlaylistInput = null;
let currentChannelLogo = null;
let pendingLogoFile = null;

// DOM elements
const channelList = document.getElementById('channelList');
const channelModal = document.getElementById('channelModal');
const channelForm = document.getElementById('channelForm');
const addChannelBtn = document.getElementById('addChannelBtn');
const cancelBtn = document.getElementById('cancelBtn');
const closeBtn = document.querySelector('.close');
// Removed: playlist items now managed separately in playlists.html

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadChannels();
    loadVersion();
    setupEventListeners();
});

function setupEventListeners() {
    addChannelBtn.addEventListener('click', () => openModal());
    cancelBtn.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);
    channelForm.addEventListener('submit', handleSubmit);

    // Setup logo handlers
    setupLogoHandlers();

    // Media browser modal handlers
    const closeMediaBrowserBtn = document.querySelector('.close-media-browser');
    const cancelMediaBrowserBtn = document.getElementById('cancelMediaBrowser');
    if (closeMediaBrowserBtn) {
        closeMediaBrowserBtn.addEventListener('click', closeMediaBrowser);
    }
    if (cancelMediaBrowserBtn) {
        cancelMediaBrowserBtn.addEventListener('click', closeMediaBrowser);
    }

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === channelModal) {
            closeModal();
        }
        if (e.target === document.getElementById('mediaBrowserModal')) {
            closeMediaBrowser();
        }
    });
}

async function loadVersion() {
    try {
        const response = await fetch(`${API_BASE}/version`);
        const data = await response.json();
        document.getElementById('versionInfo').textContent = `v${data.version}`;
    } catch (error) {
        console.error('Error loading version:', error);
        document.getElementById('versionInfo').textContent = '';
    }
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

async function loadPlaylistsForSelect() {
    try {
        const response = await fetch(`${API_BASE}/api/playlists`);
        const playlists = await response.json();

        const select = document.getElementById('channelPlaylist');
        select.innerHTML = '<option value="">-- No Playlist --</option>';

        playlists.forEach(playlist => {
            const option = document.createElement('option');
            option.value = playlist.id;
            option.textContent = `${playlist.name} (${playlist.items.length} items)`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading playlists:', error);
    }
}

async function openModal(channelId = null) {
    currentChannelId = channelId;

    // Load playlists for selector
    await loadPlaylistsForSelect();

    if (channelId) {
        // Edit mode
        const channel = channels.find(c => c.id === channelId);
        if (!channel) return;

        document.getElementById('modalTitle').textContent = 'Edit Channel';
        document.getElementById('channelId').value = channel.id;
        document.getElementById('channelName').value = channel.name;
        document.getElementById('channelNumber').value = channel.number;
        document.getElementById('channelCategory').value = channel.category;
        document.getElementById('channelLoop').checked = channel.loop;
        document.getElementById('channelEnabled').checked = channel.enabled;

        // Handle logo
        const logoUrl = channel.logo_url || '';
        document.getElementById('currentLogoUrl').value = logoUrl;
        pendingLogoFile = null;

        if (logoUrl) {
            document.getElementById('logoPreview').src = logoUrl;
            document.getElementById('logoPreview').style.display = 'block';
            document.getElementById('logoPlaceholder').style.display = 'none';

            if (logoUrl.startsWith('http')) {
                document.getElementById('logoTypeUrl').checked = true;
                document.getElementById('logoUrlInput').value = logoUrl;
                document.getElementById('logoUrlInput').style.display = 'block';
                document.getElementById('logoFileInput').style.display = 'none';
            } else {
                document.getElementById('logoTypeUpload').checked = true;
                document.getElementById('logoFileInput').style.display = 'block';
                document.getElementById('logoUrlInput').style.display = 'none';
            }
        } else {
            document.getElementById('logoPreview').style.display = 'none';
            document.getElementById('logoPlaceholder').style.display = 'block';
            document.getElementById('logoTypeUpload').checked = true;
            document.getElementById('logoFileInput').style.display = 'block';
            document.getElementById('logoUrlInput').style.display = 'none';
        }

        // Stream settings
        document.getElementById('videoBitrate').value = channel.stream_settings.video_bitrate;
        document.getElementById('audioBitrate').value = channel.stream_settings.audio_bitrate;
        document.getElementById('resolution').value = channel.stream_settings.resolution;
        document.getElementById('transcodePreset').value = channel.stream_settings.transcode_preset;

        // Set selected playlist
        if (channel.playlist_id) {
            document.getElementById('channelPlaylist').value = channel.playlist_id;
        } else {
            document.getElementById('channelPlaylist').value = '';
        }
    } else {
        // Create mode
        document.getElementById('modalTitle').textContent = 'Add Channel';
        channelForm.reset();
        document.getElementById('channelId').value = '';

        // Reset logo state
        document.getElementById('currentLogoUrl').value = '';
        pendingLogoFile = null;
        document.getElementById('logoPreview').style.display = 'none';
        document.getElementById('logoPlaceholder').style.display = 'block';
        document.getElementById('logoTypeUpload').checked = true;
        document.getElementById('logoFileInput').style.display = 'block';
        document.getElementById('logoUrlInput').style.display = 'none';
        document.getElementById('logoFileInput').value = '';
        document.getElementById('logoUrlInput').value = '';

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

function setupLogoHandlers() {
    const logoTypeUpload = document.getElementById('logoTypeUpload');
    const logoTypeUrl = document.getElementById('logoTypeUrl');
    const logoFileInput = document.getElementById('logoFileInput');
    const logoUrlInput = document.getElementById('logoUrlInput');
    const logoPreview = document.getElementById('logoPreview');
    const logoPlaceholder = document.getElementById('logoPlaceholder');

    logoTypeUpload.addEventListener('change', function() {
        if (this.checked) {
            logoFileInput.style.display = 'block';
            logoUrlInput.style.display = 'none';
            logoUrlInput.value = '';
        }
    });

    logoTypeUrl.addEventListener('change', function() {
        if (this.checked) {
            logoFileInput.style.display = 'none';
            logoUrlInput.style.display = 'block';
            logoFileInput.value = '';
            pendingLogoFile = null;
        }
    });

    logoFileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            pendingLogoFile = file;
            const reader = new FileReader();
            reader.onload = function(e) {
                logoPreview.src = e.target.result;
                logoPreview.style.display = 'block';
                logoPlaceholder.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });

    logoUrlInput.addEventListener('input', function() {
        if (this.value) {
            logoPreview.src = this.value;
            logoPreview.style.display = 'block';
            logoPlaceholder.style.display = 'none';
        } else {
            logoPreview.style.display = 'none';
            logoPlaceholder.style.display = 'block';
        }
    });
}

async function uploadChannelLogo(channelId, file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/api/uploads/logo/${channelId}`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            return data.logo_url;
        } else {
            const error = await response.json();
            console.error('Logo upload failed:', error);
            return null;
        }
    } catch (error) {
        console.error('Error uploading logo:', error);
        return null;
    }
}

// Playlist item management moved to playlists.js

async function openMediaBrowser(inputElement) {
    currentPlaylistInput = inputElement;
    currentMediaPath = '';
    document.getElementById('mediaBrowserModal').style.display = 'block';
    await loadMediaFiles('');
}

async function loadMediaFiles(path) {
    currentMediaPath = path;
    const fileList = document.getElementById('mediaFileList');
    const breadcrumb = document.getElementById('mediaBreadcrumb');

    try {
        fileList.innerHTML = '<p class="loading">Loading files...</p>';

        const url = `${API_BASE}/api/media/browse${path ? '?path=' + encodeURIComponent(path) : ''}`;
        const response = await fetch(url);
        const data = await response.json();

        breadcrumb.innerHTML = generateBreadcrumb(data.current_path, data.parent_path);

        if (data.items.length === 0) {
            fileList.innerHTML = '<p class="loading">No files found</p>';
            return;
        }

        fileList.innerHTML = data.items.map(item => {
            if (item.type === 'directory') {
                return `
                    <div class="media-item media-folder" onclick="navigateToFolder('${escapeHtml(item.path)}')">
                        <span class="media-icon">📁</span>
                        <span class="media-name">${escapeHtml(item.name)}</span>
                    </div>
                `;
            } else {
                const sizeStr = formatFileSize(item.size);
                const durationStr = item.duration ? formatDuration(item.duration) : '';
                return `
                    <div class="media-item media-file" onclick="selectMediaFile('${escapeHtml(item.path)}', ${item.duration || 0})">
                        <span class="media-icon">🎬</span>
                        <div class="media-info">
                            <span class="media-name">${escapeHtml(item.name)}</span>
                            <span class="media-meta">${sizeStr}${durationStr ? ' • ' + durationStr : ''}</span>
                        </div>
                    </div>
                `;
            }
        }).join('');
    } catch (error) {
        console.error('Error loading media files:', error);
        fileList.innerHTML = '<p class="loading">Error loading files</p>';
    }
}

function generateBreadcrumb(currentPath, parentPath) {
    if (!currentPath) {
        return '<span class="breadcrumb-item">Media</span>';
    }

    const parts = currentPath.split('/').filter(p => p);
    let html = '<span class="breadcrumb-item" onclick="loadMediaFiles(\'\')">Media</span>';

    let accumulated = '';
    parts.forEach((part, index) => {
        accumulated += (accumulated ? '/' : '') + part;
        const isLast = index === parts.length - 1;
        html += ` / <span class="breadcrumb-item${isLast ? ' active' : ''}" onclick="loadMediaFiles('${accumulated}')">${escapeHtml(part)}</span>`;
    });

    return html;
}

function navigateToFolder(path) {
    loadMediaFiles(path);
}

function selectMediaFile(path, duration) {
    if (currentPlaylistInput) {
        const fullPath = `/data/media/${path}`;
        currentPlaylistInput.value = fullPath;

        const playlistItem = currentPlaylistInput.closest('.playlist-item');
        const durationInput = playlistItem.querySelector('.playlist-duration');
        if (duration && !durationInput.value) {
            durationInput.value = duration;
        }
    }

    closeMediaBrowser();
}

function closeMediaBrowser() {
    document.getElementById('mediaBrowserModal').style.display = 'none';
    currentPlaylistInput = null;
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
}

async function handleSubmit(e) {
    e.preventDefault();

    // Get selected playlist ID
    const playlistId = document.getElementById('channelPlaylist').value || null;

    // Determine logo URL
    let logoUrl = null;
    const logoType = document.querySelector('input[name="logoType"]:checked').value;

    if (logoType === 'upload' && pendingLogoFile) {
        // Will upload after channel is created
    } else if (logoType === 'url') {
        logoUrl = document.getElementById('logoUrlInput').value || null;
    } else {
        // Keep existing logo
        logoUrl = document.getElementById('currentLogoUrl').value || null;
    }

    // Build channel object
    const channelData = {
        id: currentChannelId || '',
        name: document.getElementById('channelName').value,
        number: parseInt(document.getElementById('channelNumber').value),
        category: document.getElementById('channelCategory').value,
        logo_url: logoUrl,
        playlist_id: playlistId,
        playlist: [],  // Empty for backward compatibility
        scheduled_playlists: [],
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
            const savedChannel = await response.json();

            // Upload logo if needed
            if (pendingLogoFile) {
                const uploadedLogoUrl = await uploadChannelLogo(savedChannel.id, pendingLogoFile);
                if (uploadedLogoUrl) {
                    savedChannel.logo_url = uploadedLogoUrl;
                    await fetch(`${API_BASE}/api/channels/${savedChannel.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(savedChannel)
                    });
                }
                pendingLogoFile = null;
            }

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
