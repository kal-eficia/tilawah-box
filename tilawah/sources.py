"""Where the recitation comes from, and the local cache that lets the box work offline.

Audio is per ayah from EveryAyah (everyayah.com), so the box can repeat a single
ayah for memorisation or play any range. Files are cached on the SD card the
first time they're played, or ahead of time with `tilawah sync`.
"""
from __future__ import annotations

import os
import shutil
import urllib.request
from pathlib import Path

from .quran import ayat

BASE = "https://everyayah.com/data"

# key: (EveryAyah folder, display name)
RECITERS = {
    "alafasy": ("Alafasy_128kbps", "Mishary Rashid Alafasy"),
    "husary": ("Husary_128kbps", "Mahmoud Khalil Al-Husary"),
    "husary-muallim": ("Husary_Muallim_128kbps", "Al-Husary (teaching, with pauses to repeat)"),
    "minshawi": ("Minshawy_Murattal_128kbps", "Muhammad Siddiq Al-Minshawi"),
    "abdulbasit": ("Abdul_Basit_Murattal_192kbps", "Abdul Basit Abdus Samad"),
    "sudais": ("Abdurrahmaan_As-Sudais_192kbps", "Abdurrahman As-Sudais"),
    "shuraim": ("Saood_ash-Shuraym_128kbps", "Saud Ash-Shuraim"),
    "muaiqly": ("MaherAlMuaiqly128kbps", "Maher Al-Muaiqly"),
    "shaatree": ("Abu_Bakr_Ash-Shaatree_128kbps", "Abu Bakr Ash-Shatri"),
}


def url(reciter: str, surah: int, ayah: int) -> str:
    folder = RECITERS[reciter][0]
    return f"{BASE}/{folder}/{surah:03d}{ayah:03d}.mp3"


class Library:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser()

    def path(self, reciter: str, surah: int, ayah: int) -> Path:
        return self.root / reciter / f"{surah:03d}{ayah:03d}.mp3"

    def source(self, reciter: str, surah: int, ayah: int) -> str:
        """Local file if cached, otherwise the stream URL."""
        p = self.path(reciter, surah, ayah)
        return str(p) if p.exists() else url(reciter, surah, ayah)

    def has_surah(self, reciter: str, surah: int) -> bool:
        return all(self.path(reciter, surah, a).exists() for a in range(1, ayat(surah) + 1))

    def download(self, reciter: str, surah: int, progress=None) -> int:
        """Fetch every ayah of a surah that isn't cached yet. Returns files fetched."""
        fetched = 0
        for a in range(1, ayat(surah) + 1):
            p = self.path(reciter, surah, a)
            if p.exists():
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp = p.with_suffix(".part")
            req = urllib.request.Request(url(reciter, surah, a), headers={"User-Agent": "tilawah-box/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(tmp, "wb") as f:
                shutil.copyfileobj(r, f)
            os.replace(tmp, p)
            fetched += 1
            if progress:
                progress(surah, a)
        return fetched
