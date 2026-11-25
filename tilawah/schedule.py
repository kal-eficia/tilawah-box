"""Routines and quiet hours.

  {"days": "fri", "time": "07:30", "surah": "kahf"}          Al-Kahf every Friday morning
  {"days": "daily", "time": "20:30", "surah": "mulk"}        Al-Mulk before bed
  {"days": "mon,thu", "time": "17:00", "surah": "36", "reciter": "husary"}
  {"days": "daily", "time": "21:15", "action": "stop"}
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta

from .quran import find

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _parse_days(spec: str) -> set[int]:
    spec = spec.lower().strip()
    if spec in ("daily", "every day", "*"):
        return set(range(7))
    if spec == "weekdays":
        return set(range(5))
    if spec == "weekends":
        return {5, 6}
    out = set()
    for part in spec.split(","):
        part = part.strip()[:3]
        if part not in DAYS:
            raise ValueError(f"unknown day {part!r}: use mon..sun, daily, weekdays or weekends")
        out.add(DAYS.index(part))
    return out


def _parse_time(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


@dataclass
class Routine:
    days: set[int]
    at: time
    action: str = "play"
    surah: int | None = None
    reciter: str | None = None
    label: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Routine":
        action = d.get("action", "play")
        if action not in ("play", "stop"):
            raise ValueError("a routine's action is 'play' or 'stop'")
        surah = find(str(d["surah"])) if action == "play" else None
        return cls(_parse_days(d.get("days", "daily")), _parse_time(d["time"]), action, surah, d.get("reciter"),
                   d.get("label", ""))


@dataclass
class QuietHours:
    start: time
    end: time
    volume: int = 25

    def active(self, now: datetime) -> bool:
        t = now.time()
        if self.start <= self.end:
            return self.start <= t < self.end
        return t >= self.start or t < self.end  # crosses midnight


class Schedule:
    def __init__(self, routines: list[Routine], quiet: QuietHours | None = None):
        self.routines = routines
        self.quiet = quiet

    @classmethod
    def from_config(cls, cfg: dict) -> "Schedule":
        routines = [Routine.from_dict(r) for r in cfg.get("routines", [])]
        q = cfg.get("quiet_hours")
        quiet = QuietHours(_parse_time(q["from"]), _parse_time(q["to"]), q.get("volume", 25)) if q else None
        return cls(routines, quiet)

    def due(self, since: datetime, now: datetime) -> list[Routine]:
        """Routines whose time fell in (since, now]. Call this every few seconds."""
        out = []
        day = since.date()
        while day <= now.date():
            for r in self.routines:
                if day.weekday() in r.days:
                    at = datetime.combine(day, r.at, tzinfo=now.tzinfo)
                    if since < at <= now:
                        out.append(r)
            day += timedelta(days=1)
        return out
