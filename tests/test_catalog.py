import json
import re
import shutil
import subprocess
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from helpers import ROOT, SKILL, MockServer, closed_port_url, run_script
import voices


CATALOG = voices.load_catalog()

# A request a real user might type, and the voice that should come out on top.
EXPECTED_TOP = {
    "Onboarding walkthrough for our SaaS dashboard": "Dexter",
    "90-second trailer for a sci-fi audio drama": "Titan Epic",
    "Sleep story for a meditation app": "Drift",
    "Southern gothic ghost story for a horror channel": "Havoc",
    "Breaking news bulletin for a local radio station": "Derek",
    "Explainer about how vaccines work, serious tone": "Titan",
    "60-second TikTok explaining compound interest, upbeat": "Jett",
    "8-minute documentary on the Dust Bowl, warm and calm": "Timber",
    "Motivational sermon clip": "Reverend",
    "Animated mascot for a kids game": "Felix",
    "Cold call sales pitch, conversational": "Reel",
    "Trending news recap for Reels": "Pulse",
}


class CatalogIntegrity(unittest.TestCase):
    def test_fifteen_unique_voices_with_consistent_links(self):
        ids = [v["voice_id"] for v in CATALOG["voices"]]
        self.assertEqual(len(ids), 15)
        self.assertEqual(len(set(ids)), 15)
        for v in CATALOG["voices"]:
            self.assertTrue(v["share_url"].startswith("https://elevenlabs.io/app/voice-lab/share/"))
            self.assertTrue(v["share_url"].endswith("/" + v["voice_id"]))
            self.assertEqual(v["preview_url"], "https://voicefieldguide.com" + v["sample_path"])
            self.assertIn(v["voice_id"], v["sample_path"])
            self.assertEqual(v["language"], "English")

    def test_every_job_has_a_first_choice_and_no_voice_does_everything(self):
        for cat in CATALOG["categories"]:
            self.assertTrue(any(v["fit"][cat] == 3 for v in CATALOG["voices"]), cat)
        for v in CATALOG["voices"]:
            self.assertEqual(set(v["fit"]), set(CATALOG["categories"]))
            self.assertLessEqual(sum(1 for f in v["fit"].values() if f == 3), 4, v["short_name"])
            self.assertTrue(any(f == 0 for f in v["fit"].values()), v["short_name"])


class Recommendations(unittest.TestCase):
    def test_distinct_jobs_get_the_right_voice(self):
        for request, expected in EXPECTED_TOP.items():
            with self.subTest(request=request):
                top = voices.recommend(CATALOG, request)["picks"][0]["voice"]["short_name"]
                self.assertEqual(top, expected)

    def test_shortlists_actually_differ(self):
        tops = {voices.recommend(CATALOG, r)["picks"][0]["voice"]["short_name"] for r in EXPECTED_TOP}
        self.assertGreaterEqual(len(tops), 11)

    def test_specific_phrase_wins_over_generic_word(self):
        cats, _ = voices.match_request(CATALOG, "sleep story")
        self.assertEqual(cats, ["atmosphere"])

    def test_wrong_fit_voices_are_called_out(self):
        result = voices.recommend(CATALOG, "customer support walkthrough")
        skipped = [v["short_name"] for v in result["skip"]]
        self.assertIn("Titan Epic", skipped)
        picks = [p["voice"]["short_name"] for p in result["picks"]]
        self.assertFalse(set(picks) & set(skipped))

    def test_vague_request_falls_back_to_featured_and_says_so(self):
        result = voices.recommend(CATALOG, "something cool please")
        self.assertTrue(result["no_match"])
        self.assertEqual([p["voice"]["featured_order"] for p in result["picks"]], [1, 2, 3])

    def test_cli_recommend_output_has_ids_previews_and_tradeoffs(self):
        out = run_script("voices.py", "recommend", "onboarding video", "--json")
        self.assertEqual(out.returncode, 0, out.stderr)
        data = json.loads(out.stdout)
        first = data["picks"][0]
        self.assertEqual(first["short_name"], "Dexter")
        for key in ("voice_id", "preview_url", "share_url", "tradeoff"):
            self.assertTrue(first[key])


