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

    // Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }
});

// Sidebar Global Controls
window.expandSidebar = () => {
    const sidebar = document.getElementById('mainSidebar');
    if (sidebar) sidebar.classList.remove('collapsed');
};

window.collapseSidebar = () => {
    const sidebar = document.getElementById('mainSidebar');
    if (sidebar) sidebar.classList.add('collapsed');
};

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

        if (window.lucide) {
            lucide.createIcons();
        }

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

    // Admin Only: Admin Control, Manager Directory
    document.querySelectorAll('[data-view="admin"], [data-view="managers"]').forEach(el => {
        el.style.display = role === 'Admin' ? 'flex' : 'none';
    });

    // Manager & Admin: Manager Specific View, Employee Directory
    document.querySelectorAll('[data-view="manager"], [data-view="employees"]').forEach(el => {
        el.style.display = (role === 'Admin' || role === 'Manager') ? 'flex' : 'none';
    });

    // Dynamic Branding
    const brandEl = document.getElementById('branding-text');
    if (brandEl) {
        if (role === 'Admin') brandEl.innerText = 'Admin';
        else if (role === 'Manager') brandEl.innerText = 'Manager';
        else brandEl.innerText = 'Guardian';
    }

    // Intelligent Initial View Routing
    if (role === 'Admin') {
        switchView('admin');
    } else if (role === 'Manager') {
        switchView('manager');
    } else {
        switchView('dashboard');
    }

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
        const modal = document.getElementById('user-modal');
        const title = document.getElementById('form-title');
        const submitBtn = document.getElementById('submit-user-btn');

        window._pendingRole = roleType;
        title.innerText = `Deploy New ${roleType}`;
        submitBtn.innerText = "Commit Profile";
        document.getElementById('editing-user-id').value = ""; // Reset

        // Reset fields
        document.querySelectorAll('#user-modal input, #user-modal textarea').forEach(i => {
            if (i.id !== 'user-password') i.value = "";
        });
        document.getElementById('user-password').value = "";

        modal.classList.add('active');
    };

    window.hideUserForm = () => {
        document.getElementById('user-modal').classList.remove('active');
    };

    window.submitUserForm = async () => {
        const editId = document.getElementById('editing-user-id').value;
        const userData = {
            full_name: document.getElementById('user-fullname').value,
            email: document.getElementById('user-email').value,
            mobile_number: document.getElementById('user-mobile').value,
            gender: document.getElementById('user-gender').value,
            address: document.getElementById('user-address').value,
            dob: document.getElementById('user-dob').value ? new Date(document.getElementById('user-dob').value).toISOString() : null,
            department_id: document.getElementById('user-department').value,
            employment_type: document.getElementById('user-employment-type').value,
            emergency_contact: document.getElementById('user-emergency').value,
            joining_date: document.getElementById('user-joining').value ? new Date(document.getElementById('user-joining').value).toISOString() : null,
            employee_id: document.getElementById('user-employee-id').value,
            username: document.getElementById('user-username').value,
            password: document.getElementById('user-password').value,
            role: window._pendingRole || 'Employee'
        };

        if (!userData.username || !userData.full_name) {
            alert("Username and Full Name are required.");
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const method = editId ? 'PUT' : 'POST';
            const url = editId ? `/api/admin/users/${editId}` : '/api/admin/users';

            console.log(`📤 ${method} User Profile:`, userData);

            const res = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(userData)
            });

            if (res.ok) {
                alert(`Security Profile ${editId ? 'Updated' : 'Created'} successfully!`);
                hideUserForm();
                location.reload();
            } else {
                const err = await res.json();
                alert(`Operation failed: ${err.detail || 'Unknown error'}`);
            }
        } catch (err) {
            console.error("Submission Error:", err);
            alert("Failed to connect to security server.");
        }
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

    // Directory View Logic
    window.loadDirectoryData = async (roleType, containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            const token = localStorage.getItem('token');
            const role = localStorage.getItem('role');
            const url = (role === 'Manager' && roleType === 'employee') ? '/api/monitoring/all-employees' : '/api/admin/users';

            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const allUsers = await response.json();
            const filtered = allUsers.filter(u => u.role === (roleType === 'employee' ? 'Employee' : 'Manager'));

            renderAssetCards(filtered, containerId);

            // Setup Search
            const searchId = roleType === 'employee' ? 'employeeSearch' : 'managerSearch';
            const searchInput = document.getElementById(searchId);
            if (searchInput) {
                searchInput.oninput = (e) => {
                    const term = e.target.value.toLowerCase();
                    const searched = filtered.filter(u =>
                        u.full_name.toLowerCase().includes(term) ||
                        u.employee_id.toLowerCase().includes(term) ||
                        u.email.toLowerCase().includes(term)
                    );
                    renderAssetCards(searched, containerId);
                };
            }
        } catch (err) {
            console.error(`Error loading ${roleType} directory:`, err);
        }
    };

    const renderAssetCards = (users, containerId) => {
        const container = document.getElementById(containerId);
        container.innerHTML = users.map(u => {
            const role = localStorage.getItem('role');
            const actions = role === 'Admin' ? `
                <button class="action-btn btn-edit" onclick="editUser('${u.id}')">
                    <i data-lucide="edit-3" style="width:14px;"></i> Edit
                </button>
                <button class="action-btn btn-suspend" onclick="openSuspensionModal('${u.id}')">
                    <i data-lucide="clock" style="width:14px;"></i> Suspend
                </button>
                <button class="action-btn btn-delete" onclick="deleteUser('${u.id}')">
                    <i data-lucide="trash-2" style="width:14px;"></i> Delete
                </button>
            ` : `
                <button class="btn-secondary" onclick="quickAssignTask('${u.id}')" 
                        style="color: var(--accent-cyan); border-color: rgba(0, 212, 255, 0.2); background: rgba(0, 212, 255, 0.05); flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 12px; height: 70px;">
                    <i data-lucide="plus-circle" style="width: 18px; height: 18px;"></i>
                    <span style="font-size: 0.7rem; font-weight: 600;">Assign Work</span>
                </button>
                <button class="btn-secondary" onclick="raiseComplaint('${u.id}', '${u.full_name}')" 
                        style="color: var(--error); border-color: rgba(239, 68, 68, 0.2); background: rgba(239, 68, 68, 0.05); flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 12px; height: 70px;">
                    <i data-lucide="alert-triangle" style="width: 18px; height: 18px;"></i>
                    <span style="font-size: 0.7rem; font-weight: 600;">Raise Concern</span>
                </button>
            `;

            return `
            <div class="asset-card">
                <div class="asset-card-header">
                    <div>
                        <div class="asset-name">${u.full_name}</div>
                        <div class="asset-id">${u.employee_id}</div>
                    </div>
                    <span class="asset-badge ${u.is_suspended ? 'badge-suspended' : (u.role === 'Employee' ? 'badge-employee' : 'badge-manager')}">
                        ${u.is_suspended ? 'Suspended' : u.role}
                    </span>
                </div>
                <div class="asset-details">
                    <div class="detail-item">
                        <span class="detail-label">Email</span>
                        ${u.email}
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Department</span>
                        ${u.department_id || 'Global'}
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Joined</span>
                        ${new Date(u.joining_date).toLocaleDateString()}
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Stability</span>
                        <span style="color: var(--accent-cyan); font-weight: bold;">0.85</span>
                    </div>
                </div>
                <div class="asset-actions">
                    ${actions}
                </div>
            </div>
        `}).join('');
        if (window.lucide) lucide.createIcons();
    };

    // Action Handlers
    window.deleteUser = async (id) => {
        if (!confirm('🛑 WARNING: Permanently delete this human asset record? This cannot be undone.')) return;
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/admin/users/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                console.log('🗑️ Asset deleted');
                location.reload(); // Refresh to show changes
            }
        } catch (err) { console.error('Delete failed:', err); }
    };

    window.openSuspensionModal = (id) => {
        document.getElementById('suspend-user-id').value = id;
        document.getElementById('suspension-modal').classList.add('active');
    };

    window.closeSuspensionModal = () => {
        document.getElementById('suspension-modal').classList.remove('active');
    };

    window.executeSuspension = async () => {
        const id = document.getElementById('suspend-user-id').value;
        const start = document.getElementById('suspend-start').value;
        const end = document.getElementById('suspend-end').value;
        const reason = document.getElementById('suspend-reason').value;

        if (!start || !end || !reason) {
            alert('Please fill all suspension parameters.');
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/admin/users/${id}/suspend?start_date=${start}&end_date=${end}&reason=${reason}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                alert('Asset suspended successfully.');
                closeSuspensionModal();
                location.reload();
            }
        } catch (err) { console.error('Suspension failed:', err); }
    };

    window.editUser = (id) => {
        const user = (window._allUsers || []).find(u => u.id === id);
        if (!user) {
            alert("Asset not found in local cache. Refreshing...");
            return;
        }

        console.log('✏️ Calibrating Asset Profile:', user);

        const modal = document.getElementById('user-modal');
        const title = document.getElementById('form-title');
        const submitBtn = document.getElementById('submit-user-btn');

        title.innerText = `Calibrate Profile: ${user.full_name}`;
        submitBtn.innerText = "Commit Changes";
        document.getElementById('editing-user-id').value = user.id;
        window._pendingRole = user.role;

        // Pre-fill fields
        document.getElementById('user-fullname').value = user.full_name || "";
        document.getElementById('user-email').value = user.email || "";
        document.getElementById('user-mobile').value = user.mobile_number || "";
        document.getElementById('user-gender').value = user.gender || "Male";
        document.getElementById('user-address').value = user.address || "";
        document.getElementById('user-username').value = user.username || "";
        document.getElementById('user-employee-id').value = user.employee_id || "";
        document.getElementById('user-department').value = user.department_id || "";
        document.getElementById('user-employment-type').value = user.employment_type || "Full-Time";
        document.getElementById('user-emergency').value = user.emergency_contact || "";

        if (user.dob) document.getElementById('user-dob').value = user.dob.split('T')[0];
        if (user.joining_date) document.getElementById('user-joining').value = user.joining_date.split('T')[0];

        // Do not pre-fill password for security
        document.getElementById('user-password').value = "••••••••";

        modal.classList.add('active');
    };
}

