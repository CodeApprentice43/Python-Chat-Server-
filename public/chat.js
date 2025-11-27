// State management
let currentUsername = null;
let isAuthenticated = false;
let isGuest = false;
let ws = null;
let authMode = 'login'; // 'login' or 'register'

// DOM Elements
const authContainer = document.getElementById('authContainer');
const chatContainer = document.getElementById('chatContainer');
const authForm = document.getElementById('authForm');
const authTitle = document.getElementById('authTitle');
const authSubmitBtn = document.getElementById('authSubmitBtn');
const toggleAuthBtn = document.getElementById('toggleAuthBtn');
const guestBtn = document.getElementById('guestBtn');
const errorMessage = document.getElementById('errorMessage');
const passwordGroup = document.getElementById('passwordGroup');
const currentUserEl = document.getElementById('currentUser');
const messagesContainer = document.getElementById('messagesContainer');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const logoutBtn = document.getElementById('logoutBtn');
const usersList = document.getElementById('usersList');
const attachBtn = document.getElementById('attachBtn');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');

let selectedFile = null;

// Check if already authenticated
window.addEventListener('DOMContentLoaded', () => {
    const authCookie = getCookie('auth');
    if (authCookie === 'true') {
        // Try to connect as authenticated user
        loadMessages();
        showChat();
        connectWebSocket();
    }
});

// Toggle between login and register
toggleAuthBtn.addEventListener('click', () => {
    authMode = authMode === 'login' ? 'register' : 'login';

    if (authMode === 'register') {
        authTitle.textContent = 'Create Account';
        authSubmitBtn.textContent = 'Register';
        toggleAuthBtn.textContent = 'Already have an account?';
    } else {
        authTitle.textContent = 'Login to Chat';
        authSubmitBtn.textContent = 'Login';
        toggleAuthBtn.textContent = 'Create Account';
    }

    hideError();
});

// Continue as guest
guestBtn.addEventListener('click', () => {
    console.log('Continuing as guest');
    currentUsername = 'guest';
    isGuest = true;
    isAuthenticated = false;
    currentUserEl.textContent = 'Guest';
    showChat();
    connectWebSocket();
    loadMessages();
});

// Handle auth form submission
authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const endpoint = authMode === 'login' ? '/login' : '/register';

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString(),
        });

        if (response.ok) {
            currentUsername = username;
            isAuthenticated = true;
            isGuest = false;
            currentUserEl.textContent = username;
            loadMessages();
            showChat();
            connectWebSocket();
        } else {
            const errorText = await response.text();
            showError(errorText || 'Authentication failed');
        }
    } catch (error) {
        showError('Network error. Please try again.');
    }
});

// Logout
logoutBtn.addEventListener('click', async () => {
    if (isAuthenticated) {
        try {
            await fetch('/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    if (ws) {
        ws.close();
    }

    currentUsername = null;
    isAuthenticated = false;
    isGuest = false;
    messagesContainer.innerHTML = '';
    usersList.innerHTML = '';

    authContainer.classList.remove('hidden');
    chatContainer.classList.remove('active');
});

// Load existing messages
async function loadMessages() {
    try {
        const response = await fetch('/chat-messages');
        const messages = await response.json();

        messages.forEach(msg => {
            addMessage(msg.username, msg.message || '', msg.id, false, msg.media || null);
        });

        scrollToBottom();
    } catch (error) {
        console.error('Failed to load messages:', error);
    }
}

// Connect to WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/websocket`;

    console.log('Connecting to WebSocket:', wsUrl);
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✓ WebSocket connected successfully');
        sendBtn.disabled = false;
    };

    ws.onmessage = (event) => {
        console.log('WebSocket message received:', event.data);
        const data = JSON.parse(event.data);

        if (data.type === 'welcome') {
            console.log('Welcome message:', data);
        } else if (data.type === 'chat') {
            console.log('Chat message:', data);
            addMessage(data.username, data.message, data.id, false, data.media || null);
            scrollToBottom();
        } else if (data.type === 'online-users') {
            console.log('Online users update:', data.users);
            updateOnlineUsers(data.users);
        }
    };

    ws.onerror = (error) => {
        console.error('✗ WebSocket error:', error);
        sendBtn.disabled = true;
    };

    ws.onclose = (event) => {
        console.log('✗ WebSocket disconnected. Code:', event.code, 'Reason:', event.reason);
        sendBtn.disabled = true;

        // Attempt to reconnect after 3 seconds
        if (currentUsername) {
            console.log('Will reconnect in 3 seconds...');
            setTimeout(() => {
                if (currentUsername) {
                    connectWebSocket();
                }
            }, 3000);
        }
    };
}

