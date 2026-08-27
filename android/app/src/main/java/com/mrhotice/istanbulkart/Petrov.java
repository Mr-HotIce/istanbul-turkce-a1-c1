package com.mrhotice.istanbulkart;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** 9-cell table after Dmitry Petrov: gelecek / şimdi / geçmiş × ? / + / − (ben). */
public final class Petrov {
    private Petrov() {}

    private static final String VOWELS = "aeıioöuü";
    private static final String FRONT = "eiöü";
    private static final String ROUNDED = "oöuü";
    private static final String VOICELESS = "pçtkfsşh";

    public static class Row {
        public final String label;
        public final String q;
        public final String a;
        public final String n;

        Row(String label, String q, String a, String n) {
            this.label = label;
            this.q = q;
            this.a = a;
            this.n = n;
        }
    }

    public static List<Row> table(Card c) {
        String inf = c == null || c.word == null ? "" : c.word.trim();
        Forms f = conjugate(inf);
        List<Row> rows = new ArrayList<>();
        if (f == null) {
            rows.add(new Row("—", "—", inf, "—"));
            return rows;
        }
        String ru = gloss(c);
        String bit = ru.isEmpty() ? "…" : ru;
        rows.add(new Row("будущее",
                pair(f.gelecekQ, "буду ли я " + bit + "?"),
                pair(f.gelecekA, "я буду " + bit),
                pair(f.gelecekN, "я не буду " + bit)));
        rows.add(new Row("настоящее",
                pair(f.simdiQ, bit + " ли я?"),
                pair(f.simdiA, "я " + bit),
                pair(f.simdiN, "я не " + bit)));
        rows.add(new Row("прошедшее",
                pair(f.gecmisQ, bit + " ли я (прош.)?"),
                pair(f.gecmisA, "я " + bit + " (прош.)"),
                pair(f.gecmisN, "я не " + bit + " (прош.)")));
        return rows;
    }

    static String gloss(Card c) {
        if (c == null || c.russian == null) return "";
        String s = c.russian.trim();
        if (s.isEmpty() || s.startsWith("(нет") || s.startsWith("-ать") || s.startsWith("-еть")) {
            return "";
        }
        int cut = indexOfAny(s, ";,");
        if (cut > 0) s = s.substring(0, cut).trim();
        s = s.replace("пассивный", "").replace("каузатив", "").replace("каузативный залог", "").trim();
        if (s.length() < 2) return "";
        return s;
    }

    private static int indexOfAny(String s, String chars) {
        int best = -1;
        for (int i = 0; i < chars.length(); i++) {
            int p = s.indexOf(chars.charAt(i));
            if (p >= 0 && (best < 0 || p < best)) best = p;
        }
        return best;
    }

    private static String pair(String tr, String ru) {
        return tr + "\n[" + transcribe(tr) + "]\n" + ru;
    }

