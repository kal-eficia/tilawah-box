"""Physical controls: a rotary dial, buttons and optional NFC cards. No screen.

Default wiring (BCM pin numbers, change in config.json):
  dial A/B   17 / 27   turn to choose the surah (plays straight away if already playing)
  dial press 22        play / pause
  button     5         next reciter
  button     6         memorisation mode: repeat each ayah 1, 3, 5 or 10 times
  button     13 / 19   volume down / up
  NFC reader (RC522 on SPI)   tap a card to play its surah: made for small hands
"""
from __future__ import annotations

import threading

DEFAULT_PINS = {"dial_a": 17, "dial_b": 27, "dial_press": 22, "reciter": 5, "hifz": 6, "vol_down": 13, "vol_up": 19}


def attach_gpio(player, pins: dict | None = None, on_change=None):
    """Wire the Pi's GPIO to the player. Needs gpiozero (preinstalled on Raspberry Pi OS)."""
    from gpiozero import Button, RotaryEncoder  # imported here so the rest runs anywhere

    p = {**DEFAULT_PINS, **(pins or {})}
    lock = threading.Lock()

    def act(fn):
        def run(*_):
            with lock:
                fn()
                if on_change:
                    on_change(player)
        return run

    dial = RotaryEncoder(p["dial_a"], p["dial_b"], max_steps=0)
    dial.when_rotated_clockwise = act(lambda: player.step_surah(+1))
    dial.when_rotated_counter_clockwise = act(lambda: player.step_surah(-1))
    buttons = {
        "dial_press": act(player.toggle), "reciter": act(player.next_reciter), "hifz": act(player.cycle_hifz),
        "vol_down": act(lambda: player.change_volume(-5)), "vol_up": act(lambda: player.change_volume(+5)),
    }
    held = []
    for key, fn in buttons.items():
        b = Button(p[key], bounce_time=0.05)
        b.when_pressed = fn
        held.append(b)
    return [dial, *held]  # keep references alive


def card_action(cards: dict, uid: str) -> dict | None:
    """What a tapped card should do: {"surah": 36} or {"surah": 2, "from": 255, "to": 255}."""
    return cards.get(str(uid))


def watch_cards(player, cards: dict, on_change=None, on_unknown=None):
    """Poll an RC522 reader in a background thread. Needs `pip install mfrc522`."""
    from mfrc522 import SimpleMFRC522

    from .quran import find

    reader = SimpleMFRC522()

    def loop():
        last = None
        while True:
            uid, _ = reader.read()
            if uid == last:
                continue  # card still resting on the reader
            last = uid
            action = card_action(cards, str(uid))
            if not action:
                if on_unknown:
                    on_unknown(uid)
                continue
            rng = (action["from"], action["to"]) if "from" in action else None
            player.play(find(str(action["surah"])), rng)
            if on_change:
                on_change(player)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return t


KEYS = {
    "→ / d": "next surah", "← / a": "previous surah", "space": "play / pause", "r": "next reciter",
    "h": "memorisation repeat", "+ / -": "volume", "s": "stop", "q": "quit",
}


def handle_key(player, key: str) -> bool:
    """Simulator keys. Returns False to quit."""
    k = key.lower()
    if k in ("q", "\x03"):
        return False
    acts = {"d": lambda: player.step_surah(+1), "a": lambda: player.step_surah(-1), "\x1b[c": lambda: player.step_surah(+1),
            "\x1b[d": lambda: player.step_surah(-1), " ": player.toggle, "r": player.next_reciter, "h": player.cycle_hifz,
            "+": lambda: player.change_volume(+5), "=": lambda: player.change_volume(+5), "-": lambda: player.change_volume(-5),
            "s": player.stop}
    if k in acts:
        acts[k]()
    return True
