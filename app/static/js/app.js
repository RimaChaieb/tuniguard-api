// ===================================
// TuniGuard - Frontend JavaScript
// ===================================

// API Configuration
const API_BASE_URL = window.location.origin;

// Global state
let currentUserId = null;
let currentScanId = null;

// ===================================
// Authentication Functions
// ===================================

function checkAuthStatus() {
    const userData = localStorage.getItem('tuniguard_user');
    if (userData) {
        const user = JSON.parse(userData);
        currentUserId = user.user_id;
        showAppContainer(user);
        return true;
    }
    return false;
}

function openAuthModal(mode = 'login') {
    document.getElementById('authModal').classList.add('active');
    switchAuthTab(mode);
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('active');
}

function switchAuthTab(tab) {
    const loginForm = document.getElementById('loginFormContainer');
    const registerForm = document.getElementById('registerFormContainer');
    const modalTitle = document.getElementById('modalTitle');
    
    // Update tabs
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        document.querySelector('[data-tab="login"]').classList.add('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
        modalTitle.textContent = 'Welcome Back';
    } else {
        document.querySelector('[data-tab="register"]').classList.add('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
        modalTitle.textContent = 'Create Account';
    }
}

async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const loginBtn = event.target.querySelector('button[type="submit"]');
    const originalText = loginBtn.innerHTML;
    
    if (!username || !password) {
        showMessage('loginMessage', '⚠️ Please enter your username and password', 'error');
        return;
    }
    
    showLoading(loginBtn);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const userData = {
                user_id: data.user_id,
                username: data.username,
                anonymized_id: data.anonymized_id,
                access_token: data.access_token,
                refresh_token: data.refresh_token,
                login_time: new Date().toISOString()
            };
            
            localStorage.setItem('tuniguard_user', JSON.stringify(userData));
            currentUserId = data.user_id;
            
            closeAuthModal();
            showAppContainer(userData);
            
            // Clear form
            document.getElementById('loginForm').reset();
        } else {
            showMessage('loginMessage', `❌ ${data.error || 'Login failed'}`, 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('loginMessage', `⚠️ ${error.message || 'Connection error. Please check your internet connection.'}`, 'error');
    } finally {
        hideLoading(loginBtn, originalText);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value.trim();
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    const region = document.getElementById('registerRegion').value;
    const carrier = document.getElementById('registerCarrier').value;
    const city = document.getElementById('registerCity').value.trim() || 'Unknown';
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    if (!username || !password || !passwordConfirm || !region || !carrier) {
        showMessage('registerMessage', '⚠️ Please fill in all required fields', 'error');
        return;
    }
    
    if (password !== passwordConfirm) {
        showMessage('registerMessage', '⚠️ Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('registerMessage', '⚠️ Password must be at least 6 characters', 'error');
        return;
    }
    
    showLoading(submitBtn);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password,
                region: region,
                carrier: carrier,
                city: city
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show success message with region and carrier
            showMessage('registerMessage', `✅ Account created!<br>Region: <strong>${data.region}</strong> | Carrier: <strong>${data.carrier}</strong><br>Your ID: <strong>${data.anonymized_id}</strong>`, 'success');
            
            // Switch to login tab and pre-fill username
            setTimeout(() => {
                switchAuthTab('login');
                document.getElementById('loginUsername').value = username;
                document.getElementById('loginPassword').focus();
            }, 1500);
            
            // Clear form
            document.getElementById('registerForm').reset();
        } else {
            showMessage('registerMessage', `❌ ${data.error || 'Registration failed. Please try again.'}`, 'error');
        }
    } catch (error) {
        showMessage('registerMessage', '⚠️ Connection error. Please check your internet and try again.', 'error');
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

function continueAsGuest() {
    const guestData = {
        user_id: 'guest',
        is_guest: true,
        login_time: new Date().toISOString()
    };
    
    localStorage.setItem('tuniguard_user', JSON.stringify(guestData));
    currentUserId = 'guest';
    
    closeAuthModal();
    showAppContainer(guestData);
}

function showAppContainer(user) {
    try {
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('appContainer').style.display = 'block';
        
        // Update navigation with user info
        const userInfo = document.getElementById('userInfo');
        const userName = document.getElementById('userName');
        const userIdDisplay = document.getElementById('userId');
        const userAvatar = document.querySelector('.user-avatar');
        
        if (user.is_guest) {
            userName.textContent = 'Guest User';
            userIdDisplay.textContent = 'Guest Mode';
            userAvatar.textContent = 'G';
        } else {
            userName.textContent = user.full_name || user.username || `User ${user.user_id}`;
            userIdDisplay.textContent = user.username ? `@${user.username}` : `ID: ${user.user_id}`;
            userAvatar.textContent = (user.full_name || user.username || 'U').charAt(0).toUpperCase();
        }
        
        userInfo.style.display = 'flex';
        
        // Load threats catalog
        try {
            loadThreats();
        } catch (e) {
            console.warn('Could not load threats:', e);
        }
        
        // Load chat history
        try {
            loadChatHistory();
        } catch (e) {
            console.warn('Could not load chat history:', e);
        }
    } catch (error) {
        console.error('Error in showAppContainer:', error);
    }
}

async function handleLogout() {
    try {
        const userData = JSON.parse(localStorage.getItem('tuniguard_user') || '{}');
        const accessToken = userData.access_token;
        
        // Call backend logout endpoint with JWT
        if (accessToken) {
            await fetch(`${API_BASE_URL}/api/logout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                }
            });
        }
    } catch (error) {
        console.log('Logout API call failed:', error);
    } finally {
        // Clear local storage
        localStorage.removeItem('tuniguard_user');
        currentUserId = null;
        
        document.getElementById('welcomeScreen').style.display = 'flex';
        document.getElementById('appContainer').style.display = 'none';
        
        // Reset forms
        document.getElementById('loginForm').reset();
        document.getElementById('registerForm').reset();
        
        window.scrollTo(0, 0);
    }
}

// ===================================
// Account Management Functions
// ===================================

function openAccountSettings() {
    document.getElementById('accountSettingsModal').classList.add('active');
}

function closeAccountSettings() {
    document.getElementById('accountSettingsModal').classList.remove('active');
}

async function handleChangePassword(event) {
    event.preventDefault();
    
    const oldPassword = document.getElementById('oldPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const changeBtn = event.target.querySelector('button[type="submit"]');
    const originalText = changeBtn.innerHTML;
    
    if (!oldPassword || !newPassword || !confirmPassword) {
        showMessage('changePasswordMessage', '⚠️ Please fill in all fields', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showMessage('changePasswordMessage', '⚠️ New passwords do not match', 'error');
        return;
    }
    
    if (newPassword.length < 6) {
        showMessage('changePasswordMessage', '⚠️ New password must be at least 6 characters', 'error');
        return;
    }
    
    showLoading(changeBtn);
    
    try {
        const userData = JSON.parse(localStorage.getItem('tuniguard_user') || '{}');
        const response = await fetch(`${API_BASE_URL}/api/user/${currentUserId}/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userData.access_token}`
            },
            body: JSON.stringify({
                old_password: oldPassword,
                password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('changePasswordMessage', '✅ Password changed successfully!', 'success');
            document.getElementById('changePasswordForm').reset();
            setTimeout(() => {
                closeAccountSettings();
            }, 1500);
        } else {
            showMessage('changePasswordMessage', `❌ ${data.error || 'Failed to change password'}`, 'error');
        }
    } catch (error) {
        showMessage('changePasswordMessage', `❌ Error: ${error.message}`, 'error');
    } finally {
        changeBtn.innerHTML = originalText;
    }
}

async function handleDeleteAccount() {
    const password = prompt('Enter your password to confirm account deletion (This cannot be undone):');
    
    if (!password) {
        return;
    }
    
    if (!confirm('⚠️ Are you absolutely sure? This will permanently delete your account and all data!')) {
        return;
    }
    
    try {
        const userData = JSON.parse(localStorage.getItem('tuniguard_user') || '{}');
        const response = await fetch(`${API_BASE_URL}/api/user/${currentUserId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userData.access_token}`
            },
            body: JSON.stringify({ password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✅ Account deleted successfully');
            handleLogout();
        } else {
            alert(`❌ ${data.error || 'Failed to delete account'}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
}

// ===================================
// Utility Functions
// ===================================

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${sectionId}`) {
                link.classList.add('active');
            }
        });
    }
}

function showMessage(elementId, message, type = 'success') {
    const element = document.getElementById(elementId);
    element.className = `result-message ${type}`;
    element.innerHTML = message;
    element.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

function showLoading(buttonElement) {
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<span class="loading"></span> Processing...';
}

function hideLoading(buttonElement, originalText) {
    buttonElement.disabled = false;
    buttonElement.innerHTML = originalText;
}

// ===================================
// Threat Scanning
// ===================================

document.getElementById('scanForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentUserId || currentUserId === 'guest') {
        showMessage('scanResult', `
            <p class="error"><i class="fas fa-exclamation-circle"></i> ⚠️ Please login or register to scan messages. Guest mode cannot use this feature.</p>
        `, 'error');
        return;
    }
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    showLoading(submitBtn);
    
    const scanData = {
        user_id: currentUserId,
        content: document.getElementById('messageContent').value,
        content_type: document.getElementById('contentType').value,
        location_hint: "Tunisia"
    };
    
    try {
        const userData = JSON.parse(localStorage.getItem('tuniguard_user') || '{}');
        const response = await fetch(`${API_BASE_URL}/api/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userData.access_token}`
            },
            body: JSON.stringify(scanData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentScanId = data.scan_id;
            displayScanResult(data);
            
            // Scroll to result
            setTimeout(() => {
                document.getElementById('scanResult').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);
        } else {
            showMessage('scanResult', `
                <h4><i class="fas fa-exclamation-circle"></i> ❌ Scan Failed</h4>
                <p>${data.error || 'Please try again'}</p>
            `, 'error');
        }
    } catch (error) {
        showMessage('scanResult', `
            <h4><i class="fas fa-exclamation-triangle"></i> ⚠️ Connection Error</h4>
            <p>Could not connect to server. Please ensure you have an internet connection.</p>
        `, 'error');
    } finally {
        hideLoading(submitBtn, originalBtnText);
    }
});

function displayScanResult(scan) {
    const resultDiv = document.getElementById('scanResult');
    const isThreat = scan.threat_detected;
    const threatClass = isThreat ? 'threat-detected' : 'threat-safe';
    const scoreClass = scan.detection_score >= 70 ? 'high' : 'low';
    const icon = isThreat ? 'fa-shield-virus' : 'fa-shield-alt';
    
    resultDiv.className = `threat-result ${threatClass}`;
    resultDiv.innerHTML = `
        <h3>
            <i class="fas ${icon}"></i>
            ${isThreat ? '⚠️ THREAT DETECTED!' : '✅ MESSAGE IS SAFE'}
        </h3>
        
        <div class="threat-score ${scoreClass}">
            ${scan.detection_score}/100
            <div style="font-size: 1rem; font-weight: normal;">Threat Confidence Score</div>
        </div>
        
        <div style="text-align: center; margin: 1rem 0;">
            <span class="severity-badge severity-${scan.severity.toLowerCase()}">
                ${scan.severity} Severity
            </span>
        </div>
        
        <div class="threat-details">
            ${scan.threat_type !== 'None' ? `
                <h4><i class="fas fa-bug"></i> Threat Type</h4>
                <p><strong>${scan.threat_type}</strong></p>
            ` : ''}
            
            <h4><i class="fas fa-info-circle"></i> Analysis</h4>
            <p>${scan.explanation}</p>
            
            ${scan.red_flags && scan.red_flags.length > 0 ? `
                <h4><i class="fas fa-flag"></i> Red Flags Detected</h4>
                <ul>
                    ${scan.red_flags.map(flag => `<li>${flag}</li>`).join('')}
                </ul>
            ` : ''}
            
            <h4><i class="fas fa-shield-alt"></i> Recommended Actions</h4>
            <p>${scan.advice}</p>
            
            <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px solid rgba(0,0,0,0.1);">
                <p><small>
                    <i class="fas fa-clock"></i> Scanned at: ${new Date(scan.timestamp).toLocaleString()}
                    <br>
                    <i class="fas fa-id-badge"></i> Scan ID: ${scan.scan_id}
                </small></p>
            </div>
        </div>
    `;
    
    resultDiv.style.display = 'block';
}

// ===================================
// AI Chatbot
// ===================================

let chatHistory = [];

// Load chat history on page load
function loadChatHistory() {
    const savedHistory = localStorage.getItem(`chat_history_${currentUserId}`);
    if (savedHistory) {
        chatHistory = JSON.parse(savedHistory);
        chatHistory.forEach(msg => {
            addChatMessage(msg.text, msg.sender, false);
        });
    }
}

// Save chat history
function saveChatHistory() {
    if (currentUserId && currentUserId !== 'guest') {
        localStorage.setItem(`chat_history_${currentUserId}`, JSON.stringify(chatHistory));
    }
}

document.getElementById('chatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentUserId || currentUserId === 'guest') {
        addChatMessage('⚠️ Please login or register to use the chat feature. Guest mode has limited access.', 'bot');
        return;
    }
    
    const messageInput = document.getElementById('chatInput');
    const userMessage = messageInput.value.trim();
    
    if (!userMessage) return;
    
    // Add user message to chat
    addChatMessage(userMessage, 'user');
    messageInput.value = '';
    
    // Show typing indicator
    const typingId = addChatMessage('Typing...', 'bot-typing');
    
    try {
        const chatData = {
            user_id: currentUserId,
            message: userMessage
        };
        
        // Include scan context if available
        if (currentScanId) {
            chatData.scan_id = currentScanId;
        }
        
        const userData = JSON.parse(localStorage.getItem('tuniguard_user') || '{}');
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userData.access_token}`
            },
            body: JSON.stringify(chatData)
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        document.getElementById(typingId).remove();
        
        if (response.ok) {
            addChatMessage(data.response, 'bot');
        } else {
            addChatMessage('❌ ' + (data.error || 'Sorry, I encountered an error. Please try again.'), 'bot');
        }
    } catch (error) {
        document.getElementById(typingId).remove();
        addChatMessage('⚠️ Connection error. Please check your internet connection.', 'bot');
    }
});

