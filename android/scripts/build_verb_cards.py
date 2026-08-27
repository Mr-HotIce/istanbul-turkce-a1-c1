#!/usr/bin/env python3
# Filter Istanbul vocab to verbs and sanity-check Petrov 9-cell conjugation.
import csv, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV = os.path.join(ROOT, "istanbul_words.csv")
OUT = os.path.join(ROOT, "android", "app", "src", "main", "assets", "cards.json")
OUT_CSV = os.path.join(ROOT, "istanbul_verbs.csv")

VOWELS = "aeıioöuü"
FRONT = set("eiöü")
ROUNDED = set("oöuü")
VOICELESS = set("pçtkfsşh")

NOUNS = {
    "parmak", "ekmek", "ana yemek", "mercimek", "kaymak",
    "çakmak", "hamak", "ırmak", "başparmak",
}

NOT_ETMEK = {
    "tüketmek", "yönetmek", "iletmek", "öğretmek", "eritmek",
    "belirtmek", "incitmek", "gözetmek", "işletmek", "iletmek",
}

def last_vowel(s):
    for ch in reversed(s.lower()):
        if ch in VOWELS:
            return ch
    return "a"

def two(v):
    return "e" if v in FRONT else "a"

def four(v):
    f, r = v in FRONT, v in ROUNDED
    if f and r:
        return "ü"
    if f:
        return "i"
    if r:
        return "u"
    return "ı"

def mi(v):
    # question particle mı/mi/mu/mü
    return {"ı": "mı", "i": "mi", "u": "mu", "ü": "mü"}[four(v)]

def split_inf(word):
    w = word.strip()
    parts = w.split()
    if len(parts) > 1:
        return " ".join(parts[:-1]) + " ", parts[-1]
    return "", w

def stem_of(inf):
    low = inf.lower()
    if low.endswith("mak") or low.endswith("mek"):
        return inf[:-3]
    return inf

def yor_form(stem):
    if not stem:
        return stem + "iyor"
    if stem[-1].lower() in VOWELS:
        v = last_vowel(stem)
        return stem[:-1] + four(v) + "yor"
    v = last_vowel(stem)
    return stem + four(v) + "yor"

def fut_form(stem):
    v = last_vowel(stem)
    ae = two(v)
    suf = ae + "cak" if ae == "a" else ae + "cek"
    if stem and stem[-1].lower() in VOWELS:
        return stem + "y" + suf
    return stem + suf

def past_form(stem):
    v = last_vowel(stem)
    d = four(v)
    if stem and stem[-1].lower() in VOWELS:
        return stem + "d" + d
    if stem and stem[-1].lower() in VOICELESS:
        return stem + "t" + d
    return stem + "d" + d

def fut_1sg(fut):
    # yapacak → yapacağım
    v = last_vowel(fut)
    if fut.endswith("k"):
        return fut[:-1] + "ğ" + four(v) + "m"
    return fut + four(v) + "m"

def conjugate(infinitive):
    prefix, inf = split_inf(infinitive)
    low = inf.lower()
    # already-negative infinitives
    if low.endswith("mamak") or low.endswith("memek"):
        return None

    special = {
        "demek": dict(yor="diyor", yneg="demiyor", fut="diyecek", fneg="demeyecek",
                      past="dedi", pneg="demedi"),
        "yemek": dict(yor="yiyor", yneg="yemiyor", fut="yiyecek", fneg="yemeyecek",
                      past="yedi", pneg="yemedi"),
    }
    if low in special:
        s = special[low]
        yor, yneg, fut, fneg, past, pneg = s["yor"], s["yneg"], s["fut"], s["fneg"], s["past"], s["pneg"]
    else:
        irreg = {
            "gitmek": ("gid", "gid", "git", "git"),
            "etmek": ("ed", "ed", "et", "et"),
            "tatmak": ("tad", "tad", "tat", "tat"),
            "gütmek": ("güd", "güd", "güt", "güt"),
        }
        use = None
        pre2 = ""
        if low in irreg:
            use = irreg[low]
        elif low.endswith("etmek") and low not in NOT_ETMEK:
            pre2 = inf[:-5]
            use = irreg["etmek"]
        if use:
            ys, fs, ps, ns = use
            ys, fs, ps, ns = pre2 + ys, pre2 + fs, pre2 + ps, pre2 + ns
            yor = yor_form(ys)
            fut = fut_form(fs)
            past = past_form(ps)
            nstem = ns
        else:
            st = stem_of(inf)
            yor = yor_form(st)
            fut = fut_form(st)
            past = past_form(st)
            nstem = st
        yneg = nstem + "m" + four(last_vowel(nstem)) + "yor"
        ae = two(last_vowel(nstem))
        fneg = nstem + "m" + ae + "y" + ("acak" if ae == "a" else "ecek")
        pneg = nstem + "m" + ae + "d" + four(ae)

    past1 = past + "m"
    pneg1 = pneg + "m"
    yor1 = yor + "um"
    yneg1 = yneg + "um"
    fut1 = fut_1sg(fut)
    fneg1 = fut_1sg(fneg)

    def P(s):
        return prefix + s

    return {
        "gelecek_q": P(fut) + " " + mi(last_vowel(fut)) + "y" + four(last_vowel(fut)) + "m?",
        "gelecek_a": P(fut1),
        "gelecek_n": P(fneg1),
        "simdi_q": P(yor) + " muyum?",
        "simdi_a": P(yor1),
        "simdi_n": P(yneg1),
        "gecmis_q": P(past1) + " " + mi(last_vowel(past1)) + "?",
        "gecmis_a": P(past1),
        "gecmis_n": P(pneg1),
    }

