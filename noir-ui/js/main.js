// ═══════════════════════════════════════════════════════
// NOIR SOVEREIGN — MISSION CONTROL JS  V21.0 AEGIS
// ═══════════════════════════════════════════════════════
const API_KEY = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026";
const H = { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" };

// ── State ────────────────────────────────────────────
let allLogs = [], logVisible = true, mediaMode = 'screenshots';
let mediaItems = [], evoProposals = [], chatHistory = [];
let mirrorActive = false, mirrorZoom = 1, mirrorInterval = null;
let lastFrame = null, frameCount = 0, fpsTimer = null;
let recInterval = null, recSeconds = 0;
let activeCam = 'back';

// ── SPA Navigation ───────────────────────────────────
function switchPanel(panelId) {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(`panel-${panelId}`);
    const nav   = document.getElementById(`nav-${panelId}`);
    if (panel) panel.classList.add('active');
    if (nav)   nav.classList.add('active');
    const titles = { control:'MISSION CONTROL', mirror:'LIVE SCREEN MIRROR', camera:'CAMERA & AUDIO', chat:'AI NEURAL CHAT', media:'LOOT VAULT', evolution:'AUTONOMOUS EVOLUTION', logs:'SYSTEM LOGS', pc:'PC MASTER CONTROL' };
    document.getElementById('panel-title').innerText = titles[panelId] || panelId.toUpperCase();
    if (panelId === 'media') refreshMedia();
    if (panelId === 'evolution') renderEvolutions();
    if (panelId === 'logs') renderLogs();
    if (panelId === 'pc') refreshPcKnowledge();
    if (panelId === 'mirror' && mirrorActive) startMirror();
    // Clear badge
    const badge = document.getElementById(`${panelId === 'evolution' ? 'evo' : panelId}-badge`);
    if (badge) { badge.style.display = 'none'; badge.innerText = '0'; }
}
document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => switchPanel(btn.dataset.panel));
});

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
}

// ── Clock ────────────────────────────────────────────
setInterval(() => { document.getElementById('sys-time').innerText = new Date().toLocaleTimeString(); }, 1000);

// ── Neural Chart ─────────────────────────────────────
let chart;
function initChart() {
    const ctx = document.createElement('canvas');
    if (!ctx) return;
}

// ── Main Poll Loop ────────────────────────────────────
let lastShot = null, pingStart = 0;

async function poll() {
    try {
        pingStart = Date.now();
        const r = await fetch('/api/summary', { headers: H });
        const ping = Date.now() - pingStart;
        if (!r.ok) throw new Error('API error');
        const d = await r.json();
        updateConn(d.online, ping);
        if (d.agent) updateTelemetry(d.agent, ping);
        if (d.pc_stats) updatePcTelemetry(d.pc_stats);
        if (d.pc_override !== undefined) updateOverrideUI(d.pc_override);
        if (d.logs?.length) ingestLogs(d.logs);
        checkEvos(d.commands || []);
        // AI engine chip
        fetchProvider();
    } catch { updateConn(false, 999); }
}

async function fetchProvider() {
    try {
        const r = await fetch('/api/brain/provider', { headers: H });
        if (r.ok) {
            const d = await r.json();
            const chip = document.getElementById('ai-engine-chip');
            if (chip) { chip.innerHTML = `<i class="fas fa-robot"></i> ${d.provider}`; chip.className = 'chip success'; }
            const chatProv = document.getElementById('chat-provider-name');
            if (chatProv) chatProv.innerText = d.provider;
        }
    } catch {}
}

function updateConn(online, ping) {
    const badge = document.getElementById('connection-status');
    const dot   = document.getElementById('agent-dot');
    if (online) {
        badge.className = 'conn-badge online';
        badge.innerHTML = '<div class="pulse-dot"></div><span>NEURAL LINK ACTIVE</span>';
        dot.className   = 'agent-status-dot online';
    } else {
        badge.className = 'conn-badge offline';
        badge.innerHTML = '<div class="pulse-dot"></div><span>LINK SEVERED</span>';
        dot.className   = 'agent-status-dot offline';
    }
    const pv = document.getElementById('ping-val');
    const pb = document.getElementById('ping-bar');
    if (pv) pv.innerText = `${ping}ms`;
    if (pb) pb.style.width = `${Math.min(ping / 5, 100)}%`;
}