function addChatMessage(text, sender, saveToHistory = true) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const isTyping = sender === 'bot-typing';
    const displaySender = sender === 'bot-typing' ? 'bot' : sender;
    
    const messageHTML = `
        <div class="chat-message ${displaySender}${isTyping ? ' typing' : ''}" id="${messageId}">
            <div class="message-avatar">
                <i class="fas ${displaySender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${isTyping ? '<div class="typing-dots"><span></span><span></span><span></span></div>' : `<p>${text}</p>`}
                </div>
                ${!isTyping ? `<span class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>` : ''}
            </div>
        </div>
    `;
    
    messagesDiv.insertAdjacentHTML('beforeend', messageHTML);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Save to history (except typing indicators)
    if (saveToHistory && !isTyping && sender !== 'bot-typing') {
        chatHistory.push({ text, sender, timestamp: new Date().toISOString() });
        saveChatHistory();
    }
    
    return messageId;
}

// ===================================
// Threat Catalog
// ===================================

async function loadThreats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/threats`);
        const data = await response.json();
        
        if (response.ok && data.threats) {
            displayThreats(data.threats);
        }
    } catch (error) {
        console.error('Error loading threats:', error);
    }
}

function displayThreats(threats) {
    const threatsGrid = document.getElementById('threatsList');
    
    if (!threatsGrid) return;
    
    threatsGrid.innerHTML = threats.map(threat => `
        <div class="threat-card">
            <h3>
                <i class="fas fa-exclamation-triangle"></i>
                ${threat.type}
            </h3>
            <span class="threat-category">${threat.category}</span>
            <span class="severity-badge severity-${threat.severity.toLowerCase()}">${threat.severity}</span>
            <p>${threat.description}</p>
        </div>
    `).join('');
}

// ===================================
// Analytics Dashboard
// ===================================

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/analytics/national`);
        
        if (!response.ok) {
            console.error('Analytics endpoint error:', response.status);
            return;
        }
        
        const data = await response.json();
        console.log('Analytics data:', data);
        
        // Data comes directly, not wrapped in statistics
        displayNationalStats(data);
    } catch (error) {
        console.error('Error loading analytics:', error);
        // Don't show error to user, just log it
    }
}

