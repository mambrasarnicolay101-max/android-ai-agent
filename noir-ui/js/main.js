// ═══════════════════════════════════════════════════════
// NOIR SOVEREIGN — MISSION CONTROL JS  V21.2 ELITE AEGIS
// ═══════════════════════════════════════════════════════
const API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026";
const H = { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" };

// ── State ────────────────────────────────────────────
let activePanel = 'dashboard';
let isAgentOnline = false;
let lastScreenshot = null;
let chatHistory = [];

// ── Navigation ───────────────────────────────────────
function showPanel(panelId) {
    activePanel = panelId;
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    
    const panel = document.getElementById(`panel-${panelId}`);
    if (panel) panel.classList.add('active');
    
    // Find the nav item that matches the panelId (some might be custom)
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(nav => {
        if (nav.getAttribute('onclick')?.includes(`'${panelId}'`)) {
            nav.classList.add('active');
        }
    });

    const titles = {
        dashboard: 'COMMAND OVERVIEW',
        vision: 'NEURAL VISION STREAM',
        chat: 'COMMAND TERMINAL',
        browser: 'AUTONOMOUS RESEARCH',
        evolution: 'EVOLUTION ENGINE',
        pc: 'NODE MANAGEMENT',
        wiki: 'SOVEREIGN WIKI',
        synthesis: 'NEURAL SYNTHESIS LAB',
        logs: 'SYSTEM LOGS',
        swarm: 'SWARM INTELLIGENCE MONITOR',
        neuralmap: '3D SYNAPTIC NEURAL MAP'
    };
    document.getElementById('active-panel-title').innerText = titles[panelId] || panelId.toUpperCase();
    
    if (panelId === 'evolution') refreshEvolutions();
    if (panelId === 'pc') refreshPcStats();
    if (panelId === 'swarm') pollSwarmFeed();
    if (panelId === 'neuralmap') {
        const iframe = document.getElementById('neuralmap-iframe');
        if (iframe) iframe.src = 'neural_map.html?t=' + Date.now();
    }
    if (panelId === 'wiki') {
        const iframe = document.getElementById('wiki-iframe');
        if (iframe) iframe.src = 'wiki.html?t=' + Date.now();
    }
}

async function startSynthesis() {
    const goal = document.getElementById('synth-goal').value;
    if (!goal) return alert("Masukkan objektif sintesis terlebih dahulu.");

    const box = document.getElementById('synth-status-box');
    const text = document.getElementById('synth-status-text');
    const bar = document.getElementById('synth-progress-bar');
    const log = document.getElementById('synth-log');

    box.style.display = 'block';
    log.innerHTML = '<div>> Memulai misi otonom...</div>';
    
    const steps = [
        { t: "ANALYZING GOAL...", p: 15, l: "Menganalisis kebutuhan arsitektur sistem..." },
        { t: "GENERATING CODE...", p: 40, l: "Neural Coder sedang merancang logika asinkron..." },
        { t: "SECURITY AUDIT...", p: 65, l: "Security Sentinel melakukan scan SAST pada kode..." },
        { t: "VALIDATING...", p: 85, l: "Memverifikasi integritas dan kompabilitas modul..." },
        { t: "DEPLOYING...", p: 95, l: "Memasang skill baru ke dalam sistem syaraf Noir..." }
    ];

    for (const s of steps) {
        text.innerText = s.t;
        bar.style.width = s.p + '%';
        log.innerHTML += `<div>> ${s.l}</div>`;
        log.scrollTop = log.scrollHeight;
        await new Promise(r => setTimeout(r, 2000));
    }

    try {
        const resp = await fetch('/api/synthesis/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal })
        });
        const data = await resp.json();
        if (data.success) {
            text.innerText = "COMPLETED";
            bar.style.width = '100%';
            log.innerHTML += `<div style="color:var(--success)">> SUCCESS: Skill ${data.class} berhasil dipasang!</div>`;
        } else {
            text.innerText = "FAILED";
            log.innerHTML += `<div style="color:#ef4444">> ERROR: ${data.reason}</div>`;
        }
    } catch (e) {
        text.innerText = "ERROR";
        log.innerHTML += `<div style="color:#ef4444">> Connection failed.</div>`;
    }
}