function updateTelemetry(agent, ping) {
    const stats = agent.stats || {};
    const set = (id, v, s='%') => { const e = document.getElementById(id); if (e) e.innerText = v != null ? `${v}${s}` : '--'; };
    const bar = (id, v) => { const e = document.getElementById(id); if (e) e.style.width = `${Math.min(v||0,100)}%`; };

    const bat = stats.bat ?? stats.battery ?? 0;
    set('bat-val', bat); bar('bat-bar', bat);
    set('cpu-val', stats.cpu ?? 0); bar('cpu-bar', stats.cpu ?? 0);
    set('ram-val', stats.ram ?? 0); bar('ram-bar', stats.ram ?? 0);

    // Shizuku
    const sz = stats.shizuku || 'N/A';
    const szChip = document.getElementById('shizuku-chip');
    if (szChip) { szChip.innerHTML = `<i class="fas fa-shield-cat"></i> ${sz}`; szChip.className = sz === 'AUTHORIZED' ? 'chip online' : 'chip neutral'; }
    const szSt = document.getElementById('shizuku-status');
    if (szSt) szSt.innerText = `SHIZUKU: ${sz}`;

    // Version
    if (stats.version) {
        const vChip = document.getElementById('agent-ver-chip');
        if (vChip) vChip.innerHTML = `<i class="fas fa-code-branch"></i> ${stats.version}`;
    }

    // Vision snapshot — BUG#2 FIX: strip local: prefix before building URL
    if (agent.last_screenshot && agent.last_screenshot !== lastShot) {
        lastShot = agent.last_screenshot;
        const cleanKey = lastShot.replace('local:', ''); // BUG#2 FIX
        const img = document.getElementById('vision-img');
        if (img) { img.src = `/api/asset/${cleanKey}?t=${Date.now()}`; img.style.display = 'block'; img.style.opacity = 1; }
        document.getElementById('vision-time').innerText = new Date().toLocaleTimeString();
        document.getElementById('vision-status').innerText = 'LIVE';
        addMediaItem({ type: 'screenshot', key: cleanKey, ts: Date.now() });
    }
}

function updatePcTelemetry(stats) {
    if (!stats) return;
    const set = (id, v, s='%') => { const e = document.getElementById(id); if (e) e.innerText = v != null ? `${v}${s}` : '--'; };
    const bar = (id, v) => { const e = document.getElementById(id); if (e) e.style.width = `${Math.min(v||0,100)}%`; };

    set('pc-cpu-val', stats.cpu_percent); bar('pc-cpu-bar', stats.cpu_percent);
    set('pc-ram-val', stats.ram_used_gb, ' GB'); bar('pc-ram-bar', stats.ram_percent);
    set('pc-disk-val', stats.disk_percent); bar('pc-disk-bar', stats.disk_percent);
}

let pcOverrideActive = false;
async function togglePcOverride() {
    pcOverrideActive = !pcOverrideActive;
    try {
        const r = await fetch('/api/pc/override', {
            method: 'POST', headers: H,
            body: JSON.stringify({ state: pcOverrideActive })
        });
        const d = await r.json();
        updateOverrideUI(d.override);
        addLog('AEGIS', `Sovereign Override: ${d.override ? 'ENABLED - ALL RESTRICTIONS LIFTED' : 'DISABLED - SECURITY ACTIVE'}`);
    } catch (e) {
        console.error('Override toggle error:', e);
    }
}

function updateOverrideUI(active) {
    pcOverrideActive = active;
    const btn = document.getElementById('pc-override-btn');
    if (btn) {
        btn.innerHTML = active ? '<i class="fas fa-lock-open"></i> OVERRIDE: ON' : '<i class="fas fa-unlock"></i> OVERRIDE: OFF';
        btn.style.backgroundColor = active ? 'var(--danger)' : '';
        btn.style.color = active ? '#fff' : 'var(--danger)';
    }
}