window.handleLogout = () => {
    localStorage.clear();
    location.reload();
};


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

        if (viewId === 'admin') {
            if (window.loadAdminData) window.loadAdminData();
        } else if (viewId === 'manager') {
            if (window.loadManagerData) window.loadManagerData();
        } else if (viewId === 'employees') {
            if (window.loadDirectoryData) window.loadDirectoryData('employee', 'employeesListGrid');
        } else if (viewId === 'managers') {
            if (window.loadDirectoryData) window.loadDirectoryData('manager', 'managersListGrid');
        }
    }
}

// Manager Data Logic
window.loadManagerData = async () => {
    try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/monitoring/manager-stats', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return;
        const stats = await res.json();

        // Update Stats
        document.getElementById('mgr-team-count').innerText = stats.team_count;
        document.getElementById('mgr-at-risk-count').innerText = stats.at_risk_count;
        document.getElementById('mgr-team-stability').innerText = stats.avg_stability;

        // Populate Activity Log
        const logEl = document.getElementById('team-activity-log');
        if (stats.recent_checkins.length === 0) {
            logEl.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 2rem;">No recent team pulses detected.</p>';
        } else {
            logEl.innerHTML = stats.recent_checkins.map(c => `
                <div style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid ${c.mood === 'Stressed' ? 'var(--error)' : 'var(--accent-cyan)'};">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span style="font-weight: bold;">${c.user}</span>
                        <span style="color: var(--text-muted);">${c.time}</span>
                    </div>
                    <div style="font-size: 0.75rem; margin-top: 4px;">
                        Mood: <strong>${c.mood}</strong> | Workload: <strong>${c.workload}</strong>
                    </div>
                </div>
            `).join('');
        }

        // Populate Task Assignee Select
        const teamRes = await fetch('/api/monitoring/all-employees', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (teamRes.ok) {
            const allUsers = await teamRes.json();
            const myTeam = allUsers.filter(u => u.role === 'Employee'); // For demo, show all employees
            const select = document.getElementById('task-assignee');
            const teamList = document.getElementById('mgr-team-list');

            if (select) {
                select.innerHTML = '<option value="">Select Resource...</option>' +
                    myTeam.map(u => `<option value="${u.id}">${u.full_name}</option>`).join('');
            }

            if (teamList) {
                teamList.innerHTML = myTeam.map(u => `
                    <div class="asset-card" style="margin-bottom: 1rem;">
                        <div class="asset-header">
                            <div>
                                <h3 style="margin: 0; font-size: 1rem;">${u.full_name}</h3>
                                <span class="role-badge employee" style="font-size: 0.65rem;">${u.employee_id}</span>
                            </div>
                            <div class="asset-status">
                                <span class="status-indicator" style="background: ${Math.random() > 0.8 ? 'var(--error)' : 'var(--accent-cyan)'}"></span>
                                0.85 Stability
                            </div>
                        </div>
                        <div class="asset-details" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 1rem;">
                            <div class="detail-item">
                                <span class="detail-label">Email</span>
                                <span style="font-size: 0.8rem;">${u.email}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Department</span>
                                <span style="font-size: 0.8rem;">${u.department_id || 'Global Ops'}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Joining Date</span>
                                <span style="font-size: 0.8rem;">${new Date(u.joining_date).toLocaleDateString()}</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">Contact</span>
                                <span style="font-size: 0.8rem;">${u.mobile_number || 'N/A'}</span>
                            </div>
                        </div>
                        <div class="asset-actions" style="margin-top: 1rem; border-top: 1px solid var(--border); padding-top: 1rem; display: flex; gap: 10px;">
                            <button class="btn-secondary" onclick="quickAssignTask('${u.id}')" 
                                    style="color: var(--accent-cyan); border-color: rgba(0, 212, 255, 0.2); background: rgba(0, 212, 255, 0.05); flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 12px; height: 70px;">
                                <i data-lucide="plus-circle" style="width: 18px; height: 18px;"></i>
                                <span style="font-size: 0.7rem; font-weight: 600;">Assign Work</span>
                            </button>
                            <button class="btn-secondary" onclick="raiseComplaint('${u.id}', '${u.full_name}')" 
                                    style="color: var(--error); border-color: rgba(239, 68, 68, 0.2); background: rgba(239, 68, 68, 0.05); flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; padding: 12px; height: 70px;">
                                <i data-lucide="alert-triangle" style="width: 18px; height: 18px;"></i>
                                <span style="font-size: 0.7rem; font-weight: 600;">Raise Concern</span>
                            </button>
                        </div>
                    </div>
                `).join('');
                if (window.lucide) lucide.createIcons();
            }
        }

        // Load Heatmap
        initManagerCharts();

    } catch (err) {
        console.error("Manager data load failed:", err);
    }
};

