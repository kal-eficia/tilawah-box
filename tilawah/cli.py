"""tilawah: a screen-free Quran player for the home.

  tilawah sim                         try it on any computer with the keyboard
  tilawah run --config config.json    run on the Raspberry Pi with the dial, buttons and cards
  tilawah sync --surahs 1,18,36,67,78-114 --reciter alafasy   download for offline use
  tilawah play kahf --reciter husary  play one surah and exit
  tilawah list                        surahs and reciters
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from . import __version__
from .config import load
from .player import DryRunBackend, MpvBackend, Player
from .quran import SURAHS, ayat, find, name
from .schedule import Schedule
from .sources import RECITERS, Library


def parse_surahs(spec: str) -> list[int]:
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part and part.replace("-", "").isdigit():
            a, b = map(int, part.split("-"))
            out += list(range(a, b + 1))
        else:
            out.append(find(part))
    return out


def make_player(cfg, dry=False, echo=None) -> Player:
    backend = DryRunBackend(echo) if dry else MpvBackend()
    return Player(Library(cfg["library"]), backend, cfg["reciters"], surah=cfg["start_surah"],
                  volume=cfg["volume"], max_volume=cfg["max_volume"])


def run_schedule_loop(player, schedule: Schedule, tz: str, on_change, stop_after: float | None = None):
    zone = ZoneInfo(tz)
    last = datetime.now(zone)
    started = time.monotonic()
    normal_max = player.max_volume
    while stop_after is None or time.monotonic() - started < stop_after:
        time.sleep(2)
        now = datetime.now(zone)
        if schedule.quiet:
            quiet = schedule.quiet.active(now)
            player.max_volume = min(normal_max, schedule.quiet.volume) if quiet else normal_max
            if player.volume > player.max_volume:
                player.change_volume(0)
        for r in schedule.due(last, now):
            if r.action == "stop":
                player.stop()
            else:
                if r.reciter and r.reciter in player.reciters:
                    player.reciter_index = player.reciters.index(r.reciter)
                player.play(r.surah)
            on_change(player)
        last = now


def _getch():
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="tilawah", description="A screen-free Quran player for the home.")
    ap.add_argument("--version", action="version", version=f"tilawah-box {__version__}")
    ap.add_argument("--config", default="config.json")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sim = sub.add_parser("sim", help="keyboard simulator"); sim.add_argument("--silent", action="store_true")
    sub.add_parser("run", help="run on the Pi")
    sy = sub.add_parser("sync", help="download surahs for offline use")
    sy.add_argument("--surahs", default="1,18,36,55,56,67,78-114"); sy.add_argument("--reciter", default="alafasy")
    pl = sub.add_parser("play"); pl.add_argument("surah"); pl.add_argument("--reciter")
    pl.add_argument("--from", dest="start", type=int); pl.add_argument("--to", dest="end", type=int)
    pl.add_argument("--repeat", type=int, default=1, help="play each ayah this many times")
    sub.add_parser("list")
    sub.add_parser("check", help="check each reciter's audio source is reachable")
    a = ap.parse_args(argv)
    cfg = load(a.config)

    if a.cmd == "list":
        for i, (nm, en, n) in enumerate(SURAHS, 1):
            print(f"{i:>3}  {nm:<16} {en:<32} {n} ayat")
        print("\nReciters: " + ", ".join(f"{k} ({v[1]})" for k, v in RECITERS.items()))
        return 0

    if a.cmd == "check":
        import urllib.request
        from .sources import url
        ok = True
        for key, (_, label) in RECITERS.items():
            try:
                req = urllib.request.Request(url(key, 1, 1), method="HEAD", headers={"User-Agent": "tilawah-box/1.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    status = r.status
            except Exception as e:  # noqa: BLE001
                status, ok = str(e), False
            print(f"  {key:<15} {label:<45} {status}")
        return 0 if ok else 1

    if a.cmd == "sync":
        lib = Library(cfg["library"])
        for s in parse_surahs(a.surahs):
            got = lib.download(a.reciter, s)
            print(f"  {s:>3}. {name(s):<16} {'cached' if not got else f'{got} ayat downloaded'}")
        return 0

    if a.cmd == "play":
        p = make_player(cfg)
        if a.reciter:
            p.reciters = [a.reciter] + [r for r in p.reciters if r != a.reciter]
        p.hifz_repeat = a.repeat
        s = find(a.surah)
        rng = (a.start or 1, a.end or ayat(s)) if (a.start or a.end) else None
        p.play(s, rng)
        print(p.describe())
        try:
            while not p.backend.finished():
                time.sleep(0.5)
        except KeyboardInterrupt:
            p.stop()
        return 0

    def show(player):
        print("\r\033[K" + player.describe(), end="", flush=True) if sys.stdout.isatty() else print(player.describe())

    if a.cmd == "sim":
        from .controls import KEYS, handle_key
        p = make_player(cfg, dry=a.silent)
        print("Tilawah Box simulator. Keys: " + " · ".join(f"{k} {v}" for k, v in KEYS.items()) + "\n")
        show(p)
        try:
            while handle_key(p, _getch()):
                show(p)
        finally:
            p.stop()
            print()
        return 0

    # run on the Pi
    from .controls import attach_gpio, watch_cards
    p = make_player(cfg)
    keep = attach_gpio(p, cfg["pins"], on_change=show)  # noqa: F841 - references keep the pins alive
    if cfg["cards"]:
        try:
            watch_cards(p, cfg["cards"], on_change=show, on_unknown=lambda uid: print(f"\nunknown card {uid}: add it to config.json"))
        except ImportError:
            print("NFC cards configured but mfrc522 isn't installed: pip install mfrc522")
    print("Tilawah Box ready.")
    show(p)
    try:
        run_schedule_loop(p, Schedule.from_config(cfg), cfg["timezone"], show)
    except KeyboardInterrupt:
        p.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