async function sendPcShell() {
    const inp = document.getElementById('pc-shell-input');
    const out = document.getElementById('pc-shell-output');
    const cmd = inp.value.trim(); if (!cmd) return;
    inp.value = '';
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `<span class="log-ts">[${new Date().toLocaleTimeString()}]</span> <span class="log-lvl INFO">CMD</span> <span class="log-msg">PC Exec: ${cmd}</span>`;
    out.appendChild(entry);
    out.scrollTop = out.scrollHeight;

    try {
        const r = await fetch('/api/pc/command', {
            method: 'POST', headers: H,
            body: JSON.stringify({ cmd })
        });
        const d = await r.json();
        const resEntry = document.createElement('div');
        resEntry.className = 'log-entry';
        const color = d.success ? 'var(--success)' : 'var(--danger)';
        resEntry.innerHTML = `<span class="log-ts">[${new Date().toLocaleTimeString()}]</span> <span class="log-lvl INFO">RES</span> <span class="log-msg" style="color:${color}">${d.output || 'No output'}</span>`;
        out.appendChild(resEntry);
        out.scrollTop = out.scrollHeight;
    } catch (e) {
        addLog('ERROR', `PC Shell failed: ${e.message}`);
    }
}

async function refreshPcKnowledge() {
    const list = document.getElementById('pc-learning-list');
    try {
        const r = await fetch('/api/pc/knowledge?category=general', { headers: H });
        const d = await r.json();
        if (d.success && d.keys) {
            list.innerHTML = d.keys.slice(-10).reverse().map(k => `
                <div class="recent-item">
                    <i class="fas fa-brain" style="color:var(--accent)"></i>
                    <div style="display:flex; flex-direction:column;">
                        <span style="font-weight:700; font-size:0.8rem;">${k}</span>
                        <span style="font-size:0.7rem; opacity:0.6;">Pathway assimilated into Knowledge Base</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('KB Refresh error:', e);
    }
}

// ── LIVE MIRROR ───────────────────────────────────────
function startMirror() {
    mirrorActive = true;
    document.getElementById('mirror-status-txt').className = 'chip online';
    document.getElementById('mirror-status-txt').innerHTML = '<i class="fas fa-circle-dot" style="color:var(--danger)"></i> MIRRORING LIVE';
    document.getElementById('mirror-live-dot').style.display = 'block';
    document.getElementById('mirror-placeholder').style.display = 'none';
    frameCount = 0;
    const fpsEl = document.getElementById('mirror-fps');
    
    // Command the agent to start streaming
    sendCmd('mirror_start');

    // FPS counter
    fpsTimer = setInterval(() => {
        if (fpsEl) fpsEl.innerText = `${frameCount} FPS`;
        frameCount = 0;
    }, 1000);

    // Polling loop — fetch latest screenshot every 350ms
    mirrorInterval = setInterval(async () => {
        if (!mirrorActive) return;
        try {
            const r = await fetch('/api/screen/frame', { headers: H });
            if (!r.ok) return;
            const d = await r.json();
            if (d.key && d.key !== lastFrame) {
                lastFrame = d.key;
                frameCount++;
                const cleanKey = d.key.replace('local:', ''); // BUG#2 FIX
                const img = document.getElementById('mirror-img');
                img.style.display = 'block';
                img.src = `/api/asset/${cleanKey}?t=${Date.now()}`;
                document.getElementById('mirror-placeholder').style.display = 'none';
                // resolution hint
                if (d.width && d.height) document.getElementById('mirror-res').innerText = `${d.width}×${d.height}`;
            }
        } catch {}
    }, 500);
    addLog('SYSTEM', 'Live Mirror session started.');
}

function stopMirror() {
    mirrorActive = false;
    clearInterval(mirrorInterval);
    clearInterval(fpsTimer);
    document.getElementById('mirror-status-txt').className = 'chip offline';
    document.getElementById('mirror-status-txt').innerHTML = '<i class="fas fa-display-slash"></i> MIRROR OFFLINE';
    document.getElementById('mirror-live-dot').style.display = 'none';
    document.getElementById('mirror-placeholder').style.display = 'flex';
    addLog('SYSTEM', 'Live Mirror stopped.');
    
    // Command the agent to stop streaming
    sendCmd('mirror_stop');
}

function zoomMirror(delta) {
    mirrorZoom = Math.max(0.3, Math.min(3.0, mirrorZoom + delta));
    document.getElementById('device-shell').style.transform = `scale(${mirrorZoom})`;
    document.getElementById('zoom-level').innerText = `${Math.round(mirrorZoom * 100)}%`;
}

function resetZoom() { mirrorZoom = 1; document.getElementById('device-shell').style.transform = 'scale(1)'; document.getElementById('zoom-level').innerText = '100%'; }

async function toggleFullscreen() {
    const el = document.getElementById('panel-mirror');
    if (!document.fullscreenElement) {
        await el.requestFullscreen();
        document.getElementById('fs-btn').innerHTML = '<i class="fas fa-compress"></i> EXIT FS';
    } else {
        await document.exitFullscreen();
        document.getElementById('fs-btn').innerHTML = '<i class="fas fa-expand"></i> FULLSCREEN';
    }
}

document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
        document.getElementById('fs-btn').innerHTML = '<i class="fas fa-expand"></i> FULLSCREEN';
    }
});

// ── CAMERA CONTROL ────────────────────────────────────
function switchCamera(cam) {
    activeCam = cam;
    document.getElementById('btn-cam-back').style.color = cam === 'back' ? 'var(--accent)' : '';
    document.getElementById('btn-cam-front').style.color = cam === 'front' ? 'var(--accent)' : '';
    addLog('CMD', `Camera switched to: ${cam.toUpperCase()}`);
}

async function shootCamera(cam) {
    addLog('CMD', `Shooting ${cam.toUpperCase()} camera...`);
    await sendCmd(`camera_${cam}`);
    setTimeout(() => { refreshMedia(); updateRecentCaptures(); }, 4000);
}

async function recordAudio() {
    const dur = document.getElementById('audio-duration').value;
    addLog('CMD', `Starting audio recording: ${dur}s`);
    await sendCmd('audio_record', { duration: parseInt(dur) });

    // UI animation
    document.getElementById('rec-status').innerText = 'RECORDING...';
    document.getElementById('rec-status').style.color = 'var(--danger)';
    document.querySelectorAll('.viz-bar').forEach(b => b.classList.add('active'));
    recSeconds = 0;
    clearInterval(recInterval);
    recInterval = setInterval(() => {
        recSeconds++;
        const m = String(Math.floor(recSeconds / 60)).padStart(2, '0');
        const s = String(recSeconds % 60).padStart(2, '0');
        document.getElementById('rec-timer').innerText = `${m}:${s}`;
        if (recSeconds >= parseInt(dur)) stopAudio();
    }, 1000);
    setTimeout(() => { refreshMedia(); updateRecentCaptures(); }, parseInt(dur) * 1000 + 3000);
}

function stopAudio() {
    clearInterval(recInterval);
    document.getElementById('rec-status').innerText = 'STANDBY';
    document.getElementById('rec-status').style.color = '';
    document.querySelectorAll('.viz-bar').forEach(b => b.classList.remove('active'));
    addLog('CMD', 'Audio recording stopped.');
}

function updateRecentCaptures() {
    const list = document.getElementById('recent-captures');
    if (!list) return;
    const recent = mediaItems.slice(0, 5);
    list.innerHTML = recent.map(m => `
        <div class="recent-item" onclick="${m.type === 'audio' ? `openAudio('${m.key}')` : `openImage('/api/asset/${m.key}')`}">
            <i class="fas fa-${m.type === 'audio' ? 'music' : 'image'}"></i>
            <span>${m.key.substring(0, 20)}...</span>
        </div>`).join('');
}

// ── COMMANDS ─────────────────────────────────────────
async function sendCmd(type, extra = {}) {
    addLog('CMD', `Issuing: ${type.toUpperCase()}`);
    try {
        const r = await fetch('/api/command', {
            method: 'POST', headers: H,
            body: JSON.stringify({ target_device: 'REDMI_NOTE_14', action: { type, ...extra }, description: `Dashboard→${type}` })
        });
        const d = await r.json();
        const cid = d.command_id;
        if (!cid) return d;
        
        addLog('MESH', `Queued: ${cid.substring(0, 8)}`);

        // Wait for the mobile agent to execute and return result
        let attempts = 0;
        const pollResult = setInterval(async () => {
            attempts++;
            if (attempts > 20) { // 60 seconds timeout
                clearInterval(pollResult);
                addLog('ERROR', `Timeout waiting for ${type} result.`);
                return;
            }
            try {
                const resFetch = await fetch(`/api/command/result/${cid}`);
                if (!resFetch.ok) return;
                const cmdState = await resFetch.json();
                
                if (cmdState.status === 'done' && cmdState.result) {
                    clearInterval(pollResult);
                    const out = cmdState.result;
                    
                    if (out.success) {
                        addLog('SUCCESS', out.output || `${type} completed.`);
                        
                        // Handle GPS specifically
                        if (type === 'location' && out.data) {
                            const { lat, lon, accuracy } = out.data;
                            addLog('GPS', `📍 Location: ${lat}, ${lon} (±${accuracy}m)`);
                            const mapsUrl = `https://maps.google.com/?q=${lat},${lon}`;
                            addChatBubble('system', `📍 <b>GPS Trace Result:</b><br>Lat: ${lat}<br>Lon: ${lon}<br>Accuracy: ±${accuracy}m<br><a href="${mapsUrl}" target="_blank" style="color:var(--accent)">📌 Open in Maps</a>`);
                        }
                    } else {
                        addLog('ERROR', out.error || `${type} failed.`);
                    }
                }
            } catch (err) {}
        }, 3000); // Check every 3s
        
        return d;
    } catch (e) { addLog('ERROR', `Command failed: ${e.message}`); }
}