class Lookup(unittest.TestCase):
    def test_find_by_name_slug_or_id(self):
        for q in ("titan epic", "Titan-Epic", "titan-young-epic-storyteller", "f5KRUAmxOzuhrrp8V3zv"):
            self.assertEqual(voices.find_voice(CATALOG, q)["short_name"], "Titan Epic")
        self.assertEqual(voices.find_voice(CATALOG, "Titan")["short_name"], "Titan")

    def test_unknown_voice_suggests_close_names(self):
        out = run_script("voices.py", "show", "Dextr")
        self.assertEqual(out.returncode, 1)
        self.assertIn("Dexter", out.stderr)


class PreviewDownload(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _catalog_pointing_at(self, base):
        cat = json.loads(json.dumps(CATALOG))
        for v in cat["voices"]:
            v["preview_url"] = base + v["sample_path"]
        return cat

    def _args(self, **kw):
        return Namespace(voice="Drift", open=False, download=str(self.tmp / "previews"), force=False, timeout=5, **kw)

    def test_saves_real_preview_and_refuses_overwrite(self):
        srv = MockServer({"/audio/": (200, "audio/mpeg", b"ID3fakeaudio")})
        self.addCleanup(srv.close)
        cat = self._catalog_pointing_at(srv.url)
        self.assertEqual(voices.cmd_audition(self._args(), cat), 0)
        saved = self.tmp / "previews" / "drift_preview.mp3"
        self.assertEqual(saved.read_bytes(), b"ID3fakeaudio")
        with self.assertRaises(voices.ToolError):
            voices.cmd_audition(self._args(), cat)
        self.assertEqual(len(srv.requests), 1)

    def test_non_audio_response_saves_nothing(self):
        srv = MockServer({"/audio/": (200, "text/html", b"<html>login</html>")})
        self.addCleanup(srv.close)
        with self.assertRaisesRegex(voices.ToolError, "Expected audio"):
            voices.cmd_audition(self._args(), self._catalog_pointing_at(srv.url))
        self.assertEqual(list((self.tmp / "previews").iterdir()), [])

    def test_network_failure_is_reported(self):
        with self.assertRaisesRegex(voices.ToolError, "Could not reach"):
            voices.cmd_audition(self._args(), self._catalog_pointing_at(closed_port_url()))


class Showcase(unittest.TestCase):
    def test_render_embeds_catalog_safely(self):
        html = voices.render_showcase(CATALOG)
        self.assertNotIn("/*__CATALOG__*/", html)
        blob = re.search(r"window\.PRESTIGE_CATALOG = (.*?);</script>", html, re.S).group(1)
        self.assertEqual(len(json.loads(blob.replace("<\\/", "</"))["voices"]), 15)

    def test_published_showcase_matches_catalog(self):
        published = (ROOT / "showcase" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(published, voices.render_showcase(CATALOG),
                         "showcase/index.html is stale: run voices.py showcase --out showcase/index.html --force")

    def test_refuses_overwrite_and_wrong_extension(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / "page.html").write_text("keep me")
        self.assertEqual(run_script("voices.py", "showcase", "--out", str(tmp / "page.html")).returncode, 1)
        self.assertEqual((tmp / "page.html").read_text(), "keep me")
        self.assertEqual(run_script("voices.py", "showcase", "--out", str(tmp / "page.txt")).returncode, 1)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_browser_engine_ranks_like_the_cli(self):
        html = (SKILL / "assets" / "showcase.html").read_text(encoding="utf-8")
        engine = re.search(r'<script id="engine">(.*?)</script>', html, re.S).group(1)
        js = engine + "\nconst C = " + json.dumps(CATALOG) + ";\nconst reqs = " + json.dumps(list(EXPECTED_TOP)) + \
            ";\nconsole.log(JSON.stringify(reqs.map(r => globalThis.PrestigeEngine.recommend(C, r, 3).picks.map(p => p.voice.short_name))));"
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr)
        expected = [[p["voice"]["short_name"] for p in voices.recommend(CATALOG, r)["picks"]] for r in EXPECTED_TOP]
        self.assertEqual(json.loads(out.stdout), expected)


if __name__ == "__main__":
    unittest.main()