def is_verb(word):
    w = word.strip()
    low = w.lower()
    if low in NOUNS:
        return False
    last = low.split()[-1]
    if last in NOUNS:
        return False
    if not (last.endswith("mak") or last.endswith("mek")):
        return False
    if last.endswith("mamak") or last.endswith("memek"):
        return False
    if len(last) < 5:
        return False
    return True

EXPECT = {
    "gitmek": {
        "gelecek_a": "gideceğim", "gelecek_n": "gitmeyeceğim", "gelecek_q": "gidecek miyim?",
        "simdi_a": "gidiyorum", "simdi_n": "gitmiyorum", "simdi_q": "gidiyor muyum?",
        "gecmis_a": "gittim", "gecmis_n": "gitmedim", "gecmis_q": "gittim mi?",
    },
    "yapmak": {
        "gelecek_a": "yapacağım", "simdi_a": "yapıyorum", "gecmis_a": "yaptım",
        "gelecek_n": "yapmayacağım", "simdi_n": "yapmıyorum", "gecmis_n": "yapmadım",
    },
    "almak": {
        "gelecek_a": "alacağım", "simdi_a": "alıyorum", "gecmis_a": "aldım",
        "simdi_n": "almıyorum",
    },
    "gelmek": {
        "gelecek_a": "geleceğim", "simdi_a": "geliyorum", "gecmis_a": "geldim",
        "gelecek_n": "gelmeyeceğim", "simdi_n": "gelmiyorum",
    },
    "okumak": {
        "gelecek_a": "okuyacağım", "simdi_a": "okuyorum", "gecmis_a": "okudum",
        "simdi_n": "okumuyorum",
    },
    "sevmek": {
        "gelecek_a": "seveceğim", "simdi_a": "seviyorum", "gecmis_a": "sevdim",
    },
    "demek": {
        "gelecek_a": "diyeceğim", "simdi_a": "diyorum", "gecmis_a": "dedim",
        "simdi_n": "demiyorum", "gelecek_n": "demeyeceğim", "gecmis_n": "demedim",
    },
    "yemek": {
        "gelecek_a": "yiyeceğim", "simdi_a": "yiyorum", "gecmis_a": "yedim",
        "simdi_n": "yemiyorum",
    },
    "aramak": {
        "simdi_a": "arıyorum", "gelecek_a": "arayacağım", "gecmis_a": "aradım",
    },
    "konuşmak": {
        "simdi_a": "konuşuyorum", "gecmis_a": "konuştum",
    },
    "devam etmek": {
        "simdi_a": "devam ediyorum", "gelecek_a": "devam edeceğim", "gecmis_a": "devam ettim",
    },
    "görmek": {
        "simdi_a": "görüyorum", "gecmis_a": "gördüm", "gelecek_a": "göreceğim",
    },
}


def main():
    failed = 0
    for inf, exp in EXPECT.items():
        got = conjugate(inf)
        for k, v in exp.items():
            if got[k] != v:
                print("FAIL", inf, k, "got", got[k], "want", v)
                failed += 1
    if failed:
        print("conjugation failures", failed)
        sys.exit(1)
    print("conjugation ok")

    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    cards = []
    seen = set()
    for r in rows:
        w = r["word"].strip()
        key = w.lower()
        if key in seen:
            continue
        if not is_verb(w):
            continue
        if conjugate(w) is None:
            continue
        seen.add(key)
        ru = (r.get("russian") or "").strip()
        if ru in ("(нет перевода)", "-ать; -еть", "-ать"):
            ru = ""
        cards.append({
            "w": w,
            "ru": ru,
            "tr": r.get("transcription") or "",
            "ipa": "",
            "lvl": r.get("level") or "",
        })
    cards.sort(key=lambda c: (c["lvl"], c["w"].lower()))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, separators=(",", ":"))
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["word", "level", "transcription", "russian"])
        wr.writeheader()
        for c in cards:
            wr.writerow({"word": c["w"], "level": c["lvl"], "transcription": c["tr"], "russian": c["ru"]})
    print("verbs", len(cards), "->", OUT)

if __name__ == "__main__":
    main()
