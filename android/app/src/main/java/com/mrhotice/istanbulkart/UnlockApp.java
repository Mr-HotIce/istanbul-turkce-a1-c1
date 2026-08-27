package com.mrhotice.istanbulkart;

import android.app.Application;

public class UnlockApp extends Application {
    @Override
    public void onCreate() {
        super.onCreate();
        CardStore.get(this);
        if (Prefs.isEnabled(this)) {
            UnlockService.start(this);
        }
    }
}
