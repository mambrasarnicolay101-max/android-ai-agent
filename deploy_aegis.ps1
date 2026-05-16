# ============================================================
#  NOIR SOVEREIGN — BUILD & DEPLOY v2.0
#  Build debug APK lalu install ke Redmi Note 14
# ============================================================
$ADB     = "C:\Users\ASUS\platform-tools\adb.exe"
$USB_ID  = "9LMBAUR4A6QG5TWW"
$WIFI_ID = "192.168.1.32:5555"
$PROJECT = "$PSScriptRoot\noir-android-native"
$APK     = "$PROJECT\app\build\outputs\apk\debug\app-debug.apk"
$PKG     = "com.noir.aegis"
$MAIN    = ".MainActivity"

function Banner($msg) { Write-Host "`n[$msg]" -ForegroundColor Cyan }
function OK($msg)     { Write-Host "  ✅ $msg" -ForegroundColor Green }
function ERR($msg)    { Write-Host "  ❌ $msg" -ForegroundColor Red; exit 1 }

# Pilih target device (USB diutamakan)
$devOut = & $ADB devices
if ($devOut -match $USB_ID) { $TARGET = $USB_ID; OK "Target: USB ($USB_ID)" }
elseif ($devOut -match "192.168.1.32") { $TARGET = $WIFI_ID; OK "Target: WiFi ($WIFI_ID)" }
else { ERR "Tidak ada device terdeteksi! Jalankan adb_setup.ps1 dulu." }

Banner "STEP 1 — Set ANDROID_HOME"
$sdkPaths = @(
    "$env:LOCALAPPDATA\Android\Sdk",
    "C:\Users\ASUS\AppData\Local\Android\Sdk",
    "C:\Android\sdk"
)
foreach ($p in $sdkPaths) {
    if (Test-Path $p) { $env:ANDROID_HOME = $p; OK "ANDROID_HOME = $p"; break }
}
if (-not $env:ANDROID_HOME) { WARN "ANDROID_HOME tidak ditemukan. Build mungkin gagal." }
$env:PATH += ";$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\build-tools\34.0.0"

Banner "STEP 2 — Build APK"
Set-Location $PROJECT
$buildResult = & cmd /c "gradlew.bat assembleDebug 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Host $buildResult -ForegroundColor Red
    ERR "Build gagal! Lihat error di atas."
}
OK "Build berhasil"

Banner "STEP 3 — Verify APK"
if (-not (Test-Path $APK)) { ERR "APK tidak ditemukan di: $APK" }
$size = (Get-Item $APK).Length / 1MB
OK "APK ditemukan: $([math]::Round($size,1)) MB"

Banner "STEP 4 — Uninstall Lama (jika ada)"
& $ADB -s $TARGET shell "pm list packages $PKG" | ForEach-Object {
    if ($_ -match $PKG) {
        & $ADB -s $TARGET uninstall $PKG
        OK "APK lama diuninstall"
    }
}

Banner "STEP 5 — Install APK"
$installOut = & $ADB -s $TARGET install -r -g $APK
Write-Host "  $installOut"
if ($installOut -match "Success") { OK "Install berhasil!" }
else { ERR "Install gagal: $installOut" }

Banner "STEP 6 — Launch App"
& $ADB -s $TARGET shell "am start -n ${PKG}/${MAIN}"
Start-Sleep 2
OK "App diluncurkan"

Banner "STEP 7 — Grant Shizuku Permission via ADB"
& $ADB -s $TARGET shell "sh /sdcard/Android/data/moe.shizuku.privileged.api/start.sh" 2>$null
& $ADB -s $TARGET shell "pm grant $PKG android.permission.READ_PHONE_STATE" 2>$null
OK "Permissions granted"

Banner "STEP 8 — Logcat Monitor (5 detik)"
$job = Start-Job { & $using:ADB -s $using:TARGET logcat -s "NeuralLink:V" "AegisService:V" "MainActivity:V" }
Start-Sleep 5
Stop-Job $job
$logs = Receive-Job $job
Write-Host $logs -ForegroundColor Gray
Remove-Job $job

Banner "DEPLOY SELESAI ✅"
Write-Host "`n  APK terinstall dan berjalan di device." -ForegroundColor White
Write-Host "  Monitor log: $ADB -s $TARGET logcat -s NeuralLink AegisService" -ForegroundColor Yellow
