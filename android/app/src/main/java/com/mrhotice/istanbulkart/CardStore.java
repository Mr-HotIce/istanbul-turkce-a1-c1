package com.mrhotice.istanbulkart;

import android.content.Context;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public final class CardStore {
    private static CardStore instance;
    private final List<Card> all = new ArrayList<>();

    public static synchronized CardStore get(Context c) {
        if (instance == null) {
            instance = new CardStore(c.getApplicationContext());
        }
        return instance;
    }

    private CardStore(Context c) {
        try {
            InputStream in = c.getAssets().open("cards.json");
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
            in.close();
            JSONArray arr = new JSONArray(new String(out.toByteArray(), StandardCharsets.UTF_8));
            for (int i = 0; i < arr.length(); i++) {
                JSONObject o = arr.getJSONObject(i);
                all.add(new Card(
                        o.optString("w"),
                        o.optString("ru"),
                        o.optString("tr"),
                        o.optString("ipa"),
                        o.optString("lvl")
                ));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public int size() {
        return all.size();
    }

    public int size(String level) {
        if (level == null || level.isEmpty() || "ALL".equals(level)) return all.size();
        int n = 0;
        for (Card c : all) if (level.equals(c.level)) n++;
        return n;
    }

    public Card get(int index) {
        if (all.isEmpty()) return null;
        int i = index % all.size();
        if (i < 0) i += all.size();
        return all.get(i);
    }

    public Card get(int index, String level) {
        if (level == null || level.isEmpty() || "ALL".equals(level)) return get(index);
        List<Card> sub = new ArrayList<>();
        for (Card c : all) if (level.equals(c.level)) sub.add(c);
        if (sub.isEmpty()) return get(index);
        int i = index % sub.size();
        if (i < 0) i += sub.size();
        return sub.get(i);
    }
}
