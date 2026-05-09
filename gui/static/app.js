// NOVA-SHIELD Dashboard Client

const socket = io();

// DOM Elements
const totalIntrusionsEl = document.getElementById('total-intrusions');
const highRiskEl = document.getElementById('high-risk');
const last24hEl = document.getElementById('last-24h');
const activityList = document.getElementById('activity-list');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    refreshData();
    
    // Refresh every 30 seconds
    setInterval(refreshData, 30000);
    
    // Socket events
    socket.on('connected', (data) => {
        addActivity('[INFO] Connected to NOVA-SHIELD server');
    });
    
    socket.on('intruder_alert', (data) => {
        addActivity(`[ALERT] Intruder detected! Risk: ${data.risk}`);
    });
    
    socket.on('system_lock', () => {
        addActivity('[LOCK] System locked');
        updateSecurityLevel('locked');
    });
});

// Refresh dashboard data
async function refreshData() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        totalIntrusionsEl.textContent = stats.total_intrusions;
        highRiskEl.textContent = stats.high_risk_count;
        last24hEl.textContent = stats.last_24h;
        
        addActivity('[INFO] Dashboard data refreshed');
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

// Lock system
async function lockSystem() {
    try {
        const response = await fetch('/api/lock', { method: 'POST' });
        if (response.ok) {
            addActivity('[ACTION] Manual lock initiated');
        }
    } catch (error) {
        console.error('Error locking system:', error);
    }
}

// View logs
function viewLogs() {
    window.location.href = '/alerts';
}

// Update security level display
function updateSecurityLevel(level) {
    const levelDiv = document.getElementById('security-level');
    const levels = {
        safe: '<div class="level-safe">[SAFE] System Protected</div>',
        alert: '<div class="level-alert">[ALERT] Suspicious Activity</div>',
        locked: '<div class="level-locked">[LOCKED] System Secured</div>'
    };
    
    levelDiv.innerHTML = levels[level] || levels.safe;
}

// Add activity to log
function addActivity(message) {
    const activityItem = document.createElement('div');
    activityItem.className = 'activity-item';
    activityItem.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    
    activityList.insertBefore(activityItem, activityList.firstChild);
    
    // Keep only last 50 items
    while (activityList.children.length > 50) {
        activityList.removeChild(activityList.lastChild);
    }
}

// Load recent intrusions
async function loadRecentIntrusions() {
    try {
        const response = await fetch('/api/intrusions?limit=10');
        const intrusions = await response.json();
        
        intrusions.forEach(intrusion => {
            addActivity(`[INTRUSION] ${intrusion.timestamp} - Risk: ${intrusion.risk_score}`);
        });
    } catch (error) {
        console.error('Error loading intrusions:', error);
    }
}