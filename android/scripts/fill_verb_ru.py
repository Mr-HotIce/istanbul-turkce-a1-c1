#!/usr/bin/env python3
# Fill missing Russian glosses for Istanbul verb cards.
import csv, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV = os.path.join(ROOT, "istanbul_verbs.csv")
CARDS = os.path.join(ROOT, "android", "app", "src", "main", "assets", "cards.json")
KAIKKI = "/data/data/com.termux/files/home/tmp_ox/dicts/tr-kaikki.jsonl"
ENRU = "/data/data/com.termux/files/home/tmp_ox/dicts/eng-rus/eng-rus.tei"
CACHE = os.path.join(ROOT, "android", "scripts", ".cache")
os.makedirs(CACHE, exist_ok=True)

# Human translations for phrases and leftovers (TR lower -> RU).
EXTRA = {
    "acele etmek": "спешить, торопиться",
    "adet yerini bulmak": "идти своим чередом",
    "adım atmak": "делать шаг, предпринимать шаг",
    "affetmek": "прощать",
    "aklına getirmek": "напоминать, наводить на мысль",
    "akla karayı seçmek": "измучиться, пройти огонь и воду",
    "akıldan geçirmek": "обдумывать, прокручивать в голове",
    "aksetmek": "отражаться, отзываться",
    "alay etmek": "насмехаться, издеваться",
    "aman dilemek": "просить пощады",
    "ara vermek": "делать перерыв",
    "artış göstermek": "показывать рост",
    "arz etmek": "предлагать, представлять",
    "ayak uydurmak": "поспевать, подстраиваться",
    "ayaklarına kara sular inmek": "ноги отняться (от усталости)",
    "ayakta durmak": "стоять на ногах",
    "ayakta kalmak": "удержаться на ногах, выстоять",
    "ayırt etmek": "различать",
    "açıklığa kavuşmak": "проясниться",
    "ağırlık vermek": "делать упор, придавать значение",
    "balık tutmak": "ловить рыбу",
    "banyo yapmak": "принимать ванну",
    "başının etini yemek": "пилить, доставать (кого-л.)",
    "başını dinlemek": "отдыхать, приходить в себя",
    "başa çıkmak": "справляться",
    "başına devlet kuşu konmak": "крупно повезти",
    "berabere kalmak": "сыграть вничью",
    "beyaz peynir gibi olmak": "побледнеть (как сыр)",
    "bilgi vermek": "сообщать, информировать",
    "bilinçlendirmek": "просвещать, повышать сознательность",
    "bir şeyde hakkı olmak": "иметь право на что-л.",
    "bir şeyi lehine çevirmek": "обратить в свою пользу",
    "bir şeyin temelini atmak": "заложить основу",
    "birbirine girmek": "сцепиться, перемешаться",
    "borç vermek": "давать в долг",
    "burs vermek": "давать стипендию",
    "burun buruna gelmek": "столкнуться нос к носу",
    "bıyık altından gülmek": "усмехаться в усы",
    "can atmak": "гореть желанием",
    "canı çıkmak": "выбиться из сил, еле живой",
    "canına tak etmek": "чаша терпения переполнилась",
    "cesaret etmek": "осмелиться",
    "dahil etmek": "включать",
    "delik deşik etmek": "изрешетить, издырявить",
    "dengeli beslenmek": "питаться сбалансированно",
    "derdine çare olmak": "найти выход из беды",
    "dert yanmak": "жаловаться на беду",
    "destek vermek": "оказывать поддержку",
    "devam etmek": "продолжать",
    "dikkat çekmek": "привлекать внимание",
    "dikkat etmek": "обращать внимание, быть осторожным",
    "dikiş dikmek": "шить",
    "dikiş tutturmak": "свести концы с концами",
    "dile getirmek": "выразить словами",
    "dili tutulmak": "язык отнялся",
    "dillerde dolaşmak": "быть у всех на устах",
    "direksiyon kırmak": "крутить руль, сворачивать",
    "dizini dövmek": "кусать локти",
    "doğmamış çocuğa don biçmek": "делить шкуру неубитого медведя",
    "duş almak": "принимать душ",
    "duvar örmek": "класть стену",
    "ele almak": "взяться за дело, рассмотреть",
    "ele geçmek": "попасть в руки, быть захваченным",
    "eli boş gitmek": "уйти ни с чем",
    "etki etmek": "влиять, действовать",
    "evde kalmak": "остаться дома; засидеться в девках",
    "evlat edinmek": "усыновить / удочерить",
    "fazla gelmek": "быть слишком, оказаться лишним",
    "fotoğraf çekmek": "фотографировать",
    "garanti altına almak": "гарантировать, обеспечить",
    "geri çevirmek": "отказать, отвергнуть",
    "geride bırakmak": "оставить позади",
    "geride kalmak": "отстать",
    "gerisinde kalmak": "остаться позади",
    "gitar çalmak": "играть на гитаре",
    "giyinip kuşanmak": "нарядиться",
    "göbeği çatlamak": "надорваться (от смеха/труда)",
    "görebilmek": "суметь увидеть",
    "görev almak": "взять на себя задачу",
    "görevlendirmek": "поручить, назначить",
    "göz kamaştırmak": "ослеплять, поражать",
    "göz kırpmak": "подмигивать",
    "göz önüne serilmek": "предстать перед глазами",
    "gözden çıkarmak": "решиться потерять, списать",
    "göze batmak": "бросаться в глаза, раздражать",
    "göze çarpmak": "бросаться в глаза",
    "gözler önüne sermek": "выставить напоказ",
    "gözlerinin içi gülmek": "глаза смеются",
    "gözünü yükseklere dikmek": "метить высоко",
    "gönlünü hoş tutmak": "утешать, держать в хорошем настроении",
    "gün ışığına çıkarmak": "вывести на свет",
    "gündem oluşturmak": "формировать повестку",
    "hacca gitmek": "ехать в хадж",
    "hale düşmek": "дойти до такого состояния",
    "halsiz kalmak": "обессилеть",
    "hamle yapmak": "сделать ход, шаг",
    "hatır sormak": "справляться о здоровье",
    "hayal kurmak": "мечтать",
    "haşır neşir olmak": "быть по уши занятым",
    "hedef almak": "брать на прицел, ставить целью",
    "hoş görmek": "смотреть сквозь пальцы, прощать",
    "hoş karşılamak": "радушно встречать",
    "hoşbeş etmek": "болтать, обмениваться любезностями",
    "hüküm sürmek": "царить, господствовать",
    "hüküm vermek": "выносить приговор, судить",
    "ıslık çalmak": "свистеть",
    "iddia etmek": "утверждать, заявлять",
    "ihmal etmek": "пренебрегать",
    "ihraç etmek": "экспортировать",
    "iki laf etmek": "перекинуться парой слов",
    "ikna etmek": "убеждать",
    "ilave etmek": "добавлять",
    "ileri geri konuşmak": "говорить лишнее, грубить",
    "ilgi çekmek": "вызывать интерес",
    "ilgi duymak": "интересоваться",
    "ilgilenmek": "интересоваться, заниматься",
    "i̇lgilenmek": "интересоваться, заниматься",
    "ilham almak": "вдохновляться",
    "ilham vermek": "вдохновлять",
    "imaj yaratmak": "создавать имидж",
    "imdadına yetişmek": "прийти на помощь",
    "imza atmak": "ставить подпись",
    "internete girmek": "выходить в интернет",
    "iptal olmak": "отменяться",
    "irtibatlandırmak": "связывать, устанавливать контакт",
    "istatistik yüze gülmek": "статистика на стороне (кого-л.)",
    "istekte bulunmak": "обращаться с просьбой",
    "istifa etmek": "подавать в отставку",
    "istifade etmek": "пользоваться, извлекать пользу",
    "isyan etmek": "восставать",
    "itiraz etmek": "возражать",
    "izin vermek": "разрешать",
    "izne çıkmak": "уходить в отпуск",
    "içerlemek": "таить обиду",
    "içini boşaltmak": "излить душу",
    "içini çekmek": "вздыхать",
    "iş çevirmek": "провернуть дело",
    "iş işten geçmek": "поезд ушёл, уже поздно",
    "işe girişmek": "взяться за работу",
    "işleri yolunda olmak": "дела идут хорошо",
    "kafasına esmek": "взбрести в голову",
    "kafayı yemek": "сходить с ума",
    "kahvaltı etmek": "завтракать",
    "kalbi küt küt atmak": "сердце колотится",
    "kalbini fethetmek": "завоевать сердце",
    "kamuoyu oluşturmak": "формировать общественное мнение",
    "kanaat getirmek": "прийти к убеждению",
    "kanun çıkarmak": "принимать закон",
    "karar vermek": "принимать решение",
    "kartopu oynamak": "играть в снежки",
    "karşı karşıya kalmak": "столкнуться лицом к лицу",
    "katkı vermek": "вносить вклад",
    "kavga etmek": "ссориться, драться",
    "kayak yapmak": "кататься на лыжах",
    "kaynanası sevmek": "быть в ладах со свекровью (ирон.)",
    "kendini dışarı atmak": "выскочить наружу",
    "kendisini göstermek": "проявить себя",
    "keyfine varmak": "наслаждаться",
    "keyfini çıkarmak": "получать удовольствие",
    "kombine etmek": "комбинировать",
    "konsantre olmak": "сосредоточиться",
    "kontrol etmek": "проверять, контролировать",
    "kredi almak": "брать кредит",
    "kutlu olmak": "быть благословенным",
    "küçük düşünmek": "мелко мыслить",
    "kürek çekmek": "грести",
    "kılavuzluk etmek": "вести, быть проводником",
    "kılık değiştirmek": "переодеваться, менять облик",
    "kıyafet denemek": "примерять одежду",
    "kârlı çıkmak": "выйти в плюс",
    "lafın altından kalkmak": "найти что ответить",
    "linç etmek": "линчевать, травить",
    "mahkûm etmek": "осуждать, приговаривать",
    "mantık yürütmek": "рассуждать логически",
    "maruz kalmak": "подвергаться",
    "masaya yatırmak": "вынести на обсуждение",
    "masraf yapmak": "тратиться",
    "maymun olmak": "опростоволоситься, стать посмешищем",
    "merak etmek": "беспокоиться; любопытствовать",
    "merak uyandırmak": "вызывать интерес",
    "meraktan çatlamak": "сгорать от любопытства",
    "meydana gelmek": "происходить, возникать",
    "mezun olmak": "оканчивать (учёбу)",
    "meşhur etmek": "прославить",
    "miadı dolmak": "истечь (о сроке)",
    "mola vermek": "делать привал, перерыв",
    "motive etmek": "мотивировать",
    "mâl olmak": "обойтись в, стоить",
    "namak": "ошибка списка (не глагол)",
    "neden olmak": "стать причиной",
    "nefret etmek": "ненавидеть",
    "not etmek": "записывать",
    "nüfuz etmek": "проникать, влиять",
    "oda tutmak": "снимать комнату",
    "olanaklı kılmak": "делать возможным",
    "olmayacak duaya amin demek": "верить в несбыточное",
    "özen göstermek": "проявлять заботу, стараться",
    "pabucunu dama atmak": "выжить, затмить (кого-л.)",
    "para bozdurmak": "разменять деньги",
    "para çekmek": "снимать деньги",
    "park etmek": "парковаться",
    "payını almak": "получить свою долю",
    "peşine düşmek": "пуститься в погоню",
    "peşinde koşmak": "бегать за кем-л., стремиться",
    "problem çıkarmak": "создавать проблемы",
    "renk katmak": "вносить разнообразие",
    "restore edilmek": "реставрироваться",
    "rica etmek": "просить",
    "romantik takılmak": "флиртовать, вести себя романтично",
    "satın almak": "покупать",
    "sevk etmek": "направлять, отправлять",
    "seyre dalmak": "засмотреться",
    "sinirleri gerilmek": "нервы натянуты",
    "sitem etmek": "упрекать",
    "sohbet etmek": "беседовать",
    "spor yapmak": "заниматься спортом",
    "stres atmak": "сбрасывать стресс",
    "suratını asmak": "надуть губы, сделать кислое лицо",
    "sönük kalmak": "остаться в тени",
    "söz tutmak": "держать слово",
    "sıkı fıkı olmak": "быть запанибрата",
    "sıkıntı çekmek": "терпеть нужду, мучиться",
    "sınırlı tutmak": "ограничивать",
    "sırılsıklam olmak": "промокнуть до нитки",
    "süzülüp gitmek": "ускользнуть, уплыть",
    "şaka kaldırmak": "понимать шутки",
    "şakaya vurmak": "свести на шутку",
    "şeref vermek": "оказать честь",
    "şifayı kapmak": "подхватить болезнь",
    "şikayet etmek": "жаловаться",
    "tadım çıkarmak": "смаковать, наслаждаться",
    "tadını çıkarmak": "наслаждаться",
    "tahmin etmek": "предполагать, угадывать",
    "takip etmek": "следить, следовать",
    "tansiyon ölçtürmek": "измерять давление",
    "tarif etmek": "описывать, объяснять",
    "tartılmak": "взвешиваться",
    "tatmin etmek": "удовлетворять",
    "tedavi olmak": "лечиться",
    "teklif etmek": "предлагать",
    "tekrar etmek": "повторять",
    "telefon etmek": "звонить",
    "tembihlemek": "наказывать, предупреждать",
    "temelini atmak": "закладывать основу",
    "temin etmek": "обеспечивать, доставать",
    "tercih etmek": "предпочитать",
    "teslim etmek": "сдавать, вручать",
    "tespit etmek": "устанавливать, выявлять",
    "tıraş olmak": "бриться",
    "uzak durmak": "держаться в стороне",
    "uygun görmek": "считать уместным",
    "vaaz vermek": "проповедовать",
    "volta atmak": "ходить взад-вперёд",
    "yalan söylemek": "лгать",
    "yakından tanımak": "хорошо знать",
    "yardım etmek": "помогать",
    "yardım istemek": "просить помощи",
    "yardımcı olmak": "содействовать",
    "yatkın olmak": "быть склонным",
    "yaşayıp gitmek": "жить себе дальше",
    "yer almak": "занимать место, участвовать",
    "yok satmak": "быть раскупленным",
    "yol açmak": "приводить к, прокладывать путь",
    "yolunu bulmak": "найти выход",
    "yorumlamak": "толковать, комментировать",
    "yüreği hop etmek": "сердце ёкнуло",
    "zaman almak": "занимать время",
    "zaman harcamak": "тратить время",
    "zaman kaybetmek": "терять время",
    "zaman öldürmek": "убивать время",
    "zevk almak": "получать удовольствие",
    "zikretmek": "упоминать",
    "ziyaret etmek": "навещать, посещать",
    "ziyarete gelmek": "приходить в гости",
    "çare aramak": "искать выход",
    "çek bozdurmak": "обналичивать чек",
    "çekip gitmek": "взять и уйти",
    "çığır açmak": "прокладывать путь, быть первопроходцем",
    "çığlık atmak": "кричать, вскрикивать",
    "ölçüp biçmek": "взвешивать, прикидывать",
    "önermek": "предлагать",
    "üstesinden gelmek": "справиться, преодолеть",
    "üstünlük kurmak": "установить превосходство",
    "ümidi kaybolmak": "потерять надежду",
    "ümidini kaybetmek": "утратить надежду",
    "ün kazanmak": "прославиться",
    # single-word leftovers and common verbs
    "asmak": "вешать",
    "atlamak": "прыгать, перескакивать",
    "bakmak": "смотреть, присматривать",
    "bayılmak": "падать в обморок; очень нравиться",
    "benzemek": "быть похожим",
    "beslenmek": "питаться",
    "binmek": "садиться (на транспорт)",
    "bitirmek": "заканчивать",
    "bitmek": "кончаться",
    "buluşmak": "встречаться",
    "danışmak": "советоваться",
    "dilemek": "желать, просить",
    "dinlenmek": "отдыхать",
    "dolaşmak": "бродить, гулять",
    "doğmak": "рождаться",
    "dönmek": "возвращаться, поворачиваться",
    "evlenmek": "жениться, выходить замуж",
    "gecikmek": "опаздывать",
    "gezmek": "гулять, путешествовать",
    "geçmek": "проходить, переходить",
    "görüşmek": "общаться, обсуждать",
    "hazırlamak": "готовить, подготавливать",
    "heyecanlanmak": "волноваться",
    "hissetmek": "чувствовать",
    "hoşlanmak": "нравиться, любить",
    "izlemek": "следить, смотреть",
    "kalmak": "оставаться",
    "kapanmak": "закрываться",
    "karşılamak": "встречать",
    "katılmak": "присоединяться",
    "kaşınmak": "чесаться",
    "korkmak": "бояться",
    "korumak": "защищать, беречь",
    "koymak": "класть, ставить",
    "kızarmak": "краснеть; жариться",
    "oynamak": "играть",
    "sürmek": "вести (машину); длиться",
    "tanışmak": "знакомиться",
    "temizlemek": "чистить, убирать",
    "uzanmak": "лежать, протягиваться",
    "varmak": "прибывать",
    "vedalaşmak": "прощаться",
    "yakmak": "жечь",
    "yatmak": "лежать, ложиться",
    "yaşlanmak": "стареть",
    "yenmek": "побеждать",
    "yorulmak": "уставать",
    "yıkamak": "мыть",
    "çalmak": "играть (на инструменте); красть; звонить",
    "öksürmek": "кашлять",
    "öpmek": "целовать",
    "özlemek": "скучать",
    "öğretmek": "учить (кого-л.)",
    "anlatmak": "рассказывать, объяснять",
    "anırmak": "реветь (об осле)",
    "artmak": "увеличиваться",
    "azalmak": "уменьшаться",
    "basmak": "нажимать, наступать",
    "batmak": "тонуть, заходить (о солнце)",
    "bağlamak": "связывать",
    "boyamak": "красить",
    "bozulmak": "портиться",
    "bıkmak": "устать, надоесть",
    "dalmak": "нырять; замечтаться",
    "dağıtmak": "раздавать, рассеивать",
    "denemek": "пробовать",
    "dizilmek": "выстраиваться",
    "dizmek": "ставить в ряд",
    "doğramak": "нарезать",
    "duymak": "слышать, чувствовать",
    "dökmek": "лить, проливать",
    "eklemek": "добавлять",
    "farkında olmak": "осознавать",
    "fethetmek": "завоёвывать",
    "fırçalamak": "чистить щёткой",
    "fışkırmak": "бить струёй",
    "gerçekleştirmek": "осуществлять",
    "geç kalmak": "опаздывать",
    "giyinmek": "одеваться",
    "güneşlenmek": "загорать",
    "güvenmek": "доверять",
    "hapşırmak": "чихать",
    "hatırlamak": "вспоминать",
    "haşlamak": "варить",
    "horlamak": "храпеть",
    "icat etmek": "изобретать",
    "ilerlemek": "продвигаться",
    "imzalamak": "подписывать",
    "incelemek": "изучать, рассматривать",
    "incitmek": "обижать, ранить",
    "itmek": "толкать",
    "iyileşmek": "выздоравливать",
    "işaretlemek": "отмечать",
    "karşılaşmak": "встречаться, сталкиваться",
    "kaybolmak": "пропадать",
    "kaynamak": "кипеть",
    "kaynatmak": "кипятить",
    "kazanmak": "выигрывать, зарабатывать",
    "kaçmak": "убегать",
    "keşfetmek": "открывать, обнаруживать",
    "kopmak": "оторваться, разразиться",
    "közlemek": "запекать в золе, тлеть",
    "küsmek": "дуться, обижаться",
    "kımıldamak": "шевелиться",
    "kızartmak": "жарить",
    "kızmak": "злиться; нагреваться",
    "nişanlanmak": "обручиться",
    "numaralandırmak": "нумеровать",
    "oluşturmak": "образовывать, создавать",
    "rendelemek": "тереть на тёрке",
    "saklamak": "прятать, хранить",
    "silmek": "вытирать, удалять",
    "soluklanmak": "перевести дух",
    "söndürmek": "гасить",
    "sürtünmek": "тереться",
    "süslemek": "украшать",
    "süzmek": "процеживать",
    "sıralamak": "перечислять, выстраивать",
    "sığmak": "помещаться",
    "takmak": "надевать, прикреплять",
    "tamamlamak": "завершать",
    "tartmak": "взвешивать",
    "taşmak": "переливаться через край",
    "tükenmek": "иссякать",
    "usanmak": "устать, пресытиться",
    "yapışmak": "прилипать",
    "yatıştırmak": "успокаивать",
    "yayımlamak": "публиковать",
    "yağmak": "идти (о дожде/снеге)",
    "yerleştirmek": "размещать",
    "yetişmek": "успевать, вырастать",
    "yetiştirmek": "выращивать, успевать доставить",
    "çarpmak": "ударять, врезаться",
    "çağırmak": "звать",
    "çekinmek": "стесняться, избегать",
    "çizmek": "рисовать, чертить",
    "çözmek": "развязывать, решать",
    "çırpmak": "взбивать; хлопать",
    "ütülemek": "гладить (утюгом)",
    "şaşırmak": "удивляться",
    "şişirmek": "надувать",
    "şımartmak": "баловать",
    "aksamak": "хромать; давать сбой",
    "akıtmak": "лить, цедить",
    "algılamak": "воспринимать",
    "anımsamak": "припоминать",
    "artırmak": "увеличивать",
    "arınmak": "очищаться",
    "atıştırmak": "перекусывать",
    "ayırmak": "отделять, уделять",
    "aşmak": "преодолевать, превосходить",
    "bahsetmek": "упоминать, говорить о",
    "belirlemek": "определять",
    "benimsemek": "принимать, усваивать",
    "berraklaştırmak": "прояснять",
    "burkmak": "подворачивать (ногу)",
    "depolamak": "складировать",
    "değerlendirmek": "оценивать",
    "dinmek": "утихать",
    "dokunmak": "трогать",
    "dönüşmek": "превращаться",
    "eleştirmek": "критиковать",
    "esirgemek": "щадить, не жалеть",
    "eğmek": "наклонять",
    "geliştirmek": "развивать",
    "gerektirmek": "требовать, обусловливать",
    "gerçekleşmek": "сбываться, осуществляться",
    "gütmek": "пасти; преследовать (цель)",
    "harcamak": "тратить",
    "hedeflemek": "ставить целью",
    "ilerletmek": "продвигать",
    "kabullenmek": "принимать (факт)",
    "kanıtlamak": "доказывать",
    "katlanmak": "терпеть, сносить",
    "katmak": "добавлять",
    "kavuşmak": "воссоединяться, обретать",
    "kaynaklanmak": "происходить от, корениться",
    "kaytarmak": "увиливать",
    "kaçınmak": "избегать",
    "kurmak": "устанавливать, основывать",
    "kurtarmak": "спасать",
    "kurtulmak": "избавляться",
    "köreltmek": "притуплять, губить",
    "kötüleşmek": "ухудшаться",
    "kırılmak": "ломаться; обижаться",
    "netleşmek": "проясняться",
    "odaklanmak": "сосредоточиться",
    "olgunlaşmak": "созревать",
    "ovmak": "тереть",
    "patlamak": "взрываться",
    "paylaşmak": "делиться",
    "pıhtılaşmak": "свёртываться (о крови)",
    "rahatlamak": "расслабляться",
    "saklanmak": "прятаться",
    "saptamak": "устанавливать, выявлять",
    "sarsılmak": "сотрясаться, пошатнуться",
    "sağlamak": "обеспечивать",
    "sinirlenmek": "злиться",
    "sönmek": "гаснуть",
    "sıkışmak": "зажиматься, застревать",
    "sızdırmak": "просачивать, сливать (информацию)",
    "tanımlamak": "определять, описывать",
    "tartışmak": "спорить, обсуждать",
    "tazelemek": "освежать",
    "telaşlanmak": "суетиться, тревожиться",
    "tüketmek": "потреблять, расходовать",
    "ulaşmak": "достигать",
    "uyarlamak": "приспособлять, адаптировать",
    "uzaklaşmak": "отдаляться",
    "uzamak": "удлиняться, затягиваться",
    "uğraşmak": "возиться, заниматься",
    "yadırgamak": "считать чуждым, странным",
    "yaramak": "годиться, быть полезным",
    "yaratmak": "создавать",
    "yedeklemek": "делать запасную копию",
    "yenilemek": "обновлять",
    "yitirmek": "утрачивать",
    "yitmek": "исчезать",
    "yoğunlaşmak": "сгущаться, усиливаться",
    "yönetmek": "управлять",
    "yönlendirmek": "направлять",
    "yüceltmek": "возвеличивать",
    "yükseltmek": "поднимать, повышать",
    "yüreklendirmek": "подбадривать",
    "yıpratmak": "изнашивать, изматывать",
    "yığmak": "складывать грудой",
    "zenginleşmek": "богатеть",
    "zorlamak": "заставлять, напрягать",
    "zorlaştırmak": "усложнять",
    "çıldırtmak": "сводить с ума",
    "öfkelenmek": "злиться, гневаться",
    "ısınmak": "греться, разогреваться",
    "aldanmak": "обманываться",
    "aldatmak": "обманывать, изменять",
    "anmak": "поминать, вспоминать",
    "ayarlamak": "настраивать, назначать",
    "ayıklamak": "перебирать, отсеивать",
    "azarlamak": "бранить",
    "barındırmak": "давать приют, содержать",
    "bağlanmak": "привязываться, подключаться",
    "bağımlı olmak": "быть зависимым",
    "boğmak": "душить, топить",
    "cızırdamak": "шипеть, трещать",
    "daldırmak": "окунать",
    "damgasını vurmak": "наложить отпечаток",
    "dövünmek": "причитать, бить себя",
    "elde etmek": "добиваться, получать",
    "ertelemek": "откладывать",
    "fokurdamak": "бурлить",
    "fısıldamak": "шептать",
    "kandırmak": "обманывать",
    "kaplamak": "покрывать",
    "kapsamak": "охватывать",
    "keselemek": "тереть мочалкой",
    "kirlenmek": "пачкаться",
    "kundaklamak": "пеленать; поджигать",
    "küreselleşmek": "глобализироваться",
    "odaklamak": "фокусировать",
    "okşamak": "гладить, ласкать",
    "oyalamak": "отвлекать, занимать",
    "pazarlamak": "продавать, продвигать",
    "pekiştirmek": "закреплять, усиливать",
    "sahiplenmek": "присваивать, опекать",
    "saldırganlaşmak": "становиться агрессивным",
    "savunmak": "защищать",
    "sergilemek": "выставлять, демонстрировать",
    "sona ermek": "заканчиваться",
    "sürdürmek": "продолжать",
    "sürülmek": "быть изгнанным; сеяться",
    "sıvazlamak": "поглаживать",
    "tapmak": "поклоняться",
    "tasarlamak": "проектировать, замышлять",
    "tutuklamak": "арестовывать",
    "tıklamak": "щёлкать (мышью)",
    "uzaklaştırmak": "отдалять, отстранять",
    "yakınmak": "сетовать",
    "yanılmak": "ошибаться",
    "yaralamak": "ранить",
    "yaygınlaşmak": "распространяться",
    "yılmak": "пасовать, устрашаться",
    "çarmıha germek": "распинать",
    "çatmak": "наткнуться; набрасываться",
    "özümsemek": "усваивать",
    "ısırmak": "кусать",
    "şahlanmak": "вставать на дыбы, воспрянуть",
    "şaşmak": "удивляться; сбиваться",
    "şımarmak": "избаловаться, зазнаться",
    "adamak": "посвящать, давать обет",
    "adlandırmak": "называть",
    "aktarmak": "пересаживать, передавать",
    "buğulanmak": "запотевать",
    "desteklemek": "поддерживать",
    "deşmek": "вскрывать, ковырять",
    "doğrulmak": "выпрямляться",
    "edinmek": "приобретать",
    "ekmek yemek": "есть хлеб; зарабатывать на жизнь",
    "eritmek": "плавить, растапливать",
    "feryat etmek": "вопить",
    "fırlatmak": "швырять",
    "harmanlamak": "смешивать",
    "iletmek": "передавать, доставлять",
    "ilişkilendirmek": "связывать, соотносить",
    "işlemek": "обрабатывать; работать (о механизме)",
    "kavramak": "схватывать, постигать",
    "kaygılanmak": "беспокоиться",
    "kısıtlamak": "ограничивать",
    "kıyaslamak": "сравнивать",
    "onaylamak": "одобрять, утверждать",
    "salgılamak": "выделять (секрет)",
    "sivrilmek": "выделяться, заостряться",
    "sunmak": "предлагать, преподносить",
    "sözleşmek": "договариваться",
    "sürüklemek": "тащить",
    "takışmak": "пререкаться, застревать",
    "taramak": "расчёсывать; сканировать",
    "tutturmak": "настоять; прикрепить",
    "ulumak": "выть",
    "yakarmak": "умолять",
    "yansımak": "отражаться",
    "yapış yapış olmak": "стать липким",
    "yeltenmek": "пытаться, замахиваться",
    "zedelemek": "повреждать",
    "zonklamak": "пульсировать (о боли)",
    "çarpıtmak": "искажать",
    "çatışmak": "сталкиваться, конфликтовать",
    "çullanmak": "наваливаться",
    "çırpınmak": "биться, трепыхаться",
    "önemsemek": "придавать значение",
    "öngörmek": "предвидеть",
    "övmek": "хвалить",
    "özetlemek": "резюмировать",
    "pişirmek": "готовить (еду)",
    "çalıştırmak": "запускать, заставлять работать",
    "anlaşmak": "договариваться, понимать друг друга",
    "aramak": "искать; звонить",
    "atmak": "бросать",
    "ağrımak": "болеть",
    "beklemek": "ждать",
    "beğenmek": "нравиться",
    "biriktirmek": "копить, собирать",
    "dans etmek": "танцевать",
    "demek": "говорить, значить, сказать",
    "değiştirmek": "менять",
    "dinlemek": "слушать",
    "durmak": "останавливаться, стоять",
    "etmek": "делать (вспомогательный глагол)",
    "girmek": "входить",
    "göndermek": "отправлять, посылать",
    "hazırlanmak": "готовиться",
    "koşmak": "бегать",
    "kullanmak": "использовать",
    "kutlamak": "праздновать",
    "sallanmak": "качаться",
    "sanmak": "полагать, считать",
    "sormak": "спрашивать",
    "söylemek": "говорить, сказать",
    "sıkılmak": "скучать; стесняться",
    "tanımak": "знать, узнавать",
    "toplamak": "собирать",
    "tırmanmak": "карабкаться, лазить",
    "yaşamak": "жить",
    "yürümek": "ходить пешком",
    "yüzmek": "плавать",
    "çıkmak": "выходить",
    "öğrenmek": "учить, учиться",
    "bastırmak": "подавлять, придавливать",
    "doldurmak": "наполнять",
    "geçirmek": "проводить (время); пропускать",
    "uzatmak": "протягивать, продлевать",
    "boşaltmak": "опорожнять, выгружать",
    "kaptırmak": "дать выхватить",
    "yansıtmak": "отражать",
    "püskürtmek": "распылять, отбивать",
    "sınıflandırmak": "классифицировать",
    "uydurmak": "выдумывать, подгонять",
    "yapılandırmak": "структурировать, реструктурировать",
    "yöneltmek": "направлять",
    "yığılmak": "скопляться, заваливаться",
    "zehirlenmek": "отравляться",
    "örgütlenmek": "организовываться",
    "düşünmek": "думать, размышлять",
    "çekmek": "тянуть; снимать (фото); терпеть",
}


