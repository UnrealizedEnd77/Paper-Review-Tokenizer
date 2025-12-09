    // API Configuration
    const API_BASE_URL = 'http://localhost:8000';

    // Global State
    let currentUser = null;
    let authToken = null;

    // Initialize App
    document.addEventListener('DOMContentLoaded', () => {
        checkAuth();
        setupEventListeners();
    });

    // Check if user is authenticated
    function checkAuth() {
        authToken = localStorage.getItem('authToken');
        if (authToken) {
            fetchCurrentUser();
        } else {
            showScreen('auth-screen');
        }
    }

    // Setup Event Listeners
    function setupEventListeners() {
        document.getElementById('assign-form').addEventListener('submit', handleAssignReviewer);
        // Auth Forms
        document.getElementById('login-form').addEventListener('submit', handleLogin);
        document.getElementById('register-form').addEventListener('submit', handleRegister);
        
        // Upload Form
        document.getElementById('upload-form').addEventListener('submit', handleUploadPaper);
        
        // Review Form
        document.getElementById('review-form').addEventListener('submit', handleSubmitReview);
        
        // Feedback Form
        document.getElementById('feedback-form').addEventListener('submit', handleSubmitFeedback);
        
        // Profile Form
        document.getElementById('profile-form').addEventListener('submit', handleUpdateProfile);
    }

    // Authentication Functions
    function showAuthForm(formType) {
        document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
        
        if (formType === 'login') {
            document.querySelectorAll('.auth-tab')[0].classList.add('active');
            document.getElementById('login-form').classList.add('active');
        } else {
            document.querySelectorAll('.auth-tab')[1].classList.add('active');
            document.getElementById('register-form').classList.add('active');
        }
    }

    async function handleLogin(e) {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const errorDiv = document.getElementById('login-error');
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            if (response.ok) {
                const data = await response.json();
                authToken = data.access_token;
                localStorage.setItem('authToken', authToken);
                await fetchCurrentUser();
                showScreen('dashboard-screen');
            } else {
                const error = await response.json();
                errorDiv.textContent = error.detail || 'Login failed';
            }
        } catch (error) {
            errorDiv.textContent = 'Connection error. Please try again.';
        }
    }

    async function handleRegister(e) {
        e.preventDefault();
        
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const affiliation = document.getElementById('register-affiliation').value;
        const role = document.getElementById('register-role').value;
        const password = document.getElementById('register-password').value;
        const errorDiv = document.getElementById('register-error');
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, affiliation, role, password })
            });
            
            if (response.ok) {
                errorDiv.className = 'message success';
                errorDiv.textContent = 'Registration successful! Please login.';
                setTimeout(() => showAuthForm('login'), 2000);
            } else {
                const error = await response.json();
                errorDiv.className = 'error-message';
                errorDiv.textContent = error.detail || 'Registration failed';
            }
        } catch (error) {
            errorDiv.className = 'error-message';
            errorDiv.textContent = 'Connection error. Please try again.';
        }
    }

    async function fetchCurrentUser() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            if (response.ok) {
                currentUser = await response.json();
                updateUserUI();
                loadDashboard();
            } else {
                logout();
            }
        } catch (error) {
            console.error('Failed to fetch user:', error);
            logout();
        }
    }

    function logout() {
        localStorage.removeItem('authToken');
        authToken = null;
        currentUser = null;
        showScreen('auth-screen');
    }

    // UI Functions
    function showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => screen.classList.remove('active'));
        document.getElementById(screenId).classList.add('active');
    }

    function showSection(sectionName) {
        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
        
        document.getElementById(`nav-${sectionName}`).classList.add('active');
        document.getElementById(`section-${sectionName}`).classList.add('active');
        
        // Load section-specific data
        switch(sectionName) {
            case 'home':
                loadDashboard();
                break;
            case 'papers':
                loadPapers();
                break;
            case 'reviews':
                loadReviews();
                break;
            case 'tokens':
                loadTokens();
                break;
            case 'leaderboard':
                loadLeaderboard();
                break;
            case 'profile':
                loadProfile();
                break;
        }
    }

    function updateUserUI() {
        document.getElementById('user-name').textContent = currentUser.name;
        document.getElementById('welcome-name').textContent = currentUser.name;
        
        const roleBadge = document.getElementById('user-role');
        roleBadge.textContent = currentUser.role.toUpperCase();
        roleBadge.className = `badge ${currentUser.role}`;
        
        // Hide/show upload button based on role
        const uploadBtn = document.getElementById('upload-paper-btn');
        if (currentUser.role === 'author') {
            uploadBtn.style.display = 'block';
        } else {
            uploadBtn.style.display = 'none';
        }
    }

    // Dashboard Functions
    async function loadDashboard() {
        try {
            // Load stats based on role
            const statsGrid = document.getElementById('stats-grid');
            const quickActions = document.getElementById('quick-actions');
            
            if (currentUser.role === 'author') {
                await loadAuthorDashboard(statsGrid, quickActions);
            } else if (currentUser.role === 'reviewer') {
                await loadReviewerDashboard(statsGrid, quickActions);
            }
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        }
    }

    async function loadAuthorDashboard(statsGrid, quickActions) {
        // Fetch author's papers
        const papers = await fetchAPI('/papers');
        
        const pending = papers.filter(p => p.status === 'pending').length;
        const underReview = papers.filter(p => p.status === 'under_review').length;
        const reviewed = papers.filter(p => p.status === 'reviewed').length;
        
        statsGrid.innerHTML = `
            <div class="stat-card primary">
                <div class="stat-icon">📄</div>
                <div class="stat-value">${papers.length}</div>
                <div class="stat-label">Total Papers</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-icon">⏳</div>
                <div class="stat-value">${pending}</div>
                <div class="stat-label">Pending</div>
            </div>
            <div class="stat-card info">
                <div class="stat-icon">🔍</div>
                <div class="stat-value">${underReview}</div>
                <div class="stat-label">Under Review</div>
            </div>
            <div class="stat-card success">
                <div class="stat-icon">✅</div>
                <div class="stat-value">${reviewed}</div>
                <div class="stat-label">Reviewed</div>
            </div>
        `;
        
        quickActions.innerHTML = `
            <div class="quick-action-card" onclick="showUploadModal()">
                <div class="quick-action-icon">📤</div>
                <div class="quick-action-title">Upload Paper</div>
                <div class="quick-action-desc">Submit a new research paper for review</div>
            </div>
            <div class="quick-action-card" onclick="showSection('papers')">
                <div class="quick-action-icon">📋</div>
                <div class="quick-action-title">View Papers</div>
                <div class="quick-action-desc">Check status of your submissions</div>
            </div>
            <div class="quick-action-card" onclick="showSection('reviews')">
                <div class="quick-action-icon">💬</div>
                <div class="quick-action-title">View Reviews</div>
                <div class="quick-action-desc">Read reviews on your papers</div>
            </div>
        `;
    }

    async function loadReviewerDashboard(statsGrid, quickActions) {
        // Fetch reviewer stats
        const assignments = await fetchAPI('/assignments');
        const reviews = await fetchAPI(`/reviews?reviewer_id=${currentUser.id}`);
        const tokens = await fetchAPI(`/users/${currentUser.id}/tokens`);
        
        const pending = assignments.filter(a => a.status === 'assigned').length;
        
        statsGrid.innerHTML = `
            <div class="stat-card primary">
                <div class="stat-icon">📝</div>
                <div class="stat-value">${reviews.length}</div>
                <div class="stat-label">Total Reviews</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-icon">⏰</div>
                <div class="stat-value">${pending}</div>
                <div class="stat-label">Pending Reviews</div>
            </div>
            <div class="stat-card success">
                <div class="stat-icon">🏆</div>
                <div class="stat-value">${tokens.length}</div>
                <div class="stat-label">Tokens Earned</div>
            </div>
            <div class="stat-card info">
                <div class="stat-icon">📊</div>
                <div class="stat-value">${assignments.length}</div>
                <div class="stat-label">Total Assignments</div>
            </div>
        `;
        
        quickActions.innerHTML = `
            <div class="quick-action-card" onclick="showSection('reviews')">
                <div class="quick-action-icon">✍️</div>
                <div class="quick-action-title">Submit Review</div>
                <div class="quick-action-desc">Review assigned papers</div>
            </div>
            <div class="quick-action-card" onclick="showSection('tokens')">
                <div class="quick-action-icon">🎖️</div>
                <div class="quick-action-title">My Achievements</div>
                <div class="quick-action-desc">View earned tokens and badges</div>
            </div>
            <div class="quick-action-card" onclick="showSection('leaderboard')">
                <div class="quick-action-icon">🥇</div>
                <div class="quick-action-title">Leaderboard</div>
                <div class="quick-action-desc">Check your ranking</div>
            </div>
        `;
    }

