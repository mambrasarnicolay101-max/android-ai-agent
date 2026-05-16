# ============================================================
#  NOIR SOVEREIGN - ADB SETUP & DIAGNOSIS v2.1
#  Reset total + aktifkan WiFi TCP + verifikasi Shizuku
# ============================================================
$ADB    = "C:\Users\ASUS\platform-tools\adb.exe"
$USB_ID = "9LMBAUR4A6QG5TWW"
$DEV_IP = "192.168.1.32"
$PORT   = "5555"
$PKG    = "com.noir.aegis"

function Banner($msg) { Write-Host "`n[$msg]" -ForegroundColor Cyan }
function OK($msg)     { Write-Host "  [OK] $msg" -ForegroundColor Green }
function WARN($msg)   { Write-Host "  [!!] $msg" -ForegroundColor Yellow }
function ERR($msg)    { Write-Host "  [XX] $msg" -ForegroundColor Red }

Banner "STEP 1 - ADB Server Reset"
& $ADB kill-server; Start-Sleep 1
& $ADB start-server; Start-Sleep 1
OK "ADB server restarted"

Banner "STEP 2 - Device List"
$devOut = & $ADB devices -l
Write-Host $devOut
if ($devOut -notmatch $USB_ID) {
    ERR "USB device NOT found! Cek kabel dan USB Debugging."
    exit 1
}
OK "USB device ditemukan: $USB_ID"

Banner "STEP 3 - Enable TCP/IP on Port $PORT"
& $ADB -s $USB_ID tcpip $PORT
Start-Sleep 3
OK "tcpip mode enabled"

Banner "STEP 4 - Connect via WiFi"
$connOut = & $ADB connect "${DEV_IP}:${PORT}"
Write-Host $connOut
if ($connOut -match "connected") {
    OK "WiFi connected: ${DEV_IP}:${PORT}"
} else {
    WARN "WiFi connect gagal, coba lagi..."
    Start-Sleep 2
    $connOut2 = & $ADB connect "${DEV_IP}:${PORT}"
    Write-Host $connOut2
}

Banner "STEP 5 - Verify All Devices"
& $ADB devices -l

Banner "STEP 6 - Shizuku Status"
$shizPkg = & $ADB -s $USB_ID shell "pm list packages moe.shizuku.privileged.api 2>/dev/null"
if ($shizPkg -match "shizuku") {
    OK "Shizuku terinstall"
    $shizVer = & $ADB -s $USB_ID shell "dumpsys package moe.shizuku.privileged.api | grep versionName"
    Write-Host "    Version:$shizVer"
    $shizProc = & $ADB -s $USB_ID shell "ps -A | grep shizuku"
    if ($shizProc -match "shizuku_server") {
        OK "Shizuku SERVER aktif dan berjalan"
    } else {
        WARN "Shizuku diinstall tapi server belum aktif - buka Shizuku di HP lalu tekan Start"
    }
} else {
    ERR "Shizuku tidak terinstall!"
}

Banner "STEP 7 - Noir Aegis APK Status"
$noirPkg = & $ADB -s $USB_ID shell "pm list packages $PKG 2>/dev/null"
if ($noirPkg -match $PKG) {
    OK "Noir Aegis APK terinstall"
} else {
    WARN "Noir Aegis belum terinstall. Jalankan deploy_aegis.ps1"
}

Banner "STEP 8 - Network Info"
$ip = & $ADB -s $USB_ID shell "ip route | grep wlan"
Write-Host "  Network: $ip"
$ping = & $ADB -s $USB_ID shell "ping -c 1 -W 2 "+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+" 2>/dev/null | grep bytes"
if ($ping) {
    OK "VPS "+os.environ.get("NOIR_VPS_IP", "8.215.23.17")+" dapat di-ping dari device"
} else {
    WARN "VPS tidak dapat di-ping (mungkin firewall atau VPS offline)"
}

Banner "STEP 9 - Grant ADB Permissions to Shizuku"
& $ADB -s $USB_ID shell "pm grant moe.shizuku.privileged.api android.permission.INTERACT_ACROSS_USERS_FULL" 2>$null
& $ADB -s $USB_ID shell "appops set moe.shizuku.privileged.api INTERACT_ACROSS_USERS allow" 2>$null
OK "Shizuku permissions applied"

Banner "SETUP SELESAI"
Write-Host "`n  USB ID  : $USB_ID" -ForegroundColor White
Write-Host "  WiFi    : ${DEV_IP}:${PORT}" -ForegroundColor White
Write-Host "`n  Jalankan deploy_aegis.ps1 untuk build & install APK" -ForegroundColor Yellow
