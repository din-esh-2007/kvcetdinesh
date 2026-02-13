/**
 * Burnout Guardian - Core Application Logic
 */

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    console.log('🧠 Burnout Guardian Dashboard Initializing...');

    // Initialize i18n
    if (window.I18N) {
        const savedLang = localStorage.getItem('language') || 'en';
        window.I18N.setLanguage(savedLang);
    }

    // Initialize Theme
    const savedTheme = localStorage.getItem('theme') || 'premium';
    setTheme(savedTheme);

    // Check Authentication
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    const qAdd = document.getElementById('quickAddBtn');

    if (!token) {
        document.getElementById('login-overlay').classList.add('active');
    } else {
        document.getElementById('login-overlay').classList.remove('active');
        setupNavigation();
        initCharts();

        // Hide Quick Add for Admin
        if (qAdd) {
            qAdd.style.display = role === 'Admin' ? 'none' : 'flex';
        }
    }
});

// Login Logic
async function handleLogin() {
    const username = document.getElementById('login-username').value;
    const key = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');

    errorEl.style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', key);

        const response = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Authorization Failed');

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('role', data.role);
        localStorage.setItem('username', data.username);

        document.getElementById('login-overlay').classList.remove('active');
        setupNavigation();
        initCharts();

        // Hide Quick Add for Admin
        const qAdd = document.getElementById('quickAddBtn');
        if (qAdd) {
            qAdd.style.display = data.role === 'Admin' ? 'none' : 'flex';
        }

        console.log(`🔐 Authorized as: ${data.role}`);
    } catch (err) {
        errorEl.innerText = err.message;
        errorEl.style.display = 'block';
    }
}

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item, .bottom-nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.getAttribute('data-view');
            if (view) {
                switchView(view);
            }
        });
    });

    // Filter Navigation based on role
    const role = localStorage.getItem('role');
    document.querySelectorAll('[data-view="admin"]').forEach(el => {
        el.style.display = role === 'Admin' ? 'flex' : 'none';
    });
    document.querySelectorAll('[data-view="manager"]').forEach(el => {
        el.style.display = (role === 'Admin' || role === 'Manager') ? 'flex' : 'none';
    });

    // Quick Add Button logic
    const addBtn = document.getElementById('quickAddBtn');
    if (addBtn) {
        addBtn.addEventListener('click', () => {
            if (role === 'Manager' || role === 'Admin') {
                switchView('manager');
            } else {
                alert('Only managers can delegate tasks.');
            }
        });
    }

    // Admin Actions Logic
    window.showUserForm = (roleType) => {
        const form = document.getElementById('user-creation-form');
        const actions = document.getElementById('admin-actions');
        const title = document.getElementById('form-title');

        window._pendingRole = roleType;
        title.innerText = `Add New ${roleType}`;

        actions.style.display = 'none';
        form.style.display = 'block';
        window.scrollTo({ top: form.offsetTop - 100, behavior: 'smooth' });
    };

    window.hideUserForm = () => {
        document.getElementById('user-creation-form').style.display = 'none';
        document.getElementById('admin-actions').style.display = 'grid';
    };

    window.submitUserForm = async () => {
        const userData = {
            full_name: document.getElementById('user-fullname').value,
            email: document.getElementById('user-email').value,
            mobile_number: document.getElementById('user-mobile').value,
            gender: document.getElementById('user-gender').value,
            address: document.getElementById('user-address').value,
            dob: document.getElementById('user-dob').value,
            department: document.getElementById('user-department').value,
            employment_type: document.getElementById('user-employment-type').value,
            emergency_contact: document.getElementById('user-emergency').value,
            joining_date: document.getElementById('user-joining').value,
            username: document.getElementById('user-username').value,
            password: document.getElementById('user-password').value,
            role: window._pendingRole
        };

        if (!userData.username || !userData.password || !userData.full_name) {
            alert("Username, Password, and Full Name are required.");
            return;
        }

        console.log("📤 Submitting User Profile:", userData);

        // Mock success for now, in real app call API
        alert(`${userData.role} profile for ${userData.full_name} created successfully!`);
        hideUserForm();
    };

    // Admin Data Loading
    window.loadAdminData = async () => {
        const mgrList = document.getElementById('managerList');
        const directoryBody = document.getElementById('userDirectoryBody');
        if (!mgrList && !directoryBody) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/admin/users', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) return;
            const users = await response.json();
            window._allUsers = users; // Cache for searching

            // 1. Populate Manager List
            const managers = users.filter(u => u.role === 'Manager');
            if (mgrList) {
                if (managers.length === 0) {
                    mgrList.innerHTML = '<p style="font-size: 0.8rem; color: var(--text-muted);">No managers added yet.</p>';
                } else {
                    mgrList.innerHTML = managers.map(m => `
                        <div style="display: flex; justify-content: space-between; padding: 8px; background: rgba(255,255,255,0.05); margin-bottom: 4px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);">
                            <div style="display: flex; flex-direction: column;">
                                <span style="font-size: 0.85rem; font-weight: 600;">${m.full_name}</span>
                                <span style="font-size: 0.7rem; color: var(--accent-cyan);">${m.employee_id} | ${m.email}</span>
                            </div>
                            <button class="btn-small" style="color: var(--error); padding: 4px 8px;" onclick="removeManager('${m.id}')">✕</button>
                        </div>
                    `).join('');
                }
            }

            // 2. Populate User Directory
            renderDirectory(users);

            // 3. Setup Search
            const searchInput = document.getElementById('userDirectorySearch');
            if (searchInput && !searchInput.dataset.listener) {
                searchInput.addEventListener('input', (e) => {
                    const query = e.target.value.toLowerCase();
                    const filtered = window._allUsers.filter(u =>
                        u.full_name.toLowerCase().includes(query) ||
                        u.employee_id.toLowerCase().includes(query) ||
                        u.email.toLowerCase().includes(query)
                    );
                    renderDirectory(filtered);
                });
                searchInput.dataset.listener = "true";
            }

            // 4. Populate Aggregate Stats
            const statsResp = await fetch('/api/monitoring/aggregate-stats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (statsResp.ok) {
                const stats = await statsResp.json();
                updateDashboardStats(stats);
            }

            // 5. Hydrate Charts
            updateCharts();

        } catch (e) {
            console.error("Failed to load admin data:", e);
        }
    };

    function updateDashboardStats(stats) {
        const mapping = {
            'total-assets': stats.total_assets,
            'high-risk-alerts': stats.high_risk_assets,
            'autonomous-interventions': stats.autonomous_interventions,
            'org-stability': stats.org_stability_index
        };

        for (const [id, val] of Object.entries(mapping)) {
            const el = document.getElementById(id);
            if (el) el.innerText = val;
        }
    }

    async function updateCharts() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/monitoring/chart-data', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) return;
            const data = await response.json();

            if (window._charts) {
                // Update Stability Chart
                if (window._charts.stabilityChart) {
                    window._charts.stabilityChart.data.labels = data.stability.map(d => d.date);
                    window._charts.stabilityChart.data.datasets[0].data = data.stability.map(d => d.value);
                    window._charts.stabilityChart.update();
                }

                // Update Risk Chart
                if (window._charts.riskChart) {
                    const levels = ['low', 'moderate', 'high', 'critical'];
                    window._charts.riskChart.data.labels = levels.map(l => l.charAt(0).toUpperCase() + l.slice(1));
                    window._charts.riskChart.data.datasets[0].data = levels.map(l => data.risk[l] || 0);
                    window._charts.riskChart.update();
                }
            }
        } catch (e) {
            console.error("Chart hydration failed:", e);
        }
    }

    function renderDirectory(users) {
        const body = document.getElementById('userDirectoryBody');
        if (!body) return;

        if (users.length === 0) {
            body.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 2rem; color: var(--text-muted);">No assets found matching criteria.</td></tr>';
            return;
        }

        body.innerHTML = users.map(u => `
            <tr>
                <td style="font-weight: 600;">${u.full_name}</td>
                <td><span class="role-badge ${u.role.toLowerCase()}">${u.role}</span></td>
                <td><code>${u.employee_id}</code></td>
                <td style="font-size: 0.8rem; color: var(--text-secondary);">${u.email}</td>
                <td>${u.department_id || 'General'}</td>
                <td><span class="badge ${u.is_active ? 'success' : 'error'}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
            </tr>
        `).join('');
    }

    // Manager Management Action
    window.removeManager = (id) => {
        if (confirm(`Are you sure you want to remove manager ${id}?`)) {
            console.log(`🗑️ Removing Manager: ${id}`);
            // In demo mode, just re-load
            loadAdminData();
        }
    };

    if (role === 'Admin') loadAdminData();
}