async function sendShell() {
    const inp = document.getElementById('shell-input');
    const cmd = inp.value.trim(); if (!cmd) return;
    inp.value = '';
    addLog('CMD', `SHELL: ${cmd}`);
    await sendCmd('shell', { cmd });
}

// ── AI CHAT ──────────────────────────────────────────
async function sendChatMsg() {
    const inp = document.getElementById('chat-input');
    const msg = inp.value.trim(); if (!msg) return;
    inp.value = '';
    addChatBubble('user', msg);
    const tid = 'typing-' + Date.now();
    addChatBubble('ai', '<i class="fas fa-spinner fa-spin"></i> Thinking...', tid);
    try {
        const r = await fetch('/api/brain/chat', {
            method: 'POST', headers: H,
            body: JSON.stringify({ message: msg, device_id: 'REDMI_NOTE_14' })
        });
        const d = await r.json();
        document.getElementById(tid)?.remove();
        addChatBubble('ai', d.response || 'No response.');
        if (d.provider) {
            document.getElementById('chat-provider-name').innerText = d.provider;
            document.getElementById('ai-engine-chip').innerHTML = `<i class="fas fa-robot"></i> ${d.provider}`;
            document.getElementById('ai-engine-chip').className = 'chip success';
        }
        if (d.autonomous_action) addLog('AI', `Auto action: ${d.autonomous_action.type}`);
    } catch (e) {
        document.getElementById(tid)?.remove();
        addChatBubble('ai', `[Error] ${e.message}`);
    }
}