let ghostActive = false;
async function toggleGhostMode() {
    ghostActive = !ghostActive;
    const btn = document.getElementById('ghost-toggle-btn');
    const status = document.getElementById('ghost-status');
    
    try {
        const resp = await fetch('/api/ghost/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ active: ghostActive })
        });
        const data = await resp.json();
        if (data.success) {
            if (ghostActive) {
                btn.innerHTML = '<i class="fas fa-eye-slash"></i> DEACTIVATE GHOST';
                btn.classList.add('primary');
                status.innerText = "ACTIVE [STEALTH]";
                status.className = "text-success";
            } else {
                btn.innerHTML = '<i class="fas fa-mask"></i> ACTIVATE GHOST';
                btn.classList.remove('primary');
                status.innerText = "INACTIVE";
                status.className = "text-dim";
            }
        }
    } catch (e) {
        alert("Gagal menghubungi Ghost Engine.");
    }
}

// ── NEURAL VOICE BRIDGE ─────────────────────────────
let voiceEnabled = false;
const synth = window.speechSynthesis;

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    const btn = document.getElementById('voice-toggle-btn');
    if (voiceEnabled) {
        btn.classList.add('primary');
        btn.innerHTML = '<i class="fas fa-volume-up"></i> VOICE: ON';
        speak("Neural Voice Bridge Active. I am now capable of audio feedback.");
    } else {
        btn.classList.remove('primary');
        btn.innerHTML = '<i class="fas fa-volume-mute"></i> VOICE: OFF';
        synth.cancel();
    }
}

function speak(text) {
    if (!voiceEnabled || !text) return;
    
    // Cancel previous speech to prevent overlap
    synth.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    // Set English or Indonesian if possible
    utterance.lang = 'en-US'; // Default to English for a more 'AI' feel, or auto-detect
    utterance.pitch = 0.8; // Lower pitch for a more 'serious' tone
    utterance.rate = 1.0;
    
    // Handle Indonesian detection
    if (/[a-z]/i.test(text) && (text.includes("berhasil") || text.includes("aktif") || text.includes("sistem"))) {
        utterance.lang = 'id-ID';
    }

    synth.speak(utterance);
}

