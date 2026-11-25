"""The 114 surahs: transliterated name, English meaning and number of ayat (6,236 in total)."""

SURAHS = [
    ("Al-Fatihah", "The Opening", 7), ("Al-Baqarah", "The Cow", 286), ("Al-Imran", "The Family of Imran", 200),
    ("An-Nisa", "The Women", 176), ("Al-Ma'idah", "The Table Spread", 120), ("Al-An'am", "The Cattle", 165),
    ("Al-A'raf", "The Heights", 206), ("Al-Anfal", "The Spoils of War", 75), ("At-Tawbah", "The Repentance", 129),
    ("Yunus", "Jonah", 109), ("Hud", "Hud", 123), ("Yusuf", "Joseph", 111), ("Ar-Ra'd", "The Thunder", 43),
    ("Ibrahim", "Abraham", 52), ("Al-Hijr", "The Rocky Tract", 99), ("An-Nahl", "The Bee", 128),
    ("Al-Isra", "The Night Journey", 111), ("Al-Kahf", "The Cave", 110), ("Maryam", "Mary", 98), ("Ta-Ha", "Ta-Ha", 135),
    ("Al-Anbiya", "The Prophets", 112), ("Al-Hajj", "The Pilgrimage", 78), ("Al-Mu'minun", "The Believers", 118),
    ("An-Nur", "The Light", 64), ("Al-Furqan", "The Criterion", 77), ("Ash-Shu'ara", "The Poets", 227),
    ("An-Naml", "The Ant", 93), ("Al-Qasas", "The Stories", 88), ("Al-Ankabut", "The Spider", 69),
    ("Ar-Rum", "The Romans", 60), ("Luqman", "Luqman", 34), ("As-Sajdah", "The Prostration", 30),
    ("Al-Ahzab", "The Confederates", 73), ("Saba", "Sheba", 54), ("Fatir", "The Originator", 45), ("Ya-Sin", "Ya-Sin", 83),
    ("As-Saffat", "Those Ranged in Ranks", 182), ("Sad", "Sad", 88), ("Az-Zumar", "The Groups", 75),
    ("Ghafir", "The Forgiver", 85), ("Fussilat", "Explained in Detail", 54), ("Ash-Shura", "The Consultation", 53),
    ("Az-Zukhruf", "The Ornaments of Gold", 89), ("Ad-Dukhan", "The Smoke", 59), ("Al-Jathiyah", "The Kneeling", 37),
    ("Al-Ahqaf", "The Wind-Curved Sandhills", 35), ("Muhammad", "Muhammad", 38), ("Al-Fath", "The Victory", 29),
    ("Al-Hujurat", "The Rooms", 18), ("Qaf", "Qaf", 45), ("Adh-Dhariyat", "The Winnowing Winds", 60),
    ("At-Tur", "The Mount", 49), ("An-Najm", "The Star", 62), ("Al-Qamar", "The Moon", 55),
    ("Ar-Rahman", "The Most Merciful", 78), ("Al-Waqi'ah", "The Inevitable", 96), ("Al-Hadid", "The Iron", 29),
    ("Al-Mujadilah", "The Pleading Woman", 22), ("Al-Hashr", "The Exile", 24), ("Al-Mumtahanah", "She That Is Examined", 13),
    ("As-Saff", "The Ranks", 14), ("Al-Jumu'ah", "Friday", 11), ("Al-Munafiqun", "The Hypocrites", 11),
    ("At-Taghabun", "Mutual Disillusion", 18), ("At-Talaq", "Divorce", 12), ("At-Tahrim", "The Prohibition", 12),
    ("Al-Mulk", "The Sovereignty", 30), ("Al-Qalam", "The Pen", 52), ("Al-Haqqah", "The Reality", 52),
    ("Al-Ma'arij", "The Ascending Stairways", 44), ("Nuh", "Noah", 28), ("Al-Jinn", "The Jinn", 28),
    ("Al-Muzzammil", "The Enshrouded One", 20), ("Al-Muddaththir", "The Cloaked One", 56), ("Al-Qiyamah", "The Resurrection", 40),
    ("Al-Insan", "Man", 31), ("Al-Mursalat", "Those Sent Forth", 50), ("An-Naba", "The Tidings", 40),
    ("An-Nazi'at", "Those Who Drag Forth", 46), ("Abasa", "He Frowned", 42), ("At-Takwir", "The Overthrowing", 29),
    ("Al-Infitar", "The Cleaving", 19), ("Al-Mutaffifin", "Those Who Give Less", 36), ("Al-Inshiqaq", "The Splitting Open", 25),
    ("Al-Buruj", "The Constellations", 22), ("At-Tariq", "The Night Comer", 17), ("Al-A'la", "The Most High", 19),
    ("Al-Ghashiyah", "The Overwhelming", 26), ("Al-Fajr", "The Dawn", 30), ("Al-Balad", "The City", 20),
    ("Ash-Shams", "The Sun", 15), ("Al-Layl", "The Night", 21), ("Ad-Duha", "The Morning Hours", 11),
    ("Ash-Sharh", "The Relief", 8), ("At-Tin", "The Fig", 8), ("Al-Alaq", "The Clot", 19), ("Al-Qadr", "The Power", 5),
    ("Al-Bayyinah", "The Clear Proof", 8), ("Az-Zalzalah", "The Earthquake", 8), ("Al-Adiyat", "The Courser", 11),
    ("Al-Qari'ah", "The Calamity", 11), ("At-Takathur", "The Rivalry in World Increase", 8), ("Al-Asr", "The Declining Day", 3),
    ("Al-Humazah", "The Traducer", 9), ("Al-Fil", "The Elephant", 5), ("Quraysh", "Quraysh", 4),
    ("Al-Ma'un", "The Small Kindnesses", 7), ("Al-Kawthar", "The Abundance", 3), ("Al-Kafirun", "The Disbelievers", 6),
    ("An-Nasr", "The Divine Support", 3), ("Al-Masad", "The Palm Fibre", 5), ("Al-Ikhlas", "The Sincerity", 4),
    ("Al-Falaq", "The Daybreak", 5), ("An-Nas", "Mankind", 6),
]

TOTAL_AYAT = 6236


def surah(n: int) -> tuple[str, str, int]:
    if not 1 <= n <= 114:
        raise ValueError(f"there is no surah {n}: surahs are numbered 1 to 114")
    return SURAHS[n - 1]


def name(n: int) -> str:
    return surah(n)[0]


def ayat(n: int) -> int:
    return surah(n)[2]


def find(text: str) -> int:
    """Surah number from a number or a name ("18", "kahf", "Al-Mulk", "yasin")."""
    text = text.strip()
    if text.isdigit():
        surah(int(text))
        return int(text)
    key = _key(text)
    for i, (nm, en, _) in enumerate(SURAHS, 1):
        if key in (_key(nm), _key(nm.split("-", 1)[-1]), _key(en)):
            return i
    raise ValueError(f"no surah called {text!r}")


def _key(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum()).removeprefix("al").removeprefix("an").removeprefix("ar")