function addChatBubble(role, text, id = null) {
    const win = document.getElementById('chat-window');
    if (!win) return;
    const d = document.createElement('div');
    d.className = `chat-msg ${role === 'user' ? 'user' : role === 'system' ? 'system' : 'ai'}`;
    if (id) d.id = id;
    d.innerHTML = `<div class="chat-bubble">${text}</div>`;
    win.appendChild(d);
    win.scrollTop = win.scrollHeight;
    if (role === 'ai' && !document.getElementById('nav-chat')?.classList.contains('active')) {
        const b = document.getElementById('chat-badge');
        if (b) { b.style.display = 'inline'; b.innerText = (parseInt(b.innerText) || 0) + 1; }
    }
}

document.getElementById('chat-input')?.addEventListener('keydown', e => { if (e.key === 'Enter') sendChatMsg(); });

// ── MEDIA VAULT ───────────────────────────────────────
function addMediaItem(item) {
    if (!mediaItems.find(m => m.key === item.key)) {
        mediaItems.unshift(item);
        const b = document.getElementById('media-badge');
        if (b && !document.getElementById('nav-media')?.classList.contains('active')) {
            b.style.display = 'inline'; b.innerText = (parseInt(b.innerText) || 0) + 1;
        }
    }
    updateRecentCaptures();
}

