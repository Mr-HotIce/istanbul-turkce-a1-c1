package com.mrhotice.istanbulkart;

import android.app.Activity;
import android.app.KeyguardManager;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

public class CardActivity extends Activity {
    private Card card;
    private boolean revealed;
    private TextView hint, ipa, ruphon, russian;

    public static void show(Context c) {
        Intent i = new Intent(c, CardActivity.class);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK
                | Intent.FLAG_ACTIVITY_CLEAR_TOP
                | Intent.FLAG_ACTIVITY_NO_USER_ACTION);
        try {
            c.startActivity(i);
        } catch (Exception e) {
            fireFullScreen(c);
        }
    }

    public static void fireFullScreen(Context c) {
        Intent i = new Intent(c, CardActivity.class);
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pi = PendingIntent.getActivity(
                c, 7, i, PendingIntent.FLAG_UPDATE_CURRENT | UnlockService.immutable());
        Notification.Builder b;
        if (Build.VERSION.SDK_INT >= 26) {
            b = new Notification.Builder(c, UnlockService.CH_CARD);
        } else {
            b = new Notification.Builder(c);
        }
        Notification n = b.setContentTitle("İstanbul Kartlar")
                .setContentText("Карточка")
                .setSmallIcon(R.drawable.ic_stat)
                .setPriority(Notification.PRIORITY_HIGH)
                .setCategory(Notification.CATEGORY_ALARM)
                .setFullScreenIntent(pi, true)
                .setAutoCancel(true)
                .build();
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        nm.notify(99, n);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setupLockFlags();
        setContentView(R.layout.activity_card);
        hint = findViewById(R.id.hint);
        ipa = findViewById(R.id.ipa);
        ruphon = findViewById(R.id.ruphon);
        russian = findViewById(R.id.russian);
        findViewById(R.id.cardBody).setOnClickListener(v -> reveal());
        findViewById(R.id.word).setOnClickListener(v -> reveal());
        ((Button) findViewById(R.id.btnClose)).setOnClickListener(v -> finish());
        ((Button) findViewById(R.id.btnNext)).setOnClickListener(v -> loadCard());
        loadCard();
    }

    private void setupLockFlags() {
        if (Build.VERSION.SDK_INT >= 27) {
            setShowWhenLocked(true);
            setTurnScreenOn(true);
            KeyguardManager km = (KeyguardManager) getSystemService(KEYGUARD_SERVICE);
            if (km != null) km.requestDismissKeyguard(this, null);
        } else {
            getWindow().addFlags(
                    WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED
                            | WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
                            | WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD
                            | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        }
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }

    private void loadCard() {
        CardStore store = CardStore.get(this);
        String lvl = Prefs.levelFilter(this);
        int size = store.size(lvl);
        card = store.get(Prefs.nextIndex(this, size), lvl);
        Prefs.bumpShown(this);
        revealed = false;
        bind();
    }

    private void bind() {
        if (card == null) {
            ((TextView) findViewById(R.id.word)).setText("kart yok");
            return;
        }
        ((TextView) findViewById(R.id.word)).setText(card.word);
        ((TextView) findViewById(R.id.meta)).setText("Türkçe  ·  " + card.level);
        hint.setVisibility(View.VISIBLE);
        ipa.setVisibility(View.GONE);
        ruphon.setVisibility(View.GONE);
        russian.setVisibility(View.GONE);
        View petrov = findViewById(R.id.petrov);
        if (petrov != null) petrov.setVisibility(View.GONE);
    }

    private void reveal() {
        if (card == null) return;
        revealed = true;
        hint.setVisibility(View.GONE);
        if (card.ipa != null && !card.ipa.isEmpty()) {
            ipa.setText(card.ipa);
            ipa.setVisibility(View.VISIBLE);
        }
        if (card.transcription != null && !card.transcription.isEmpty()) {
            ruphon.setText("[" + card.transcription + "]");
            ruphon.setVisibility(View.VISIBLE);
        }
        if (card.russian != null && !card.russian.isEmpty()) {
            russian.setText(card.russian);
            russian.setVisibility(View.VISIBLE);
        }
    }
}