function handleLogout() {
    localStorage.clear();
    location.reload();
}


// View Switching Logic
function switchView(viewId) {
    console.log(`🚀 Switching to view: ${viewId}`);

    // Update Active Nav Items
    document.querySelectorAll('.nav-item, .bottom-nav-item').forEach(item => {
        if (item.getAttribute('data-view') === viewId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Toggle View Sections
    document.querySelectorAll('.view-section').forEach(view => {
        view.classList.remove('active');
    });

    const targetView = document.getElementById(`view-${viewId}`);
    if (targetView) {
        targetView.classList.add('active');
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Load specific data
        if (viewId === 'admin') {
            if (window.loadAdminData) window.loadAdminData();
        }
    }
}

// Theme Management
function setTheme(theme) {
    document.body.className = `theme-${theme}`;
    localStorage.setItem('theme', theme);

    // Update theme toggle buttons in settings if they exist
    document.querySelectorAll('.theme-btn').forEach(btn => {
        if (btn.classList.contains(theme)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Chart Storage
window._charts = {};

// Chart Initialization
function initCharts() {
    console.log("📊 Initializing Charts...");

    const chartConfigs = [
        { id: 'stabilityChart', type: 'line', color: '#00ccff', label: 'Org Stability' },
        { id: 'riskChart', type: 'bar', color: '#ff3366', label: 'Risk Intensity' },
        { id: 'forecastChart', type: 'line', color: '#00ffaa', label: 'Forecast' },
        { id: 'emotionChart', type: 'line', color: '#cc99ff', label: 'Sentiment' }
    ];

    chartConfigs.forEach(conf => {
        const ctx = document.getElementById(conf.id);
        if (ctx) {
            window._charts[conf.id] = new Chart(ctx, {
                type: conf.type,
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: conf.label,
                        data: [0, 0, 0, 0, 0, 0, 0],
                        borderColor: conf.color,
                        backgroundColor: conf.color + '33',
                        fill: conf.type === 'line',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }
    });

    // If already admin, trigger hydration
    const role = localStorage.getItem('role');
    if (role === 'Admin' && window.loadAdminData) {
        // Data will be loaded when switchView is called or on direct access
    }
}