function switchMediaTab(btn, mode) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    mediaMode = mode;
    renderMedia();
}

async function refreshMedia() {
    try {
        const r = await fetch('/api/assets', { headers: H });
        if (!r.ok) return;
        const assets = await r.json();
        assets.forEach(a => {
            const type = /\.(mp3|m4a|aac|wav)$/i.test(a.key) ? 'audio' : 'screenshot';
            addMediaItem({ type, key: a.key, ts: new Date(a.uploaded || Date.now()).getTime() });
        });
        renderMedia();
    } catch (e) { addLog('ERROR', `Media refresh: ${e.message}`); }
}

function renderMedia() {
    const grid = document.getElementById('media-grid');
    const filtered = mediaItems.filter(m =>
        mediaMode === 'screenshots' ? m.type === 'screenshot' || m.type === 'image' :
        mediaMode === 'audio'       ? m.type === 'audio' : true);
    if (!filtered.length) {
        grid.innerHTML = '<div class="empty-state"><i class="fas fa-vault"></i><p>No media in vault.</p></div>';
        return;
    }
    grid.innerHTML = filtered.map(m => {
        const ts = new Date(m.ts).toLocaleString();
        const cleanKey = (m.key || '').replace('local:', ''); // BUG#2 FIX
        if (m.type === 'audio') return `
            <div class="audio-card" onclick="openAudio('${cleanKey}')">
                <i class="fas fa-music"></i>
                <div><div style="font-weight:700;font-size:.8rem;">${cleanKey.substring(0,22)}</div><div style="font-size:.65rem;color:var(--dim);">${ts}</div></div>
            </div>`;
        return `
            <div class="media-item" onclick="openImage('/api/asset/${cleanKey}')">
                <img src="/api/asset/${cleanKey}" alt="" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 1 1%22><rect fill=%22%23111%22/></svg>'">
                <div class="media-item-info"><span>${cleanKey.substring(0,18)}</span>${ts}</div>
            </div>`;
    }).join('');
}

function openImage(src) {
    const lb = document.getElementById('lightbox');
    document.getElementById('lb-img').src = src;
    document.getElementById('lb-img').style.display = 'block';
    document.getElementById('lb-audio').style.display = 'none';
    lb.classList.remove('hidden');
}

function openAudio(key) {
    const cleanKey = key.replace('local:', ''); // BUG#2 FIX
    const lb = document.getElementById('lightbox');
    document.getElementById('lb-img').style.display = 'none';
    const a = document.getElementById('lb-audio');
    a.src = `/api/asset/${cleanKey}`;
    a.style.display = 'block';
    a.load();
    a.play();
    lb.classList.remove('hidden');
}

// ── EVOLUTION PROPOSALS ───────────────────────────────
function checkEvos(cmds) {
    const evo = cmds.filter(c => /evolution|evolusi/i.test(c.description || '') && c.status === 'pending');
    let newCount = 0;
    evo.forEach(e => {
        if (!evoProposals.find(p => p.id === e.id)) {
            evoProposals.unshift({ id: e.id, title: e.description || 'Evolution Proposal', body: 'AI Agent has analysed operational patterns and submitted an evolution proposal for your approval.', ts: e.updated_at });
            newCount++;
        }
    });
    if (newCount > 0) {
        const b = document.getElementById('evo-badge');
        if (b && !document.getElementById('nav-evolution')?.classList.contains('active')) { b.style.display = 'inline'; b.innerText = evoProposals.length; }
        if (document.getElementById('panel-evolution')?.classList.contains('active')) renderEvolutions();
    }
}