window.deployTeamTask = async () => {
    const task = {
        title: document.getElementById('task-title').value,
        description: "Assigned via Manager Dashboard Operations",
        assigned_to_id: document.getElementById('task-assignee').value,
        expected_hours: parseFloat(document.getElementById('task-hours').value),
        deadline: document.getElementById('task-deadline').value ? new Date(document.getElementById('task-deadline').value).toISOString() : null,
        priority: document.getElementById('task-priority').value
    };

    if (!task.title || !task.assigned_to_id) {
        alert("Mission Objective and Target Asset are required.");
        return;
    }

    try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/tasks/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(task)
        });

        if (res.ok) {
            alert("🚀 Strategic Mission Deployed Successfully!");
            document.getElementById('task-title').value = "";
            document.getElementById('task-hours').value = "";
        } else {
            const err = await res.json();
            alert(`Deployment Failed: ${err.detail}`);
        }
    } catch (err) {
        console.error("Deploy error:", err);
    }
};

window.raiseComplaint = (id, name) => {
    const reason = prompt(`🛑 ESCALATION PROTOCOL: Please state the stability concern or complaint for asset ${name}:`);
    if (reason) {
        alert(`🚨 LOGGED: A formal stability concern has been escalated for ${name}. Administrative oversight has been notified.`);
        console.log(`[Escalation] Asset ID: ${id}, Reason: ${reason}`);
        // In a production environment, this would hit /api/admin/complaints or similar
    }
};