function displayNationalStats(stats) {
    // Update hero stats
    document.getElementById('totalUsers').textContent = stats.total_scans || 0;
    document.getElementById('totalThreats').textContent = stats.threats_detected || 0;
    
    // Update national stats section
    document.getElementById('nationalScans').textContent = stats.total_scans || 0;
    document.getElementById('nationalDetected').textContent = stats.threats_detected || 0;
    document.getElementById('nationalRate').textContent = `${stats.threat_percentage || 0}%`;
    document.getElementById('national24h').textContent = stats.total_scans || 0;
    
    // Display most common threats (threat types, not content types)
    const commonThreatsDiv = document.getElementById('commonThreats');
    if (stats.most_common_threats && stats.most_common_threats.length > 0) {
        commonThreatsDiv.innerHTML = stats.most_common_threats.map(threat => `
            <div class="common-threat-item">
                <span class="common-threat-name">${threat.threat_type}</span>
                <span class="common-threat-count">${threat.count} detected</span>
            </div>
        `).join('');
    } else {
        commonThreatsDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #666;">
                <i class="fas fa-chart-line" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                <p>No threat data available yet</p>
                <p style="font-size: 0.9rem;">Start scanning messages to see threat statistics</p>
            </div>
        `;
    }
}

// ===================================
// Navigation
// ===================================

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        link.classList.add('active');
        
        // Scroll to section
        const sectionId = link.getAttribute('href').substring(1);
        scrollToSection(sectionId);
    });
});

// ===================================
// Page Load Initialization
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('TuniGuard Frontend Loaded');
    
    // Always load analytics for public stats (hero section)
    loadAnalytics();
    setInterval(loadAnalytics, 30000);
    
    // Check authentication status
    if (checkAuthStatus()) {
        // User is logged in, load data
        loadThreats();
    } else {
        // Show welcome screen
        document.getElementById('welcomeScreen').style.display = 'flex';
        document.getElementById('appContainer').style.display = 'none';
    }
    
    // Attach authentication event listeners
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});

// ===================================
// Example Message Buttons (Optional)
// ===================================

function fillExamplePhishing() {
    document.getElementById('messageContent').value = 
        "مرحبا! لقد ربحت 5000 دينار من Ooredoo. اضغط على الرابط للاستلام: http://fake-ooredoo.com/claim";
}

function fillExampleSafe() {
    document.getElementById('messageContent').value = 
        "Hi mom, I'll be home by 7pm for dinner. Love you!";
}

// Expose functions globally for inline onclick handlers
window.scrollToSection = scrollToSection;
window.fillExamplePhishing = fillExamplePhishing;
window.fillExampleSafe = fillExampleSafe;
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.switchAuthTab = switchAuthTab;
window.continueAsGuest = continueAsGuest;
window.handleLogout = handleLogout;
window.openAccountSettings = openAccountSettings;
window.closeAccountSettings = closeAccountSettings;
window.handleChangePassword = handleChangePassword;
window.handleDeleteAccount = handleDeleteAccount;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