function renderEvolutions() {
    const list = document.getElementById('evo-list');
    if (!evoProposals.length) { list.innerHTML = '<div class="empty-state"><i class="fas fa-dna"></i><p>No proposals yet.</p></div>'; return; }
    list.innerHTML = evoProposals.map(p => `
        <div class="evo-card" id="evo-${p.id}">
            <div class="evo-card-hd">
                <div class="evo-card-title"><i class="fas fa-dna" style="color:var(--purple)"></i> ${p.title}</div>
                <div class="evo-card-ts">${p.ts || '--'}</div>
            </div>
            <div class="evo-card-body">${p.body}</div>
            <div class="evo-actions">
                <button class="evo-btn approve" onclick="approveEvo('${p.id}')"><i class="fas fa-check"></i> Approve & Deploy</button>
                <button class="evo-btn reject" onclick="rejectEvo('${p.id}')"><i class="fas fa-x"></i> Reject</button>
            </div>
        </div>`).join('');
}

async function approveEvo(id) {
    addLog('SYSTEM', `Evolution approved: ${id}`);
    await sendCmd('apply_evolution', { evolution_id: id });
    evoProposals = evoProposals.filter(p => p.id !== id);
    renderEvolutions();
    addChatBubble('system', `Evolution ${id.substring(0,8)} approved and deployed.`);
}

function rejectEvo(id) { evoProposals = evoProposals.filter(p => p.id !== id); renderEvolutions(); }

async function triggerAutoUpdate() {
    addLog('SYSTEM', 'Auto-update triggered by operator.');
    await sendCmd('auto_update');
    addChatBubble('system', 'Auto-update command sent to Neural Agent.');
}

// ── LOG SYSTEM ────────────────────────────────────────
function addLog(level, msg) {
    allLogs.push({ ts: new Date().toLocaleTimeString(), level, msg });
    if (allLogs.length > 800) allLogs = allLogs.slice(-600);
    if (document.getElementById('panel-logs')?.classList.contains('active')) renderLogs();
}

function ingestLogs(logs) {
    logs.forEach(l => addLog(l.level || 'INFO', l.message || ''));
}

function renderLogs() {
    const con = document.getElementById('log-console');
    if (!con) return;
    if (!logVisible) { con.innerHTML = '<div style="text-align:center;color:var(--dim);padding:2rem;opacity:.4;">STEALTH MODE — Logs hidden</div>'; return; }
    const filter = document.getElementById('log-filter')?.value || 'all';
    const filtered = filter === 'all' ? allLogs : allLogs.filter(l => l.level === filter);
    con.innerHTML = filtered.slice(-300).map(l =>
        `<div class="log-entry"><span class="log-ts">[${l.ts}]</span><span class="log-lvl ${l.level}">${l.level}</span><span class="log-msg">${l.msg}</span></div>`
    ).join('');
    con.scrollTop = con.scrollHeight;
}

function filterLogs() { renderLogs(); }
function clearLogs() { allLogs = []; renderLogs(); }

async function toggleLogVisibility() {
    logVisible = !logVisible;
    const btn = document.getElementById('log-toggle-btn');
    btn.innerHTML = logVisible ? '<i class="fas fa-eye"></i> VISIBLE' : '<i class="fas fa-eye-slash"></i> HIDDEN';
    btn.style.color = logVisible ? '' : 'var(--danger)';
    addLog('SYSTEM', `Log stealth: ${logVisible ? 'OFF' : 'ON'}`);
    await fetch('/api/log-visibility', { method: 'POST', headers: H, body: JSON.stringify({ visible: logVisible }) });
    renderLogs();
}

function exportLogs() {
    const blob = new Blob([allLogs.map(l => `[${l.ts}] ${l.level}: ${l.msg}`).join('\n')], { type: 'text/plain' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `noir_logs_${Date.now()}.txt`; a.click();
}

// ── BOOT ─────────────────────────────────────────────
window.addEventListener('load', () => {
    addLog('SYSTEM', 'NOIR SOVEREIGN MISSION CONTROL V21.0.3 — INITIALIZED (BUG#1-7 FIXED)');
    addChatBubble('system', 'NOIR AI AGENT V21.0.3 — ONLINE. Mirror, Camera, Audio, GPS: FIXED.');
    poll();
    setInterval(poll, 4000);
    setTimeout(refreshMedia, 2000);
    // Auto-refresh media every 15s to catch new uploads
    setInterval(refreshMedia, 15000);
});
