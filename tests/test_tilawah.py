import unittest
from datetime import datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory

from tilawah.controls import card_action, handle_key
from tilawah.player import DryRunBackend, Player
from tilawah.quran import SURAHS, TOTAL_AYAT, ayat, find
from tilawah.schedule import QuietHours, Schedule
from tilawah.sources import Library, url


def player(tmp, **kw):
    return Player(Library(tmp), DryRunBackend(), **kw)


class Quran(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(SURAHS), 114)
        self.assertEqual(sum(n for *_, n in SURAHS), TOTAL_AYAT)

    def test_find_by_name_or_number(self):
        for text, n in [("kahf", 18), ("Al-Mulk", 67), ("yasin", 36), ("36", 36), ("The Cave", 18), ("ikhlas", 112)]:
            self.assertEqual(find(text), n)
        with self.assertRaises(ValueError):
            find("115")


class Playback(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.p = player(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_bismillah_rules(self):
        self.p.play(18)
        self.assertEqual(len(self.p.backend.playlist), ayat(18) + 1)
        self.assertTrue(self.p.backend.playlist[0].endswith("001001.mp3"))
        self.p.play(9)
        self.assertEqual(len(self.p.backend.playlist), ayat(9))
        self.p.play(1)
        self.assertEqual(len(self.p.backend.playlist), 7)

    def test_range_for_ayat_al_kursi(self):
        self.p.play(2, (255, 255))
        self.assertEqual(self.p.backend.playlist, [url("alafasy", 2, 255)])
        with self.assertRaises(ValueError):
            self.p.play(112, (1, 9))

    def test_cached_files_are_used(self):
        f = Library(self.tmp.name).path("alafasy", 112, 1)
        f.parent.mkdir(parents=True)
        f.write_bytes(b"x")
        self.p.play(112, (1, 1))
        self.assertEqual(self.p.backend.playlist[-1], str(f))  # after the bismillah

    def test_dial_wraps_round(self):
        self.p.surah = 114
        self.p.step_surah(+1)
        self.assertEqual(self.p.surah, 1)
        self.p.step_surah(-1)
        self.assertEqual(self.p.surah, 114)

    def test_volume_is_capped(self):
        for _ in range(30):
            self.p.change_volume(+5)
        self.assertEqual(self.p.volume, self.p.max_volume)

    def test_hifz_cycle_and_pause(self):
        self.p.play(114)
        seen = []
        for _ in range(4):
            self.p.cycle_hifz()
            seen.append(self.p.hifz_repeat)
        self.assertEqual(seen, [3, 5, 10, 1])
        self.p.hifz_repeat = 3
        self.p.play(112)
        self.assertEqual(len(self.p.backend.playlist), 1 + 4 * 3)  # bismillah once, each ayah three times
        self.p.toggle()
        self.assertTrue(self.p.backend.paused)

    def test_keys(self):
        handle_key(self.p, "d")
        self.assertEqual(self.p.surah, 2)
        handle_key(self.p, " ")
        self.assertTrue(self.p.playing)
        self.assertFalse(handle_key(self.p, "q"))

    def test_unknown_reciter(self):
        with self.assertRaises(ValueError):
            player(self.tmp.name, reciters=["nobody"])


class Schedules(unittest.TestCase):
    def test_friday_kahf(self):
        s = Schedule.from_config({"routines": [{"days": "fri", "time": "07:30", "surah": "kahf"}]})
        fri = datetime(2026, 11, 27, 7, 29, 58)
        self.assertEqual([r.surah for r in s.due(fri, fri.replace(minute=30, second=1))], [18])
        thu = datetime(2026, 11, 26, 7, 29, 58)
        self.assertEqual(s.due(thu, thu.replace(minute=30, second=1)), [])

    def test_due_across_midnight(self):
        s = Schedule.from_config({"routines": [{"days": "daily", "time": "00:00", "action": "stop"}]})
        self.assertEqual(len(s.due(datetime(2026, 11, 25, 23, 59, 59), datetime(2026, 11, 26, 0, 0, 1))), 1)

    def test_quiet_hours_cross_midnight(self):
        q = QuietHours(time(21, 30), time(6, 30))
        self.assertTrue(q.active(datetime(2026, 1, 1, 23, 0)))
        self.assertTrue(q.active(datetime(2026, 1, 1, 5, 0)))
        self.assertFalse(q.active(datetime(2026, 1, 1, 12, 0)))

    def test_bad_day(self):
        with self.assertRaises(ValueError):
            Schedule.from_config({"routines": [{"days": "funday", "time": "07:00", "surah": 1}]})


class Cards(unittest.TestCase):
    def test_card_lookup(self):
        cards = {"5841239": {"surah": "yasin"}, "77": {"surah": 2, "from": 255, "to": 255}}
        self.assertEqual(card_action(cards, "77")["from"], 255)
        self.assertIsNone(card_action(cards, "000"))


if __name__ == "__main__":
    unittest.main()