// Send message via WebSocket
messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    e.stopPropagation();

    const message = messageInput.value.trim();
    if (!message) return;

    console.log('Sending message:', message);
    console.log('WebSocket state:', ws ? ws.readyState : 'null');

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'chat',
            message: message
        }));

        messageInput.value = '';
        messageInput.focus();
    } else {
        console.error('WebSocket not connected');
        alert('Not connected to server. Please refresh the page.');
    }

    return false;
});

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Enter to send, Shift+Enter for new line
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        messageForm.dispatchEvent(new Event('submit'));
    }
});

// Add message to UI
function addMessage(username, content, messageId, isOwn, media = null) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message';
    messageEl.dataset.id = messageId;

    if (username === currentUsername || (isGuest && username === 'guest')) {
        messageEl.classList.add('own');
    }

    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });

    let mediaHtml = '';
    if (media) {
        if (media.type && media.type.startsWith('image/')) {
            mediaHtml = `
                <div class="message-media">
                    <img src="${media.url}" alt="${escapeHtml(media.filename || 'Image')}"
                         onclick="window.open('${media.url}', '_blank')">
                </div>
            `;
        } else if (media.type && media.type.startsWith('video/')) {
            mediaHtml = `
                <div class="message-media">
                    <video src="${media.url}" controls></video>
                </div>
            `;
        }
    }

    messageEl.innerHTML = `
        <div class="message-header">
            <span class="message-author">${escapeHtml(username)}</span>
            <span class="message-time">${timeStr}</span>
        </div>
        ${content ? `<div class="message-content">${escapeHtml(content)}</div>` : ''}
        ${mediaHtml}
    `;

    messagesContainer.appendChild(messageEl);
}

// Update online users list
function updateOnlineUsers(users) {
    usersList.innerHTML = '';

    if (users.length === 0) {
        usersList.innerHTML = '<div style="color: #71717a; font-size: 0.875rem;">No users online</div>';
        return;
    }

    users.forEach(user => {
        const userEl = document.createElement('div');
        userEl.className = 'user-item';
        userEl.innerHTML = `
            <div class="user-status"></div>
            <span>${escapeHtml(user)}</span>
        `;
        usersList.appendChild(userEl);
    });
}

// Utility functions
function showChat() {
    authContainer.classList.add('hidden');
    chatContainer.classList.add('active');
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// File upload handling
attachBtn.addEventListener('click', () => {
    if (!isAuthenticated) {
        alert('Please log in to upload files');
        return;
    }
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4'];
    if (!validTypes.includes(file.type)) {
        alert('Only images (JPEG, PNG, GIF) and MP4 videos are allowed');
        fileInput.value = '';
        return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB');
        fileInput.value = '';
        return;
    }

    selectedFile = file;
    showFilePreview(file);
});

function showFilePreview(file) {
    const reader = new FileReader();

    reader.onload = (e) => {
        const isImage = file.type.startsWith('image/');
        const isVideo = file.type.startsWith('video/');

        filePreview.innerHTML = `
            ${isImage ? `<img src="${e.target.result}" alt="Preview">` : ''}
            ${isVideo ? `<video src="${e.target.result}" controls></video>` : ''}
            <div class="file-preview-info">
                <div class="file-preview-name">${escapeHtml(file.name)}</div>
                <div class="file-preview-size">${formatFileSize(file.size)}</div>
            </div>
            <button type="button" class="file-preview-remove" onclick="removeFilePreview()">Remove</button>
        `;

        filePreview.classList.remove('hidden');
    };

    reader.readAsDataURL(file);
}

function removeFilePreview() {
    selectedFile = null;
    fileInput.value = '';
    filePreview.classList.add('hidden');
    filePreview.innerHTML = '';
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload-file', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            return result;
        } else {
            const error = await response.text();
            throw new Error(error);
        }
    } catch (error) {
        console.error('Upload failed:', error);
        throw error;
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Update message sending to handle file uploads
const originalSubmitHandler = messageForm.onsubmit;
messageForm.onsubmit = null;

messageForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const message = messageInput.value.trim();

    // If there's a file, upload it first
    if (selectedFile) {
        if (!isAuthenticated) {
            alert('Please log in to upload files');
            return false;
        }

        try {
            sendBtn.disabled = true;
            sendBtn.textContent = 'Uploading...';

            const uploadResult = await uploadFile(selectedFile);

            // Send message with file URL
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'chat',
                    message: message || '',
                    media: {
                        url: uploadResult.url,
                        type: uploadResult.mime_type,
                        filename: uploadResult.original_filename
                    }
                }));

                messageInput.value = '';
                removeFilePreview();
            }
        } catch (error) {
            alert('File upload failed: ' + error.message);
        } finally {
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
        }

        return false;
    }

    // Regular text message
    if (!message) return false;

    console.log('Sending message:', message);
    console.log('WebSocket state:', ws ? ws.readyState : 'null');

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'chat',
            message: message
        }));

        messageInput.value = '';
        messageInput.focus();
    } else {
        console.error('WebSocket not connected');
        alert('Not connected to server. Please refresh the page.');
    }

    return false;
});
