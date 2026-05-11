import os
import json
import logging
from datetime import datetime

log = logging.getLogger("SovereignWiki")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SovereignWiki:
    """
    Generator Wiki Otonom v1.0 — NOIR SOVEREIGN
    ===========================================
    Mengubah riwayat evolusi, pembelajaran, dan simulasi keamanan menjadi
    dokumentasi visual yang premium dan mudah dipantau oleh User.
    """
    WIKI_FILE = os.path.join(os.path.dirname(__file__), "..", "noir-ui", "wiki.html")
    EVO_HISTORY = os.path.join(os.path.dirname(__file__), "..", "knowledge", "evolution", "evolution_history.json")

    @staticmethod
    def generate_wiki():
        log.info("[WIKI] Generating Sovereign Wiki update...")
        
        # Load history
        history = []
        if os.path.exists(SovereignWiki.EVO_HISTORY):
            try:
                with open(SovereignWiki.EVO_HISTORY, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                log.error(f"[WIKI] Error loading history: {e}")

        # Sort by timestamp reverse (terbaru di atas)
        try:
            history.sort(key=lambda x: x.get("applied_at", x.get("timestamp", "")), reverse=True)
        except:
            pass

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOVEREIGN AEGIS — KNOWLEDGE WIKI</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0a0a0c;
            --card: #121215;
            --accent: #a855f7;
            --accent-glow: rgba(168, 85, 247, 0.4);
            --text: #e2e8f0;
            --dim: #94a3b8;
            --border: #1f2937;
            --success: #22c55e;
            --font-mono: 'JetBrains Mono', monospace;
        }
        * { box-sizing: border-box; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
            overflow-x: hidden;
        }
        body::-webkit-scrollbar { width: 6px; }
        body::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

        .header {
            border-bottom: 1px solid var(--border);
            padding-bottom: 2rem;
            margin-bottom: 3rem;
            position: relative;
        }
        .header h1 {
            margin: 0;
            font-weight: 800;
            font-size: 2.2rem;
            letter-spacing: -1.5px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .header h1 i { color: var(--accent); filter: drop-shadow(0 0 8px var(--accent-glow)); }
        .header p {
            color: var(--dim);
            margin: 0.75rem 0 0 0;
            font-size: 1rem;
            font-weight: 400;
        }
        .stats-strip {
            display: flex;
            gap: 2rem;
            margin-top: 1.5rem;
        }
        .stat-item {
            display: flex;
            flex-direction: column;
        }
        .stat-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; color: var(--dim); }
        .stat-value { font-size: 1.1rem; font-weight: 700; color: var(--accent); font-family: var(--font-mono); }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
            gap: 2rem;
        }
        .entry {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.75rem;
            position: relative;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
        }
        .entry:hover {
            border-color: var(--accent);
            transform: translateY(-4px);
            box-shadow: 0 12px 24px -10px rgba(0,0,0,0.5);
        }
        .entry-title {
            font-weight: 700;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
        }
        .status-badge {
            font-size: 0.6rem;
            padding: 3px 10px;
            border-radius: 20px;
            background: rgba(168, 85, 247, 0.1);
            color: var(--accent);
            border: 1px solid rgba(168, 85, 247, 0.2);
            font-family: var(--font-mono);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }
        .timestamp {
            font-size: 0.75rem;
            color: var(--dim);
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .desc {
            font-size: 0.92rem;
            color: var(--dim);
            margin-bottom: 1.5rem;
            flex-grow: 1;
        }
        .code-block {
            background: #000;
            padding: 1.25rem;
            border-radius: 10px;
            font-family: var(--font-mono);
            font-size: 0.8rem;
            overflow-x: auto;
            border: 1px solid #1a1a1a;
            position: relative;
        }
        .code-block::before {
            content: "MUTATION_DATA";
            position: absolute;
            top: 0; right: 1rem;
            font-size: 0.6rem;
            color: #333;
            font-weight: 800;
        }
        pre { margin: 0; color: #a5b4fc; }
        .no-data {
            grid-column: 1 / -1;
            text-align: center;
            padding: 6rem 2rem;
            background: rgba(255,255,255,0.02);
            border: 1px dashed var(--border);
            border-radius: 20px;
            color: var(--dim);
        }
        .tag {
            display: inline-block;
            font-size: 0.65rem;
            color: var(--accent);
            margin-top: 1rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-book-atlas"></i> SOVEREIGN WIKI</h1>
        <p>Repository otonom yang mencatat setiap evolusi, mitigasi keamanan, dan kecerdasan baru yang diserap oleh AI.</p>
        <div class="stats-strip">
            <div class="stat-item">
                <span class="stat-label">Total Lessons</span>
                <span class="stat-value">{total_count}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Last Evolution</span>
                <span class="stat-value">{last_update}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Stability</span>
                <span class="stat-value" style="color:var(--success)">OPTIMAL</span>
            </div>
        </div>
    </div>
    <div class="grid">
        {entries}
    </div>
</body>
</html>
"""
        entries_html = ""
        total_lessons = len(history)
        last_update = "N/A"
        
        if not history:
            entries_html = '<div class="no-data"><i class="fas fa-ghost fa-3x" style="margin-bottom:1rem; opacity:0.3;"></i><br>Belum ada data evolusi yang tercatat. Jalankan simulasi arena atau biarkan AI melakukan penelitian otonom.</div>'
        else:
            last_update = history[0].get("applied_at", history[0].get("timestamp", "N/A"))[:16].replace("T", " ")
            for item in history:
                title = item.get("title", "Untitled Evolution")
                desc = item.get("description", "No description available.")
                ts = item.get("applied_at", item.get("timestamp", "Unknown Time")).replace("T", " ")[:16]
                status = item.get("status", "UNKNOWN")
                
                # Format changes for the wiki
                changes_json = json.dumps(item.get("changes", {}), indent=2)
                
                entries_html += f"""
                <div class="entry">
                    <div class="entry-title">
                        {title}
                        <span class="status-badge">{status}</span>
                    </div>
                    <div class="timestamp"><i class="far fa-calendar-alt"></i> {ts}</div>
                    <div class="desc">{desc}</div>
                    <div class="code-block">
                        <pre>{changes_json}</pre>
                    </div>
                    <div class="tag">#SOVEREIGN_EVOLUTION</div>
                </div>
                """

        full_html = html_template.replace("{entries}", entries_html)\
                                 .replace("{total_count}", str(total_lessons))\
                                 .replace("{last_update}", last_update)
        
        try:
            with open(SovereignWiki.WIKI_FILE, "w", encoding="utf-8") as f:
                f.write(full_html)
            log.info(f"[WIKI] Wiki updated successfully.")
        except Exception as e:
            log.error(f"[WIKI] Failed to write wiki file: {e}")

if __name__ == "__main__":
    SovereignWiki.generate_wiki()
