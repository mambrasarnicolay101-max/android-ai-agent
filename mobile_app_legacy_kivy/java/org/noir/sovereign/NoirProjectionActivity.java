package org.noir.sovereign;

import android.app.Activity;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;

/**
 * NoirProjectionActivity - Transparent trampoline activity
 * Required to get the user's one-time MediaProjection permission grant.
 * It is launched by Python, gets the permission silently, then exits.
 * On Android 10+, the system dialog is shown once; the token is stored.
 */
public class NoirProjectionActivity extends Activity {
    public static final int REQUEST_CODE = 1001;
    public static final String PREFS = "noir_prefs";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Make the activity fully transparent (theme declared in manifest)
        MediaProjectionManager mgr =
            (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
        startActivityForResult(mgr.createScreenCaptureIntent(), REQUEST_CODE);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQUEST_CODE) {
            if (resultCode == RESULT_OK && data != null) {
                // Store permission grant and forward to service
                Intent svc = new Intent(this, NoirNativeService.class);
                svc.setAction(NoirNativeService.ACTION_MIRROR_START);
                svc.putExtra(NoirNativeService.EXTRA_RESULT_CODE, resultCode);
                svc.putExtra(NoirNativeService.EXTRA_RESULT_DATA, data);
                startForegroundService(svc);
                // Persist grant indicator
                getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                    .putInt("projection_result_code", resultCode).apply();
            }
            finish();
        }
    }
}
