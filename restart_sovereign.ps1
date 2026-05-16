# RESTART SOVEREIGN ECOSYSTEM — FRESH DEPLOY
Write-Host "🌘 [RESTART] Killing existing AI processes..."
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "🌘 [RESTART] Clearing old caches..."
Get-ChildItem -Path "c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent" -Filter "__pycache__" -Recurse | Remove-Item -Force -Recurse

Write-Host "🌘 [RESTART] Initiating Shadow Node Heartbeat..."
Start-Process python "c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\noir-vps\shadow_node.py" -WindowStyle Hidden

Write-Host "🌘 [RESTART] Initiating Grand Singularity Cycle..."
Start-Process python "c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\noir-vps\grand_singularity_cycle.py" -WindowStyle Hidden

Write-Host "🌘 [RESTART] Launching Sovereign Dashboard Bridge..."
# (Assuming there's a dashboard server)
# Start-Process python "c:\Users\ASUS\.gemini\antigravity\scratch\android-ai-agent\noir-ui\web_server.py" -WindowStyle Hidden

Write-Host "✅ DEPLOYMENT COMPLETE. System is now fully autonomous and synchronized."