// Email Task Assignment - Mission Dispatch Suite
let selectedAssignmentFile = null;

window.quickAssignTask = (userId) => {
    console.log(`📡 Initiating assignment for asset: ${userId}`);
    const modal = document.getElementById('email-modal');
    if (!modal) return;

    // Phase 1: Immediate Manifestation
    modal.classList.add('active');
    if (window.lucide) lucide.createIcons();

    // Reset Form Fields
    document.getElementById('email-from').value = `${localStorage.getItem('username') || 'Authorized Manager'} (Management Node)`;
    document.getElementById('email-to').value = "Loading asset telemetry...";
    document.getElementById('email-body').value = "";
    document.getElementById('email-subject').value = "";
    document.getElementById('file-name').innerText = "";
    selectedAssignmentFile = null;

    // Initialize Drag & Drop logic if not already done
    setupAssignmentDragAndDrop();

    // Phase 2: Telemetry Synchronization
    const token = localStorage.getItem('token');
    fetch('/api/monitoring/all-employees', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
        .then(res => res.json())
        .then(users => {
            if (!Array.isArray(users)) throw new Error("Invalid workforce data");
            const user = users.find(u => u.id === userId);
            if (user) {
                document.getElementById('email-to').value = `${user.full_name} <${user.email}>`;
                document.getElementById('email-to').dataset.userId = userId;
                document.getElementById('email-subject').value = `Operational Mission: ${user.full_name}`;
                console.log("✅ Asset telemetry synchronized.");
            }
        })
        .catch(err => {
            console.error("❌ Telemetry failed:", err);
            document.getElementById('email-to').value = "Sync Error: Manual Override Required";
        });
};

function setupAssignmentDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('email-file');
    const fileNameDisplay = document.getElementById('file-name');

    if (!dropZone || !fileInput) return;

    // Trigger click on zone
    dropZone.onclick = () => fileInput.click();

    // File selection change
    fileInput.onchange = (e) => {
        if (e.target.files.length > 0) {
            handleAssignmentFile(e.target.files[0]);
        }
    };

    // Drag & Drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = 'var(--accent-cyan)';
            dropZone.style.background = 'rgba(0, 212, 255, 0.08)';
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = 'rgba(0, 212, 255, 0.3)';
            dropZone.style.background = 'rgba(0, 212, 255, 0.02)';
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        if (file) handleAssignmentFile(file);
    }, false);

    function handleAssignmentFile(file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'text/csv', 'application/pdf'];
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|csv|pdf)$/i)) {
            alert("🛑 INCOMPATIBLE ASSET: Only JPEG, PNG, CSV, and PDF documentation is permitted.");
            return;
        }
        selectedAssignmentFile = file;
        fileNameDisplay.innerText = `📂 ATTACHED: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        console.log(`📎 Operational asset attached: ${file.name}`);
    }
}

window.closeEmailModal = () => {
    const modal = document.getElementById('email-modal');
    if (modal) modal.classList.remove('active');
};

window.dispatchEmailTask = async () => {
    const userId = document.getElementById('email-to').dataset.userId;
    const title = document.getElementById('email-subject').value || "Mission Assignment";
    const body = document.getElementById('email-body').value;
    const hours = document.getElementById('email-hours').value || "0";
    const deadline = document.getElementById('email-deadline').value;
    const priority = document.getElementById('email-priority').value;

    if (!body || !userId) {
        alert("🛑 MISSION ABORTED: Objectives and Target Asset are required.");
        return;
    }

    // High-performance FormData construction
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', body);
    formData.append('assigned_to_id', userId);
    formData.append('expected_hours', hours);
    formData.append('deadline', deadline ? new Date(deadline).toISOString() : new Date().toISOString());
    formData.append('priority', priority);

    if (selectedAssignmentFile) {
        formData.append('file', selectedAssignmentFile);
    }

    try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/tasks', { // Removed trailing slash for robustness
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (res.ok) {
            alert("🚀 MISSION DEPLOYED: Personnel record updated and SMTP dispatch successful.");
            closeEmailModal();
            if (window.loadManagerData) await window.loadManagerData();
        } else {
            const errText = await res.text();
            let errDetail = "Unknown Tactical Error";
            try {
                const errJson = JSON.parse(errText);
                errDetail = errJson.detail || errDetail;
            } catch (e) { }
            alert(`⚠️ Tactical Error (Status: ${res.status}): ${errDetail}`);
        }
    } catch (err) {
        console.error("🚨 Dispatch failure:", err);
        alert(`🚨 SYSTEM CRITICAL: Connection refused or Timeout. [Log: ${err.message}]`);
    }
};

function initManagerCharts() {
    const ctx = document.getElementById('burnoutHeatmap');
    if (!ctx) return;

    if (window._charts.burnoutHeatmap) {
        window._charts.burnoutHeatmap.destroy();
    }

    window._charts.burnoutHeatmap = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            datasets: [{
                label: 'Team Burnout Risk',
                data: [12, 19, 15, 25, 32],
                backgroundColor: ['#10b981', '#10b981', '#fbbf24', '#f59e0b', '#ef4444'],
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: 'Stress Level %' } },
                x: { grid: { display: false } }
            }
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