JUNK_MARK = (
    "-ать", "-еть", "каузатив", "пассивный", "бездеятельный", "возвратный",
    "телль", "коллекта", "покрывало", "право голоса",
)


def clean_ru(s):
    s = (s or "").strip()
    parts = [p.strip() for p in s.replace("·", ";").split(";")]
    keep = []
    for p in parts:
        if not p or p.startswith("-"):
            continue
        low = p.lower()
        if any(j in low for j in JUNK_MARK):
            continue
        if p in ("из", "не", "акт", "ибо"):
            continue
        keep.append(p)
    return "; ".join(keep)


def good_ru(s):
    s = clean_ru(s)
    if not s:
        return False
    if s.startswith("(нет"):
        return False
    low = s.lower()
    if any(j in low for j in JUNK_MARK):
        return False
    return True


def load_kaikki():
    cache = os.path.join(CACHE, "kaikki_verbs.json")
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    need = set()
    for r in csv.DictReader(open(CSV, encoding="utf-8")):
        w = r["word"].strip().lower()
        need.add(w)
        need.add(w.split()[-1])
    hits = {}
    with open(KAIKKI, encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            w = (o.get("word") or "").lower()
            if w not in need:
                continue
            glosses = []
            for s in o.get("senses") or []:
                tags = s.get("tags") or []
                if "form-of" in tags:
                    continue
                for g in s.get("glosses") or []:
                    gl = g.lower()
                    if "imperative of" in gl or "form of" in gl or "participle of" in gl:
                        continue
                    glosses.append(g)
            if glosses:
                hits.setdefault(w, [])
                for g in glosses:
                    if g not in hits[w]:
                        hits[w].append(g)
    json.dump(hits, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    return hits


def load_enru():
    cache = os.path.join(CACHE, "enru_verbs.json")
    if os.path.exists(cache):
        return json.load(open(cache, encoding="utf-8"))
    text = open(ENRU, encoding="utf-8").read()
    d = {}
    for m in re.finditer(r"<entry>(.*?)</entry>", text, re.S):
        block = m.group(1)
        orth = re.search(r"<orth>(.*?)</orth>", block)
        if not orth:
            continue
        key = orth.group(1).strip().lower()
        quotes = re.findall(r'<cit type="trans"[^>]*>\s*<quote>(.*?)</quote>', block, re.S)
        quotes = [re.sub(r"<[^>]+>", "", q).strip() for q in quotes]
        quotes = [q for q in quotes if q]
        if not quotes:
            continue
        is_verb = "<pos>v</pos>" in block
        slot = d.setdefault(key, {"v": [], "o": []})
        (slot["v"] if is_verb else slot["o"]).extend(quotes)
    json.dump(d, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    return d


def en_tokens(gloss):
    g = gloss.strip()
    g = re.sub(r"^\(?to\)?\s+", "", g, flags=re.I)
    g = g.split("/")[0]
    g = g.split(";")[0]
    g = g.split("(")[0]
    parts = [p.strip() for p in re.split(r",| or ", g) if p.strip()]
    out = []
    for p in parts[:3]:
        p = re.sub(r"^\(?to\)?\s+", "", p, flags=re.I).strip()
        # first 3 words max
        words = p.split()
        if not words:
            continue
        out.append(" ".join(words[:3]).lower())
        out.append(words[0].lower())
    return out


def lookup_en(enru, token):
    e = enru.get(token)
    if not e:
        return ""
    for q in e.get("v") or []:
        if q:
            return q
    for q in e.get("o") or []:
        if q:
            return q
    return ""


def pick_from_glosses(enru, glosses):
    rus = []
    seen = set()
    for g in glosses[:6]:
        for tok in en_tokens(g):
            ru = lookup_en(enru, tok)
            if ru and ru.lower() not in seen:
                seen.add(ru.lower())
                rus.append(ru)
            if len(rus) >= 2:
                return ", ".join(rus)
    return ", ".join(rus)


def extra_get(word):
    k = word.strip().lower()
    if k in EXTRA:
        return EXTRA[k]
    # dotted capital i
    k2 = k.replace("i̇", "i").replace("İ", "i")
    if k2 in EXTRA:
        return EXTRA[k2]
    last = k.split()[-1]
    if last in EXTRA:
        prefix = word.strip()[: -(len(last))].strip()
        if prefix:
            return EXTRA[last]
        return EXTRA[last]
    return ""


def main():
    print("loading kaikki...")
    kaikki = load_kaikki()
    print("kaikki keys", len(kaikki))
    print("loading en-ru...")
    enru = load_enru()
    print("enru keys", len(enru))

    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    still = []
    filled = 0
    kept = 0
    for r in rows:
        w = r["word"].strip()
        ru = extra_get(w)
        if not good_ru(ru):
            old = clean_ru(r.get("russian"))
            if good_ru(old):
                ru = old
        if not good_ru(ru):
            key = w.lower().replace("i̇", "i")
            glosses = kaikki.get(key) or kaikki.get(key.split()[-1]) or []
            ru = pick_from_glosses(enru, glosses)
        if good_ru(ru):
            if ru != (r.get("russian") or "").strip():
                filled += 1
            else:
                kept += 1
            r["russian"] = clean_ru(ru)
        else:
            still.append(w)
    print("kept", kept, "filled", filled, "still", len(still))
    if still:
        print("STILL MISSING:")
        for w in still:
            print(" ", w)

    with open(CSV, "w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["word", "level", "transcription", "russian"])
        wr.writeheader()
        wr.writerows(rows)

    cards = []
    for r in rows:
        cards.append({
            "w": r["word"],
            "ru": (r.get("russian") or "").strip(),
            "tr": r.get("transcription") or "",
            "ipa": "",
            "lvl": r.get("level") or "",
        })
    json.dump(cards, open(CARDS, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    empty = sum(1 for c in cards if not good_ru(c["ru"]))
    print("cards", len(cards), "without good ru", empty)
    if empty and still:
        sys.exit(1)


if __name__ == "__main__":
    main()
