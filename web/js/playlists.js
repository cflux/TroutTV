// API base URL
const API_BASE = '';

// Global state
let playlists = [];
let currentPlaylistId = null;
let playlistItemCounter = 0;
let currentMediaPath = '';
let currentPlaylistInput = null;
let selectedMediaFiles = [];
let allMediaFiles = [];

// DOM elements
const playlistList = document.getElementById('playlistList');
const playlistModal = document.getElementById('playlistModal');
const playlistForm = document.getElementById('playlistForm');
const addPlaylistBtn = document.getElementById('addPlaylistBtn');
const cancelBtn = document.getElementById('cancelBtn');
const closeBtn = document.querySelector('.close');
const addItemBtn = document.getElementById('addItemBtn');
const playlistItemsContainer = document.getElementById('playlistItems');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPlaylists();
    loadVersion();
    setupEventListeners();
});

function setupEventListeners() {
    addPlaylistBtn.addEventListener('click', () => openModal());
    cancelBtn.addEventListener('click', closeModal);
    closeBtn.addEventListener('click', closeModal);
    playlistForm.addEventListener('submit', handleSubmit);
    addItemBtn.addEventListener('click', addPlaylistItem);

    // Media browser modal handlers
    const closeMediaBrowserBtn = document.querySelector('.close-media-browser');
    const cancelMediaBrowserBtn = document.getElementById('cancelMediaBrowser');
    const selectAllFilesBtn = document.getElementById('selectAllFiles');
    const addSelectedFilesBtn = document.getElementById('addSelectedFiles');
    const addAllInFolderBtn = document.getElementById('addAllInFolder');

    if (closeMediaBrowserBtn) {
        closeMediaBrowserBtn.addEventListener('click', closeMediaBrowser);
    }
    if (cancelMediaBrowserBtn) {
        cancelMediaBrowserBtn.addEventListener('click', closeMediaBrowser);
    }
    if (selectAllFilesBtn) {
        selectAllFilesBtn.addEventListener('change', toggleSelectAll);
    }
    if (addSelectedFilesBtn) {
        addSelectedFilesBtn.addEventListener('click', addSelectedFilesToPlaylist);
    }
    if (addAllInFolderBtn) {
        addAllInFolderBtn.addEventListener('click', addAllFilesInFolder);
    }

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === playlistModal) {
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

async function loadPlaylists() {
    try {
        const response = await fetch(`${API_BASE}/api/playlists`);
        playlists = await response.json();
        renderPlaylists();
    } catch (error) {
        console.error('Error loading playlists:', error);
        playlistList.innerHTML = '<p class="loading">Error loading playlists</p>';
    }
}

function renderPlaylists() {
    if (playlists.length === 0) {
        playlistList.innerHTML = '<p class="loading">No playlists yet. Click "Add Playlist" to create one.</p>';
        return;
    }

    playlistList.innerHTML = playlists.map(playlist => `
        <div class="channel-card">
            <div class="channel-header">
                <div class="channel-info">
                    <h3>${escapeHtml(playlist.name)}</h3>
                    <span class="channel-number">${playlist.items.length} items</span>
                </div>
            </div>
            <div class="channel-details">
                ${playlist.description ? `<p class="channel-description">${escapeHtml(playlist.description)}</p>` : ''}
                ${playlist.tags && playlist.tags.length > 0 ? `<p class="tags">Tags: ${playlist.tags.map(tag => escapeHtml(tag)).join(', ')}</p>` : ''}
            </div>
            <div class="channel-actions">
                <button class="btn btn-secondary" onclick="editPlaylist('${playlist.id}')">Edit</button>
                <button class="btn btn-danger" onclick="deletePlaylist('${playlist.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

function openModal(playlistId = null) {
    currentPlaylistId = playlistId;
    playlistItemsContainer.innerHTML = '';
    playlistItemCounter = 0;

    if (playlistId) {
        // Edit mode
        document.getElementById('modalTitle').textContent = 'Edit Playlist';
        const playlist = playlists.find(p => p.id === playlistId);
        if (playlist) {
            document.getElementById('playlistId').value = playlist.id;
            document.getElementById('playlistName').value = playlist.name;
            document.getElementById('playlistDescription').value = playlist.description || '';

            // Add existing items
            if (playlist.items && playlist.items.length > 0) {
                playlist.items.forEach(item => addPlaylistItem(item));
            }
        }
    } else {
        // Create mode
        document.getElementById('modalTitle').textContent = 'Add Playlist';
        playlistForm.reset();
        document.getElementById('playlistId').value = '';
    }

    playlistModal.style.display = 'block';
}

function closeModal() {
    playlistModal.style.display = 'none';
    playlistForm.reset();
    playlistItemsContainer.innerHTML = '';
}

async function handleSubmit(e) {
    e.preventDefault();

    // Collect playlist items
    const items = [];
    const itemDivs = playlistItemsContainer.querySelectorAll('.playlist-item');
    itemDivs.forEach(itemDiv => {
        const filePath = itemDiv.querySelector('.playlist-file-path').value;
        const duration = parseInt(itemDiv.querySelector('.playlist-duration').value);
        const title = itemDiv.querySelector('.playlist-title').value;
        const description = itemDiv.querySelector('.playlist-description').value;

        items.push({
            file_path: filePath,
            duration: duration,
            title: title,
            description: description || ''
        });
    });

    const playlistData = {
        id: document.getElementById('playlistId').value || '',
        name: document.getElementById('playlistName').value,
        description: document.getElementById('playlistDescription').value || '',
        items: items,
        tags: []
    };

    try {
        let response;
        if (currentPlaylistId) {
            // Update existing playlist
            response = await fetch(`${API_BASE}/api/playlists/${currentPlaylistId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(playlistData)
            });
        } else {
            // Create new playlist
            response = await fetch(`${API_BASE}/api/playlists`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(playlistData)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save playlist');
        }

        closeModal();
        await loadPlaylists();
    } catch (error) {
        console.error('Error saving playlist:', error);
        alert(`Error saving playlist: ${error.message}`);
    }
}