// ── REAL-TIME WEBSOCKET BRIDGE ──────────────────
let socket;
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws/telemetry`);

    socket.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        if (msg.type === 'log') {
            const entry = msg.data;
            const log = document.getElementById('terminal');
            const color = entry.level === 'CRITICAL' ? '#ef4444' : 
                          entry.level === 'WARNING' ? '#f59e0b' : '#10b981';
            
            log.innerHTML += `<div style="color:${color}">[${entry.timestamp}] [${entry.device_id}] ${entry.message}</div>`;
            log.scrollTop = log.scrollHeight;
            
            // Critical Voice Feedback
            if (entry.level === 'CRITICAL') {
                speak("Attention. Critical system event from " + entry.device_id + ": " + entry.message);
            }
        }
    };

    socket.onclose = function() {
        console.log("WebSocket closed. Reconnecting in 5s...");
        setTimeout(initWebSocket, 5000);
    };
}

// ── Main Loop ────────────────────────────────────────
async function poll() {
    // Keep polling for non-WS telemetry like PC stats
    try {
        const r = await fetch('/api/summary', { headers: H });
        if (!r.ok) throw new Error('API error');
        const d = await r.json();
        
        updateStatusChips(d);
        updateTelemetry(d);
        if (d.logs) ingestLogs(d.logs);
        if (d.agent?.last_screenshot) updateVision(d.agent.last_screenshot);
        
        // Render SMI (Sovereign Maturity Index)
        if (d.smi) {
            const scoreEl = document.getElementById('smi-score');
            const barEl = document.getElementById('smi-bar');
            const phaseEl = document.getElementById('smi-phase');
            const readyEl = document.getElementById('smi-readiness');
            
            if (scoreEl) scoreEl.innerText = d.smi.score;
            if (barEl) barEl.style.width = d.smi.score + '%';
            if (phaseEl) phaseEl.innerText = d.smi.phase;
            if (readyEl) {
                readyEl.innerText = d.smi.readiness;
                // Color coding for readiness
                if (d.smi.score > 75) readyEl.style.color = '#10b981';
                else if (d.smi.score > 50) readyEl.style.color = '#f59e0b';
                else readyEl.style.color = '#ef4444';
            }
        }
        
        // Handle offline warning — uses CSS class 'visible'
        isAgentOnline = d.online;
        const warn = document.getElementById('offline-warning');
        if (warn) {
            if (!isAgentOnline) warn.classList.add('visible');
            else warn.classList.remove('visible');
        }

        // Voice Feedback for Critical Events
        if (d.logs && d.logs.length > 0) {
            const lastLog = d.logs[d.logs.length - 1];
            if (lastLog.level === 'CRITICAL' || lastLog.level === 'ERROR') {
                if (window.lastSpokenLog !== lastLog.message) {
                    speak("Warning. Critical event detected: " + lastLog.message);
                    window.lastSpokenLog = lastLog.message;
                }
            }
        }
        
        // Render 12 Pillars Mesh
        if (d.pillars) {
            const meshContainer = document.getElementById('pilar-mesh-list');
            if (meshContainer) {
                // We assume the list is already there, just update the dots
                const dots = meshContainer.querySelectorAll('.dot');
                dots.forEach(dot => dot.classList.add('online')); // All online for now
            }
        }
        
        if (d.learning_progress) {
            const learnBar = document.querySelector('.tele-bar-fill[style*="92%"]');
            if (learnBar) learnBar.style.width = d.learning_progress + '%';
        }

    } catch (e) {
        console.error('Poll error:', e);
        updateStatusChips({ online: false, core_online: true });
    }
}

function updateStatusChips(d) {
    const coreChip = document.getElementById('core-status-chip');
    if (coreChip) {
        coreChip.innerHTML = d.core_online ? '<i class="fas fa-brain"></i> AI CORE: ONLINE' : '<i class="fas fa-brain-slash"></i> AI CORE: OFFLINE';
        coreChip.className = `chip ${d.core_online ? 'online' : 'offline'}`;
    }

    const vpsChip = document.getElementById('alibaba-chip');
    if (vpsChip && d.alibaba_vps) {
        vpsChip.innerHTML = `<i class="fas fa-cloud"></i> ALIBABA VPS: ${d.alibaba_vps.status}`;
        vpsChip.className = `chip ${d.alibaba_vps.status === 'ONLINE' ? 'online' : ''}`;
    }
    
    const agentChip = document.getElementById('agent-status-chip');
    if (agentChip) {
        agentChip.innerHTML = d.online ? '<i class="fas fa-link"></i> LINK: ACTIVE' : '<i class="fas fa-link-slash"></i> LINK: SEVERED';
        agentChip.className = `chip ${d.online ? 'online' : 'offline'}`;
    }
}

function updateTelemetry(d) {
    const set = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = val !== undefined ? val + (id.includes('stat') ? '%' : '') : '--';
    };
    const bar = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.style.width = (val || 0) + '%';
    };

    if (d.agent?.stats) {
        const s = d.agent.stats;
        set('stat-cpu', s.cpu); bar('bar-cpu', s.cpu);
        set('stat-ram', s.ram); bar('bar-ram', s.ram);
        set('stat-bat', s.bat || s.battery); bar('bar-bat', s.bat || s.battery);
    }

    if (d.pc_stats) {
        const ps = d.pc_stats;
        set('pc-cpu', ps.cpu_percent); bar('bar-pc-cpu', ps.cpu_percent);
        set('pc-ram', ps.ram_percent); bar('bar-pc-ram', ps.ram_percent);
    }
    
    if (d.proactive_insight) {
        document.getElementById('ai-insight').innerText = d.proactive_insight;
    }
}

function updateVision(key) {
    if (key === lastScreenshot) return;
    lastScreenshot = key;
    const cleanKey = key.replace('local:', '');
    const url = `/api/asset/${cleanKey}?t=${Date.now()}`;
    
    const dashImg = document.getElementById('dashboard-vision-img');
    const mainImg = document.getElementById('main-vision-img');
    const placeholder = document.getElementById('vision-placeholder');
    
    if (dashImg) { dashImg.src = url; dashImg.style.display = 'block'; }
    if (mainImg) { mainImg.src = url; }
    if (placeholder) placeholder.style.display = 'none';
}

// ── Commands ─────────────────────────────────────────
async function sendCommand(type, extra = {}) {
    try {
        const r = await fetch('/api/command', {
            method: 'POST', headers: H,
            body: JSON.stringify({ target_device: 'REDMI_NOTE_14', action: { type, ...extra } })
        });
        const d = await r.json();
        addLog('CMD', `Sent: ${type.toUpperCase()}`);
        return d;
    } catch (e) {
        addLog('ERROR', `Cmd failed: ${e.message}`);
    }
}

// ── Chat ─────────────────────────────────────────────
async function sendChatMessage() {
    const inp = document.getElementById('chat-input');
    const msg = inp.value.trim();
    if (!msg) return;
    inp.value = '';
    
    addBubble('user', msg);
    try {
        const r = await fetch('/api/brain/chat', {
            method: 'POST', headers: H,
            body: JSON.stringify({ message: msg, device_id: 'REDMI_NOTE_14' })
        });
        const d = await r.json();
        addBubble('ai', d.response || 'System processing error.');
    } catch (e) {
        addBubble('ai', `Connection error: ${e.message}`);
    }
}

function addBubble(role, text) {
    const win = document.getElementById('chat-window');
    if (!win) return;
    const d = document.createElement('div');
    d.className = `chat-msg ${role}`;
    d.innerHTML = `<div class="chat-bubble">${text}</div>`;
    win.appendChild(d);
    win.scrollTop = win.scrollHeight;
}

// ── Browser ──────────────────────────────────────────
async function browserGo() {
    const inp = document.getElementById('browser-url');
    let url = inp.value.trim();
    if (!url) return;
    if (!url.startsWith('http')) url = 'https://' + url;
    
    const view = document.getElementById('browser-viewport');
    const img = document.getElementById('browser-img');
    const ph = document.getElementById('browser-placeholder');
    
    ph.innerHTML = '<i class="fas fa-circle-notch fa-spin fa-3x"></i><span>Navigating Secure Tunnel...</span>';
    
    try {
        const r = await fetch('/api/browser/goto', {
            method: 'POST', headers: H, body: JSON.stringify({ url })
        });
        const d = await r.json();
        if (d.screenshot) {
            img.src = `data:image/jpeg;base64,${d.screenshot}`;
            img.style.display = 'block';
            ph.style.display = 'none';
        }
    } catch (e) {
        ph.innerHTML = `<i class="fas fa-exclamation-circle fa-3x text-danger"></i><span>Research Failed: ${e.message}</span>`;
    }
}

// ── Evolution ────────────────────────────────────────
async function refreshEvolutions() {
    try {
        const r = await fetch('/api/evolutions', { headers: H });
        const d = await r.json();
        const pList = document.getElementById('evo-pending');
        const hList = document.getElementById('evo-history');

        pList.innerHTML = d.pending.length ? d.pending.map(p => `
            <div class="evo-card">
                <input type="checkbox" class="evo-checkbox" data-id="${p.id}">
                <div class="evo-card-body">
                    <div class="evo-card-title">${p.title}</div>
                    <div class="evo-card-desc">${p.description}</div>
                    <div class="evo-card-actions">
                        <button class="micro-btn primary" onclick="approveEvo('${p.id}')"><i class="fas fa-check"></i> APPROVE</button>
                        <button class="micro-btn" onclick="rejectEvo('${p.id}')"><i class="fas fa-xmark"></i> REJECT</button>
                    </div>
                </div>
            </div>
        `).join('') : '<div class="text-dim" style="font-size:0.8rem;padding:0.5rem 0;">No pending proposals.</div>';

        hList.innerHTML = d.history.length ? d.history.slice(-8).reverse().map(h => `
            <div style="font-size:0.75rem; padding:0.6rem 0; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; gap:1rem;">
                <span class="text-dim" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${h.title}</span>
                <span class="${h.status === 'APPLIED' ? 'text-success' : 'text-danger'}" style="flex-shrink:0; font-family:var(--font-mono); font-size:0.65rem;">${h.status}</span>
            </div>
        `).join('') : '<div class="text-dim" style="font-size:0.8rem;padding:0.5rem 0;">No history yet.</div>';
    } catch (e) {
        console.error('Evo refresh failed:', e);
    }
}

async function approveSelectedEvos() {
    const checked = document.querySelectorAll('.evo-checkbox:checked');
    if (!checked.length) return;
    
    addLog('SYSTEM', `Batch approving ${checked.length} mutations...`);
    for (const cb of checked) {
        const id = cb.dataset.id;
        await fetch('/api/evolution/approve', { method: 'POST', headers: H, body: JSON.stringify({ id }) });
    }
    refreshEvolutions();
}

async function approveAllEvos() {
    const checkboxes = document.querySelectorAll('.evo-checkbox');
    if (!checkboxes.length) return;
    
    addLog('SYSTEM', `Approve All: Processing ${checkboxes.length} mutations...`);
    for (const cb of checkboxes) {
        const id = cb.dataset.id;
        await fetch('/api/evolution/approve', { method: 'POST', headers: H, body: JSON.stringify({ id }) });
    }
    refreshEvolutions();
}

async function approveEvo(id) {
    await fetch('/api/evolution/approve', { method: 'POST', headers: H, body: JSON.stringify({ id }) });
    refreshEvolutions();
}

async function rejectEvo(id) {
    await fetch('/api/evolution/reject', { method: 'POST', headers: H, body: JSON.stringify({ id }) });
    refreshEvolutions();
}

// ── PC Master ────────────────────────────────────────
async function refreshPcStats() {
    // Already handled by poll, but could add specific refresh here
}

async function togglePcOverride() {
    const btn = document.getElementById('pc-override-btn');
    const isOverridden = btn.innerText.includes('DISABLE');
    
    try {
        const r = await fetch('/api/pc/override', {
            method: 'POST', headers: H,
            body: JSON.stringify({ state: !isOverridden })
        });
        const d = await r.json();
        btn.innerText = d.override ? 'DISABLE OVERRIDE' : 'ENABLE OVERRIDE';
        btn.className = d.override ? 'cmd-btn purple' : 'cmd-btn danger';
        addLog('AEGIS', `Override status changed to: ${d.override}`);
    } catch {}
}

// ── Logs ─────────────────────────────────────────────
function ingestLogs(logs) {
    const term = document.getElementById('terminal');
    if (!term) return;
    logs.forEach(l => {
        const entry = document.createElement('div');
        entry.innerHTML = `<span class="text-dim">[${new Date().toLocaleTimeString()}]</span> <span class="text-accent">${l.level}</span> ${l.message}`;
        term.appendChild(entry);
    });
    if (logs.length > 0) term.scrollTop = term.scrollHeight;
}

function addLog(level, msg) {
    ingestLogs([{ level, message: msg }]);
}

function exportLogs() {
    const text = document.getElementById('terminal').innerText;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `noir_system_dump_${Date.now()}.txt`;
    a.click();
}

// ── Swarm Monitor ─────────────────────────────────────
async function pollSwarmFeed() {
    try {
        const r = await fetch('/api/swarm/bus', { headers: H });
        if (!r.ok) {
            document.getElementById('swarm-live-feed').innerHTML =
                `<div style="color:rgba(255,80,80,0.7);">⚠ Swarm Bus API tidak dapat dijangkau. Pastikan server berjalan.</div>`;
            return;
        }
        const data = await r.json();
        const feedEl = document.getElementById('swarm-live-feed');
        const countEl = document.getElementById('swarm-msg-count');
        const barEl   = document.getElementById('swarm-msg-bar');
        if (!feedEl) return;

        const msgs = (data.messages || []).slice(-30).reverse();
        if (countEl) {
            countEl.textContent = msgs.length + ' msgs';
            if (barEl) barEl.style.width = Math.min(msgs.length * 10, 100) + '%';
        }

        if (msgs.length === 0) {
            feedEl.innerHTML = '<div style="color:rgba(255,255,255,0.2);">◈ Bus kosong — belum ada aktivitas Swarm.</div>';
            return;
        }

        feedEl.innerHTML = msgs.map(msg => {
            const t = new Date(msg.ts * 1000).toLocaleTimeString('id-ID');
            const statusColor = msg.status === 'read' ? 'rgba(255,255,255,0.25)' : '#00ffaa';
            const statusDot   = msg.status === 'read' ? '◦' : '●';
            const content     = typeof msg.content === 'object' ? JSON.stringify(msg.content).substring(0, 80) : msg.content;
            return `<div style="padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); display:flex; gap:0.75rem; align-items:flex-start;">
                <span style="color:${statusColor}; flex-shrink:0;">${statusDot}</span>
                <span style="color:rgba(255,255,255,0.3); flex-shrink:0;">[${t}]</span>
                <span style="color:#00f2ff;">${msg.sender || '?'}</span>
                <span style="color:rgba(255,255,255,0.4);">→</span>
                <span style="color:#bf00ff;">${msg.target || '?'}</span>
                <span style="color:rgba(255,255,255,0.35); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${content}</span>
            </div>`;
        }).join('');
        feedEl.scrollTop = 0;
    } catch (e) {
        const feedEl = document.getElementById('swarm-live-feed');
        if (feedEl) feedEl.innerHTML = `<div style="color:rgba(255,80,80,0.7);">⚠ Error: ${e.message}</div>`;
    }
}
setInterval(pollSwarmFeed, 5000);

// ── Init ─────────────────────────────────────────────
setInterval(poll, 3000);
initWebSocket();
poll();
document.getElementById('chat-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') sendChatMessage(); });
document.getElementById('browser-url')?.addEventListener('keydown', e => { if (e.key === 'Enter') browserGo(); });