    /** Cyrillic pronunciation, same mapping as istanbul_verbs.csv. */
    static String transcribe(String s) {
        if (s == null || s.isEmpty()) return "";
        StringBuilder sb = new StringBuilder();
        boolean wordStart = true;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch == ' ' || ch == '\n' || ch == '\t') {
                sb.append(' ');
                wordStart = true;
                continue;
            }
            if (ch == '?' || ch == '!' || ch == '.' || ch == ',' || ch == '-' || ch == '\'') {
                sb.append(ch);
                continue;
            }
            char low;
            if (ch == 'I') low = 'ı';
            else if (ch == 'İ') low = 'i';
            else low = Character.toLowerCase(ch);
            if (low == 'ğ') {
                wordStart = false;
                continue;
            }
            sb.append(cyr(low, wordStart));
            wordStart = false;
        }
        return sb.toString().trim();
    }

    private static String cyr(char c, boolean wordStart) {
        switch (c) {
            case 'a': case 'â': return "а";
            case 'e': return wordStart ? "э" : "е";
            case 'ı': return "ы";
            case 'i': case 'î': return "и";
            case 'o': return "о";
            case 'ö': return "ё";
            case 'u': case 'û': return "у";
            case 'ü': return "ю";
            case 'b': return "б";
            case 'c': return "дж";
            case 'ç': return "ч";
            case 'd': return "д";
            case 'f': return "ф";
            case 'g': return "г";
            case 'h': return "х";
            case 'j': return "ж";
            case 'k': return "к";
            case 'l': return "л";
            case 'm': return "м";
            case 'n': return "н";
            case 'p': return "п";
            case 'r': return "р";
            case 's': return "с";
            case 'ş': return "ш";
            case 't': return "т";
            case 'v': return "в";
            case 'y': return "й";
            case 'z': return "з";
            default: return String.valueOf(c);
        }
    }

    static final class Forms {
        String gelecekQ, gelecekA, gelecekN;
        String simdiQ, simdiA, simdiN;
        String gecmisQ, gecmisA, gecmisN;
    }

    static Forms conjugate(String word) {
        String[] sp = splitInf(word);
        String prefix = sp[0];
        String inf = sp[1];
        String low = inf.toLowerCase(Locale.ROOT);
        if (low.endsWith("mamak") || low.endsWith("memek")) return null;
        if (!(low.endsWith("mak") || low.endsWith("mek"))) return null;

        String yor, yneg, fut, fneg, past, pneg;

        if ("demek".equals(low)) {
            yor = "diyor"; yneg = "demiyor";
            fut = "diyecek"; fneg = "demeyecek";
            past = "dedi"; pneg = "demedi";
        } else if ("yemek".equals(low)) {
            yor = "yiyor"; yneg = "yemiyor";
            fut = "yiyecek"; fneg = "yemeyecek";
            past = "yedi"; pneg = "yemedi";
        } else {
            String ys, fs, ps, ns;
            if ("gitmek".equals(low)) {
                ys = "gid"; fs = "gid"; ps = "git"; ns = "git";
            } else if ("etmek".equals(low)) {
                ys = "ed"; fs = "ed"; ps = "et"; ns = "et";
            } else if ("tatmak".equals(low)) {
                ys = "tad"; fs = "tad"; ps = "tat"; ns = "tat";
            } else if ("gütmek".equals(low)) {
                ys = "güd"; fs = "güd"; ps = "güt"; ns = "güt";
            } else if (low.endsWith("etmek") && !notEtmek(low)) {
                String pre2 = inf.substring(0, inf.length() - 5);
                ys = pre2 + "ed"; fs = pre2 + "ed"; ps = pre2 + "et"; ns = pre2 + "et";
            } else {
                String st = stemOf(inf);
                ys = fs = ps = ns = st;
            }
            yor = yorForm(ys);
            fut = futForm(fs);
            past = pastForm(ps);
            yneg = ns + "m" + four(lastVowel(ns)) + "yor";
            String ae = two(lastVowel(ns));
            fneg = ns + "m" + ae + "y" + ("a".equals(ae) ? "acak" : "ecek");
            pneg = ns + "m" + ae + "d" + four(ae.charAt(0));
        }

        String past1 = past + "m";
        String pneg1 = pneg + "m";
        String yor1 = yor + "um";
        String yneg1 = yneg + "um";
        String fut1 = fut1sg(fut);
        String fneg1 = fut1sg(fneg);

        Forms f = new Forms();
        f.gelecekQ = prefix + fut + " " + mi(lastVowel(fut)) + "y" + four(lastVowel(fut)) + "m?";
        f.gelecekA = prefix + fut1;
        f.gelecekN = prefix + fneg1;
        f.simdiQ = prefix + yor + " muyum?";
        f.simdiA = prefix + yor1;
        f.simdiN = prefix + yneg1;
        f.gecmisQ = prefix + past1 + " " + mi(lastVowel(past1)) + "?";
        f.gecmisA = prefix + past1;
        f.gecmisN = prefix + pneg1;
        return f;
    }

    private static boolean notEtmek(String low) {
        return "tüketmek".equals(low) || "yönetmek".equals(low) || "iletmek".equals(low)
                || "öğretmek".equals(low) || "eritmek".equals(low) || "belirtmek".equals(low)
                || "incitmek".equals(low) || "gözetmek".equals(low) || "işletmek".equals(low);
    }

    private static String[] splitInf(String word) {
        String w = word.trim();
        int sp = w.lastIndexOf(' ');
        if (sp < 0) return new String[]{"", w};
        return new String[]{w.substring(0, sp + 1), w.substring(sp + 1)};
    }

    private static String stemOf(String inf) {
        if (inf.length() >= 3) {
            String tail = inf.substring(inf.length() - 3).toLowerCase(Locale.ROOT);
            if ("mak".equals(tail) || "mek".equals(tail)) return inf.substring(0, inf.length() - 3);
        }
        return inf;
    }

    private static char lastVowel(String s) {
        for (int i = s.length() - 1; i >= 0; i--) {
            char ch = Character.toLowerCase(s.charAt(i));
            if (VOWELS.indexOf(ch) >= 0) return ch;
        }
        return 'a';
    }

    private static String two(char v) {
        return FRONT.indexOf(v) >= 0 ? "e" : "a";
    }

    private static String four(char v) {
        boolean f = FRONT.indexOf(v) >= 0;
        boolean r = ROUNDED.indexOf(v) >= 0;
        if (f && r) return "ü";
        if (f) return "i";
        if (r) return "u";
        return "ı";
    }

    private static String mi(char v) {
        String x = four(v);
        if ("ı".equals(x)) return "mı";
        if ("i".equals(x)) return "mi";
        if ("u".equals(x)) return "mu";
        return "mü";
    }

    private static String yorForm(String stem) {
        if (stem.isEmpty()) return "iyor";
        char last = Character.toLowerCase(stem.charAt(stem.length() - 1));
        char v = lastVowel(stem);
        if (VOWELS.indexOf(last) >= 0) return stem.substring(0, stem.length() - 1) + four(v) + "yor";
        return stem + four(v) + "yor";
    }

    private static String futForm(String stem) {
        String ae = two(lastVowel(stem));
        String suf = "a".equals(ae) ? "acak" : "ecek";
        if (!stem.isEmpty() && VOWELS.indexOf(Character.toLowerCase(stem.charAt(stem.length() - 1))) >= 0) {
            return stem + "y" + suf;
        }
        return stem + suf;
    }

    private static String pastForm(String stem) {
        String d = four(lastVowel(stem));
        if (!stem.isEmpty() && VOWELS.indexOf(Character.toLowerCase(stem.charAt(stem.length() - 1))) >= 0) {
            return stem + "d" + d;
        }
        if (!stem.isEmpty() && VOICELESS.indexOf(Character.toLowerCase(stem.charAt(stem.length() - 1))) >= 0) {
            return stem + "t" + d;
        }
        return stem + "d" + d;
    }

    private static String fut1sg(String fut) {
        char v = lastVowel(fut);
        if (fut.endsWith("k")) return fut.substring(0, fut.length() - 1) + "ğ" + four(v) + "m";
        return fut + four(v) + "m";
    }
}