async function editPlaylist(playlistId) {
    openModal(playlistId);
}

async function deletePlaylist(playlistId) {
    const playlist = playlists.find(p => p.id === playlistId);
    if (!confirm(`Are you sure you want to delete "${playlist.name}"? This will fail if any channels are using this playlist.`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/playlists/${playlistId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete playlist');
        }

        await loadPlaylists();
    } catch (error) {
        console.error('Error deleting playlist:', error);
        alert(`Error deleting playlist: ${error.message}`);
    }
}

function addPlaylistItem(item = null) {
    const itemId = playlistItemCounter++;
    const itemDiv = document.createElement('div');
    itemDiv.className = 'playlist-item';
    itemDiv.dataset.itemId = itemId;

    itemDiv.innerHTML = `
        <div class="playlist-item-header">
            <strong>Item ${itemId + 1}</strong>
            <div class="playlist-item-controls">
                <button type="button" class="btn btn-secondary btn-small" onclick="movePlaylistItemUp(${itemId})" title="Move Up">↑</button>
                <button type="button" class="btn btn-secondary btn-small" onclick="movePlaylistItemDown(${itemId})" title="Move Down">↓</button>
                <button type="button" class="btn btn-danger btn-small" onclick="removePlaylistItem(${itemId})">Remove</button>
            </div>
        </div>
        <div class="playlist-file-input-group">
            <input type="text" placeholder="File Path" class="playlist-file-path" value="${item ? escapeHtml(item.file_path) : ''}" readonly required>
            <button type="button" class="btn btn-secondary btn-small browse-media-btn">Browse</button>
        </div>
        <input type="number" placeholder="Duration (seconds)" class="playlist-duration" min="1" value="${item ? item.duration : ''}" required>
        <input type="text" placeholder="Title" class="playlist-title" value="${item ? escapeHtml(item.title) : ''}" required>
        <input type="text" placeholder="Description (optional)" class="playlist-description" value="${item ? escapeHtml(item.description || '') : ''}">
    `;

    playlistItemsContainer.appendChild(itemDiv);

    // Add event listener for browse button
    const browseBtn = itemDiv.querySelector('.browse-media-btn');
    const fileInput = itemDiv.querySelector('.playlist-file-path');
    browseBtn.addEventListener('click', () => openMediaBrowser(fileInput));
}

function removePlaylistItem(itemId) {
    const itemDiv = document.querySelector(`[data-item-id="${itemId}"]`);
    if (itemDiv) {
        itemDiv.remove();
    }
}

function movePlaylistItemUp(itemId) {
    const itemDiv = document.querySelector(`[data-item-id="${itemId}"]`);
    if (itemDiv && itemDiv.previousElementSibling) {
        playlistItemsContainer.insertBefore(itemDiv, itemDiv.previousElementSibling);
    }
}

function movePlaylistItemDown(itemId) {
    const itemDiv = document.querySelector(`[data-item-id="${itemId}"]`);
    if (itemDiv && itemDiv.nextElementSibling) {
        playlistItemsContainer.insertBefore(itemDiv.nextElementSibling, itemDiv);
    }
}

// Media Browser Functions
async function openMediaBrowser(inputElement) {
    currentPlaylistInput = inputElement;
    currentMediaPath = '';
    selectedMediaFiles = [];
    allMediaFiles = [];
    document.getElementById('mediaBrowserModal').style.display = 'block';
    await loadMediaFiles('');
}

function closeMediaBrowser() {
    document.getElementById('mediaBrowserModal').style.display = 'none';
    currentPlaylistInput = null;
    selectedMediaFiles = [];
    allMediaFiles = [];
    updateSelectedCount();
}

async function loadMediaFiles(path) {
    currentMediaPath = path;
    const fileList = document.getElementById('mediaFileList');
    const breadcrumb = document.getElementById('mediaBreadcrumb');
    const addAllBtn = document.getElementById('addAllInFolder');
    const selectAllCheckbox = document.getElementById('selectAllFiles');

    // Reset selection
    selectedMediaFiles = [];
    allMediaFiles = [];
    selectAllCheckbox.checked = false;
    updateSelectedCount();

    try {
        fileList.innerHTML = '<p class="loading">Loading files...</p>';

        const url = `${API_BASE}/api/media/browse${path ? '?path=' + encodeURIComponent(path) : ''}`;
        const response = await fetch(url);
        const data = await response.json();

        breadcrumb.innerHTML = generateBreadcrumb(data.current_path, data.parent_path);

        if (data.items.length === 0) {
            fileList.innerHTML = '<p class="loading">No files found</p>';
            addAllBtn.style.display = 'none';
            return;
        }

        // Store all files for bulk operations
        allMediaFiles = data.items.filter(item => item.type === 'file');

        // Show "Add All" button if there are files
        if (allMediaFiles.length > 0) {
            addAllBtn.style.display = 'inline-block';
        } else {
            addAllBtn.style.display = 'none';
        }

        fileList.innerHTML = data.items.map((item, index) => {
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
                const fileIndex = allMediaFiles.findIndex(f => f.path === item.path);
                return `
                    <div class="media-item media-file">
                        <input type="checkbox" class="media-checkbox" data-file-index="${fileIndex}" onchange="toggleFileSelection(${fileIndex})">
                        <span class="media-icon" onclick="toggleFileCheckbox(${fileIndex})">🎬</span>
                        <div class="media-info" onclick="toggleFileCheckbox(${fileIndex})">
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
        addAllBtn.style.display = 'none';
    }
}

function generateBreadcrumb(currentPath, parentPath) {
    if (!currentPath) {
        return '<span class="breadcrumb-item">Root</span>';
    }

    const parts = currentPath.split(/[\/\\]/);
    let breadcrumb = `<span class="breadcrumb-item breadcrumb-link" onclick="navigateToFolder('')">Root</span>`;

    let pathSoFar = '';
    parts.forEach((part, index) => {
        if (!part) return;
        pathSoFar = pathSoFar ? `${pathSoFar}/${part}` : part;
        if (index === parts.length - 1) {
            breadcrumb += ` / <span class="breadcrumb-item">${escapeHtml(part)}</span>`;
        } else {
            breadcrumb += ` / <span class="breadcrumb-item breadcrumb-link" onclick="navigateToFolder('${escapeHtml(pathSoFar)}')">${escapeHtml(part)}</span>`;
        }
    });

    return breadcrumb;
}

async function navigateToFolder(path) {
    await loadMediaFiles(path);
}

function selectMediaFile(filePath, duration) {
    if (currentPlaylistInput) {
        currentPlaylistInput.value = filePath;

        const itemDiv = currentPlaylistInput.closest('.playlist-item');
        if (itemDiv) {
            // Fill in duration if available
            if (duration) {
                const durationInput = itemDiv.querySelector('.playlist-duration');
                if (durationInput && !durationInput.value) {
                    durationInput.value = Math.round(duration);
                }
            }

            // Auto-fill title from filename (if title is empty)
            const titleInput = itemDiv.querySelector('.playlist-title');
            if (titleInput && !titleInput.value) {
                // Extract filename from path
                const filename = filePath.split('/').pop();
                // Remove file extension
                const title = filename.replace(/\.[^/.]+$/, '');
                titleInput.value = title;
            }
        }

        closeMediaBrowser();
    }
}

// Utility Functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// Multi-select functions
function toggleFileCheckbox(fileIndex) {
    const checkbox = document.querySelector(`[data-file-index="${fileIndex}"]`);
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        toggleFileSelection(fileIndex);
    }
}

function toggleFileSelection(fileIndex) {
    const file = allMediaFiles[fileIndex];
    const existingIndex = selectedMediaFiles.findIndex(f => f.path === file.path);

    if (existingIndex >= 0) {
        selectedMediaFiles.splice(existingIndex, 1);
    } else {
        selectedMediaFiles.push(file);
    }

    updateSelectedCount();
}

function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAllFiles');
    const checkboxes = document.querySelectorAll('.media-checkbox');

    checkboxes.forEach((checkbox, index) => {
        checkbox.checked = selectAllCheckbox.checked;
    });

    if (selectAllCheckbox.checked) {
        selectedMediaFiles = [...allMediaFiles];
    } else {
        selectedMediaFiles = [];
    }

    updateSelectedCount();
}

function updateSelectedCount() {
    const countSpan = document.getElementById('selectedCount');
    const addSelectedBtn = document.getElementById('addSelectedFiles');

    if (countSpan) {
        countSpan.textContent = selectedMediaFiles.length;
    }

    if (addSelectedBtn) {
        addSelectedBtn.style.display = selectedMediaFiles.length > 0 ? 'inline-block' : 'none';
    }
}

function addSelectedFilesToPlaylist() {
    if (selectedMediaFiles.length === 0) return;

    selectedMediaFiles.forEach(file => {
        addPlaylistItemFromFile(file.path, file.duration);
    });

    closeMediaBrowser();
}

function addAllFilesInFolder() {
    if (allMediaFiles.length === 0) return;

    allMediaFiles.forEach(file => {
        addPlaylistItemFromFile(file.path, file.duration);
    });

    closeMediaBrowser();
}

function addPlaylistItemFromFile(filePath, duration) {
    const itemId = playlistItemCounter++;
    const itemDiv = document.createElement('div');
    itemDiv.className = 'playlist-item';
    itemDiv.dataset.itemId = itemId;

    // Extract filename and title
    const filename = filePath.split('/').pop();
    const title = filename.replace(/\.[^/.]+$/, '');

    itemDiv.innerHTML = `
        <div class="playlist-item-header">
            <strong>Item ${itemId + 1}</strong>
            <div class="playlist-item-controls">
                <button type="button" class="btn btn-secondary btn-small" onclick="movePlaylistItemUp(${itemId})" title="Move Up">↑</button>
                <button type="button" class="btn btn-secondary btn-small" onclick="movePlaylistItemDown(${itemId})" title="Move Down">↓</button>
                <button type="button" class="btn btn-danger btn-small" onclick="removePlaylistItem(${itemId})">Remove</button>
            </div>
        </div>
        <div class="playlist-file-input-group">
            <input type="text" placeholder="File Path" class="playlist-file-path" value="${escapeHtml(filePath)}" readonly required>
            <button type="button" class="btn btn-secondary btn-small browse-media-btn">Browse</button>
        </div>
        <input type="number" placeholder="Duration (seconds)" class="playlist-duration" min="1" value="${duration ? Math.round(duration) : ''}" required>
        <input type="text" placeholder="Title" class="playlist-title" value="${escapeHtml(title)}" required>
        <input type="text" placeholder="Description (optional)" class="playlist-description" value="">
    `;

    playlistItemsContainer.appendChild(itemDiv);

    // Add event listener for browse button
    const browseBtn = itemDiv.querySelector('.browse-media-btn');
    const fileInput = itemDiv.querySelector('.playlist-file-path');
    browseBtn.addEventListener('click', () => openMediaBrowser(fileInput));
}
