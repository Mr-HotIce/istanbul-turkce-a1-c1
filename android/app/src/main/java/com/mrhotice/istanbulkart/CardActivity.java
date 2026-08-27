package com.mrhotice.istanbulkart;

import android.app.Activity;
import android.app.KeyguardManager;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.text.SpannableString;
import android.text.Spanned;
import android.text.style.ForegroundColorSpan;
import android.view.GestureDetector;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import java.util.List;

public class CardActivity extends Activity {
    private Card card;
    private boolean revealed;
    private TextView hint, ipa, ruphon, russian;
    private TableLayout petrov;
    private GestureDetector gestures;

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
        Notification n = b.setContentTitle("Petrov Fiiller")
                .setContentText("Kart")
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
        petrov = findViewById(R.id.petrov);
        findViewById(R.id.cardBody).setOnClickListener(v -> reveal());
        findViewById(R.id.word).setOnClickListener(v -> reveal());
        ((Button) findViewById(R.id.btnClose)).setOnClickListener(v -> finish());
        gestures = new GestureDetector(this, new GestureDetector.SimpleOnGestureListener() {
            @Override
            public boolean onDown(MotionEvent e) {
                return true;
            }

            @Override
            public boolean onFling(MotionEvent e1, MotionEvent e2, float vx, float vy) {
                if (e1 == null || e2 == null) return false;
                float dx = e2.getX() - e1.getX();
                float dy = e2.getY() - e1.getY();
                if (dx > 120 && Math.abs(dx) > Math.abs(dy) && vx > 250) {
                    loadCard();
                    return true;
                }
                return false;
            }
        });
        loadCard();
    }

    @Override
    public boolean dispatchTouchEvent(MotionEvent ev) {
        if (gestures != null) gestures.onTouchEvent(ev);
        return super.dispatchTouchEvent(ev);
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
        ((TextView) findViewById(R.id.meta)).setText("глагол  ·  " + card.level + "  ·  я");
        hint.setVisibility(View.VISIBLE);
        ipa.setVisibility(View.GONE);
        ruphon.setVisibility(View.GONE);
        russian.setVisibility(View.GONE);
        if (petrov != null) {
            petrov.setVisibility(View.GONE);
            petrov.removeAllViews();
        }
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
        if (card.russian != null && !card.russian.isEmpty()
                && !"(нет перевода)".equals(card.russian)) {
            russian.setText(card.russian);
            russian.setVisibility(View.VISIBLE);
        }
        fillPetrov();
        if (petrov != null) petrov.setVisibility(View.VISIBLE);
    }

    private void fillPetrov() {
        if (petrov == null) return;
        petrov.removeAllViews();
        TableRow head = new TableRow(this);
        head.addView(cell("", true, 0));
        head.addView(cell("вопрос\n?", true, 1));
        head.addView(cell("да\n+", true, 2));
        head.addView(cell("нет\n−", true, 3));
        petrov.addView(head);
        List<Petrov.Row> rows = Petrov.table(card);
        for (Petrov.Row r : rows) {
            TableRow tr = new TableRow(this);
            tr.addView(cell(r.label, true, 0));
            tr.addView(cell(r.q, false, 1));
            tr.addView(cell(r.a, false, 2));
            tr.addView(cell(r.n, false, 3));
            petrov.addView(tr);
        }
    }

    private TextView cell(String text, boolean bold, int kind) {
        TextView tv = new TextView(this);
        SpannableString sp = new SpannableString(text);
        int ink = getResources().getColor(R.color.ink);
        int phon = getResources().getColor(R.color.phon);
        int ru = getResources().getColor(R.color.ru);
        int a = text.indexOf('[');
        int b = text.indexOf(']');
        if (a >= 0 && b > a) {
            sp.setSpan(new ForegroundColorSpan(ink), 0, a, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            sp.setSpan(new ForegroundColorSpan(phon), a, b + 1, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            if (b + 1 < text.length()) {
                sp.setSpan(new ForegroundColorSpan(ru), b + 1, text.length(), Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
            }
        }
        tv.setText(sp);
        tv.setTextSize(kind == 0 ? 10.5f : 10f);
        tv.setPadding(5, 7, 5, 7);
        tv.setGravity(kind == 0 ? Gravity.CENTER : Gravity.START);
        tv.setTextColor(ink);
        if (bold) tv.setTypeface(Typeface.DEFAULT_BOLD);
        int bg = R.drawable.badge_bg;
        if (kind == 1) bg = R.drawable.cell_q;
        else if (kind == 2) bg = R.drawable.cell_a;
        else if (kind == 3) bg = R.drawable.cell_n;
        tv.setBackgroundResource(bg);
        return tv;
    }
}