async function loadPapers() {
    try {
        const papers = await fetchAPI('/papers');
        const papersList = document.getElementById('papers-list');
        
        if (papers.length === 0) {
            papersList.innerHTML = '<p>No papers found. Upload your first paper!</p>';
            return;
        }
        
        papersList.innerHTML = papers.map(paper => `
            <div class="paper-card">
                <div class="paper-title">${paper.title}</div>
                <div class="paper-abstract">${paper.abstract || 'No abstract provided'}</div>
                <div class="paper-meta">
                    <span class="paper-status ${paper.status}">${paper.status.replace('_', ' ').toUpperCase()}</span>
                    ${paper.category ? `<span class="paper-tag">${paper.category}</span>` : ''}
                    ${paper.domain ? `<span class="paper-tag">${paper.domain}</span>` : ''}
                </div>
                <div class="paper-actions">
                    <button class="btn btn-info btn-small" onclick="downloadPaper(${paper.id})">📥 Download</button>
                    ${currentUser.role === 'author' && currentUser.id === paper.author_id ? 
                        `<button class="btn btn-warning btn-small" onclick="showAssignModal(${paper.id})">👥 Assign Reviewer</button>
                         <button class="btn btn-primary btn-small" onclick="viewPaperReviews(${paper.id})">📖 View Reviews</button>` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load papers:', error);
    }
}

    async function downloadPaper(paperId) {
        try {
            const response = await fetch(`${API_BASE_URL}/papers/${paperId}/download`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'paper.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                alert('Failed to download paper');
            }
        } catch (error) {
            console.error('Download error:', error);
            alert('Failed to download paper');
        }
    }

    // Reviews Functions
    async function loadReviews() {
        const container = document.getElementById('reviews-container');
        
        try {
            if (currentUser.role === 'author') {
                await loadAuthorReviews(container);
            } else if (currentUser.role === 'reviewer') {
                await loadReviewerAssignments(container);
            }
        } catch (error) {
            console.error('Failed to load reviews:', error);
        }
    }

    async function loadAuthorReviews(container) {
        const papers = await fetchAPI('/papers');
        
        let html = '<h2>Reviews on Your Papers</h2>';
        
        for (const paper of papers) {
            const reviews = await fetchAPI(`/reviews?paper_id=${paper.id}`);
            
            if (reviews.length > 0) {
                html += `
                    <div class="paper-section">
                        <h3>${paper.title}</h3>
                        ${reviews.map(review => `
                            <div class="review-card">
                                <div class="review-header">
                                    <div>
                                        <strong>Review #${review.id}</strong>
                                        ${review.rating ? `<div class="review-rating">${'⭐'.repeat(Math.floor(review.rating))}</div>` : ''}
                                    </div>
                                    ${!review.author_feedback_rating ? `
                                        <button class="btn btn-warning btn-small" onclick="showFeedbackModal(${review.id})">
                                            Rate Review
                                        </button>
                                    ` : `<div>Your Rating: ${'⭐'.repeat(Math.floor(review.author_feedback_rating))}</div>`}
                                </div>
                                <div class="review-text">${review.review_text}</div>
                                <div class="review-meta">
                                    <span>📅 ${new Date(review.timestamp).toLocaleDateString()}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        }
        
        if (papers.filter(p => p.status !== 'pending').length === 0) {
            html += '<p>No reviews yet. Your papers are being reviewed.</p>';
        }
        
        container.innerHTML = html;
    }

    async function loadReviewerAssignments(container) {
        const assignments = await fetchAPI('/assignments');
        const myReviews = await fetchAPI(`/reviews?reviewer_id=${currentUser.id}`);
        
        const reviewedPaperIds = new Set(myReviews.map(r => r.paper_id));
        const pendingAssignments = assignments.filter(a => !reviewedPaperIds.has(a.paper_id));
        
        let html = '<h2>Assigned Papers</h2>';
        
        if (pendingAssignments.length === 0) {
            html += '<p>No pending assignments. Great job!</p>';
        } else {
            for (const assignment of pendingAssignments) {
                const paper = await fetchAPI(`/papers/${assignment.paper_id}`);
                html += `
                    <div class="paper-card">
                        <div class="paper-title">${paper.title}</div>
                        <div class="paper-abstract">${paper.abstract || 'No abstract provided'}</div>
                        <div class="paper-meta">
                            ${assignment.deadline ? `<span class="paper-tag">⏰ Due: ${new Date(assignment.deadline).toLocaleDateString()}</span>` : ''}
                        </div>
                        <div class="paper-actions">
                            <button class="btn btn-info btn-small" onclick="downloadPaper(${paper.id})">📥 Download</button>
                            <button class="btn btn-success btn-small" onclick="showReviewModal(${paper.id})">✍️ Submit Review</button>
                        </div>
                    </div>
                `;
            }
        }
        
        html += '<h2 style="margin-top: 40px;">My Submitted Reviews</h2>';
        
        if (myReviews.length === 0) {
            html += '<p>No reviews submitted yet.</p>';
        } else {
            html += myReviews.map(review => `
                <div class="review-card">
                    <div class="review-header">
                        <div>
                            <strong>Review #${review.id}</strong> - Paper #${review.paper_id}
                            ${review.rating ? `<div class="review-rating">${'⭐'.repeat(Math.floor(review.rating))}</div>` : ''}
                        </div>
                        ${review.author_feedback_rating ? 
                            `<div>Author Rating: ${'⭐'.repeat(Math.floor(review.author_feedback_rating))}</div>` : 
                            '<span class="paper-tag">Awaiting feedback</span>'}
                    </div>
                    <div class="review-text">${review.review_text}</div>
                    <div class="review-meta">
                        <span>📅 ${new Date(review.timestamp).toLocaleDateString()}</span>
                    </div>
                </div>
            `).join('');
        }
        
        container.innerHTML = html;
    }

    // Tokens Functions
    async function loadTokens() {
        try {
            const userTokens = await fetchAPI(`/users/${currentUser.id}/tokens`);
            const allTokens = await fetchAPI('/achievements');
            
            // Load stats
            const statsDiv = document.getElementById('tokens-stats');
            
            let stats = {
                total: userTokens.length,
                badges: userTokens.filter(t => t.token.type === 'badge').length,
                achievements: userTokens.filter(t => t.token.type === 'achievement').length,
                access: userTokens.filter(t => t.token.type === 'access').length
            };
            
            statsDiv.innerHTML = `
                <div class="stat-card primary">
                    <div class="stat-icon">🏆</div>
                    <div class="stat-value">${stats.total}</div>
                    <div class="stat-label">Total Tokens</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-value">${stats.badges}</div>
                    <div class="stat-label">Badges</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-value">${stats.achievements}</div>
                    <div class="stat-label">Achievements</div>
                </div>
                <div class="stat-card info">
                    <div class="stat-icon">🔓</div>
                    <div class="stat-value">${stats.access}</div>
                    <div class="stat-label">Access Tokens</div>
                </div>
            `;
            
            // Load earned tokens
            const tokensList = document.getElementById('tokens-list');
            const earnedTokenIds = new Set(userTokens.map(t => t.token_id));
            
            tokensList.innerHTML = allTokens.map(token => {
                const userToken = userTokens.find(ut => ut.token_id === token.id);
                const earned = earnedTokenIds.has(token.id);
                
                return `
                    <div class="token-card ${token.type}" style="opacity: ${earned ? '1' : '0.4'}">
                        <div class="token-icon">${token.icon}</div>
                        <div class="token-name">${token.name}</div>
                        <div class="token-description">${token.description}</div>
                        <div class="token-earned">
                            ${earned ? 
                                `✅ Earned on ${new Date(userToken.earned_at).toLocaleDateString()}` : 
                                `🔒 ${token.criteria}`}
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Failed to load tokens:', error);
        }
    }

    // Leaderboard Functions
    async function loadLeaderboard() {
        try {
            const leaderboard = await fetchAPI('/leaderboard');
            const tbody = document.getElementById('leaderboard-body');
            
            tbody.innerHTML = leaderboard.map((entry, index) => {
                const rank = index + 1;
                let rankClass = '';
                if (rank === 1) rankClass = 'top1';
                else if (rank === 2) rankClass = 'top2';
                else if (rank === 3) rankClass = 'top3';
                
                const isCurrentUser = entry.user_id === currentUser.id;
                
                return `
                    <tr style="${isCurrentUser ? 'background: rgba(99, 102, 241, 0.2); font-weight: bold;' : ''}">
                        <td><span class="rank ${rankClass}">#${rank}</span></td>
                        <td>${entry.name}${isCurrentUser ? ' (You)' : ''}</td>
                        <td>${entry.total_reviews}</td>
                        <td>${entry.total_tokens}</td>
                        <td>${entry.ranking_score.toFixed(1)}</td>
                        <td><span class="level-badge ${entry.level}">${entry.level.toUpperCase()}</span></td>
                    </tr>
                `;
            }).join('');
        } catch (error) {
            console.error('Failed to load leaderboard:', error);
        }
    }

    // Profile Functions
    async function loadProfile() {
        document.getElementById('profile-name').value = currentUser.name;
        document.getElementById('profile-email').value = currentUser.email;
        document.getElementById('profile-affiliation').value = currentUser.affiliation || '';
        document.getElementById('profile-role').value = currentUser.role;
        document.getElementById('profile-bio').value = currentUser.bio || '';
        document.getElementById('profile-expertise').value = currentUser.expertise || '';
        document.getElementById('profile-interests').value = currentUser.interests || '';
    }

    async function handleUpdateProfile(e) {
        e.preventDefault();
        
        const bio = document.getElementById('profile-bio').value;
        const expertise = document.getElementById('profile-expertise').value;
        const interests = document.getElementById('profile-interests').value;
        const messageDiv = document.getElementById('profile-message');
        
        try {
            const response = await fetch(`${API_BASE_URL}/users/${currentUser.id}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ bio, expertise, interests })
            });
            
            if (response.ok) {
                currentUser = await response.json();
                messageDiv.className = 'message success';
                messageDiv.textContent = 'Profile updated successfully!';
            } else {
                messageDiv.className = 'message error';
                messageDiv.textContent = 'Failed to update profile';
            }
        } catch (error) {
            messageDiv.className = 'message error';
            messageDiv.textContent = 'Connection error';
        }
    }

    // Modal Functions
    function showUploadModal() {
        document.getElementById('upload-modal').classList.add('active');
    }

    function closeUploadModal() {
        document.getElementById('upload-modal').classList.remove('active');
        document.getElementById('upload-form').reset();
        document.getElementById('upload-message').textContent = '';
    }

    async function handleUploadPaper(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('title', document.getElementById('paper-title').value);
        formData.append('abstract', document.getElementById('paper-abstract').value);
        formData.append('keywords', document.getElementById('paper-keywords').value);
        formData.append('category', document.getElementById('paper-category').value);
        formData.append('domain', document.getElementById('paper-domain').value);
        formData.append('file', document.getElementById('paper-file').files[0]);
        
        const messageDiv = document.getElementById('upload-message');
        
        try {
            const response = await fetch(`${API_BASE_URL}/papers`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${authToken}` },
                body: formData
            });
            
            if (response.ok) {
                messageDiv.className = 'message success';
                messageDiv.textContent = 'Paper uploaded successfully!';
                setTimeout(() => {
                    closeUploadModal();
                    loadPapers();
                    loadDashboard();
                }, 2000);
            } else {
                const error = await response.json();
                messageDiv.className = 'message error';
                messageDiv.textContent = error.detail || 'Upload failed';
            }
        } catch (error) {
            messageDiv.className = 'message error';
            messageDiv.textContent = 'Connection error';
        }
    }

    function showReviewModal(paperId) {
        document.getElementById('review-paper-id').value = paperId;
        document.getElementById('review-modal').classList.add('active');
    }

    function closeReviewModal() {
        document.getElementById('review-modal').classList.remove('active');
        document.getElementById('review-form').reset();
        document.getElementById('review-message').textContent = '';
    }

    async function handleSubmitReview(e) {
        e.preventDefault();
        
        const paperId = parseInt(document.getElementById('review-paper-id').value);
        const reviewText = document.getElementById('review-text').value;
        const rating = parseFloat(document.getElementById('review-rating').value) || null;
        const messageDiv = document.getElementById('review-message');
        
        try {
            const response = await fetch(`${API_BASE_URL}/reviews`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    paper_id: paperId,
                    review_text: reviewText,
                    rating: rating
                })
            });
            
            if (response.ok) {
                messageDiv.className = 'message success';
                messageDiv.textContent = 'Review submitted successfully! 🎉';
                setTimeout(() => {
                    closeReviewModal();
                    loadReviews();
                    loadDashboard();
                    loadTokens();
                }, 2000);
            } else {
                const error = await response.json();
                messageDiv.className = 'message error';
                messageDiv.textContent = error.detail || 'Submission failed';
            }
        } catch (error) {
            messageDiv.className = 'message error';
            messageDiv.textContent = 'Connection error';
        }
    }

    function showFeedbackModal(reviewId) {
        document.getElementById('feedback-review-id').value = reviewId;
        document.getElementById('feedback-modal').classList.add('active');
    }

    function closeFeedbackModal() {
        document.getElementById('feedback-modal').classList.remove('active');
        document.getElementById('feedback-form').reset();
        document.getElementById('feedback-message').textContent = '';
    }

    async function handleSubmitFeedback(e) {
        e.preventDefault();
        
        const reviewId = parseInt(document.getElementById('feedback-review-id').value);
        const rating = parseFloat(document.getElementById('feedback-rating').value) || null;
        const text = document.getElementById('feedback-text').value;
        const messageDiv = document.getElementById('feedback-message');
        
        try {
            const response = await fetch(`${API_BASE_URL}/reviews/${reviewId}/feedback`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    author_feedback_rating: rating,
                    author_feedback_text: text
                })
            });
            
            if (response.ok) {
                messageDiv.className = 'message success';
                messageDiv.textContent = 'Feedback submitted successfully!';
                setTimeout(() => {
                    closeFeedbackModal();
                    loadReviews();
                }, 2000);
            } else {
                const error = await response.json();
                messageDiv.className = 'message error';
                messageDiv.textContent = error.detail || 'Submission failed';
            }
        } catch (error) {
            messageDiv.className = 'message error';
            messageDiv.textContent = 'Connection error';
        }
    }

    async function viewPaperReviews(paperId) {
        showSection('reviews');
    }

    // Helper function to fetch from API
    async function fetchAPI(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        return await response.json();
    }

    async function showAssignModal(paperId) {
    document.getElementById('assign-paper-id').value = paperId;
    
    // Load available reviewers
    try {
        const reviewers = await fetchAPI('/reviewers');
        const select = document.getElementById('assign-reviewer-id');
        select.innerHTML = '<option value="">Select a reviewer...</option>' + 
            reviewers.map(r => `<option value="${r.id}">${r.name} (${r.email})</option>`).join('');
        
        document.getElementById('assign-modal').classList.add('active');
    } catch (error) {
        console.error('Failed to load reviewers:', error);
        alert('Failed to load reviewers');
    }
}

function closeAssignModal() {
    document.getElementById('assign-modal').classList.remove('active');
    document.getElementById('assign-form').reset();
    document.getElementById('assign-message').textContent = '';
}

async function handleAssignReviewer(e) {
    e.preventDefault();
    
    const paperId = parseInt(document.getElementById('assign-paper-id').value);
    const reviewerId = parseInt(document.getElementById('assign-reviewer-id').value);
    const messageDiv = document.getElementById('assign-message');
    
    if (!reviewerId) {
        messageDiv.className = 'message error';
        messageDiv.textContent = 'Please select a reviewer';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/papers/${paperId}/assign`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paper_id: paperId,
                reviewer_id: reviewerId
            })
        });
        
        if (response.ok) {
            messageDiv.className = 'message success';
            messageDiv.textContent = 'Reviewer assigned successfully! 🎉';
            setTimeout(() => {
                closeAssignModal();
                loadPapers();
            }, 2000);
        } else {
            const error = await response.json();
            messageDiv.className = 'message error';
            messageDiv.textContent = error.detail || 'Assignment failed';
        }
    } catch (error) {
        messageDiv.className = 'message error';
        messageDiv.textContent = 'Connection error';
    }
}