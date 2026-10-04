import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import MockServer, closed_port_url, json_body, run_script

FAKE_KEY = "test-key-should-never-be-printed-123"
DEXTER = "Smxkoz0xiOoHo5WcSskf"


class TTSHelper(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.env = {k: v for k, v in os.environ.items() if k != "ELEVENLABS_API_KEY"}
        self.env["PYTHONIOENCODING"] = "utf-8"
        self.script = self.tmp / "script.txt"
        self.script.write_text("Click Settings, then Billing. Your invoices are on the left.", encoding="utf-8")

    def server(self, routes):
        srv = MockServer(routes)
        self.addCleanup(srv.close)
        return srv

    def speak(self, base, *extra, key=True, out="take.mp3"):
        env = dict(self.env)
        if key:
            env["ELEVENLABS_API_KEY"] = FAKE_KEY
        res = run_script("tts.py", "speak", "--voice", "Dexter", "--text-file", str(self.script),
                         "--out", str(self.tmp / out), "--api-base", base, *extra, env=env)
        self.assertNotIn(FAKE_KEY, res.stdout + res.stderr)
        return res

    def test_dry_run_sends_nothing_without_explicit_billing_consent(self):
        srv = self.server({"/": (200, "audio/mpeg", b"audio")})
        res = self.speak(srv.url)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Nothing was sent", res.stdout)
        self.assertNotIn("Generated", res.stdout)
        self.assertEqual(srv.requests, [])
        self.assertFalse((self.tmp / "take.mp3").exists())

    def test_missing_key_stops_before_any_request(self):
        srv = self.server({"/": (200, "audio/mpeg", b"audio")})
        res = self.speak(srv.url, "--confirm-billable", key=False)
        self.assertEqual(res.returncode, 1)
        self.assertIn("ELEVENLABS_API_KEY is not set", res.stderr)
        self.assertEqual(srv.requests, [])

    def test_generates_with_the_selected_voice_only(self):
        srv = self.server({f"/v1/text-to-speech/{DEXTER}": (200, "audio/mpeg", b"ID3generated")})
        res = self.speak(srv.url, "--confirm-billable", "--speed", "0.95")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual((self.tmp / "take.mp3").read_bytes(), b"ID3generated")
        self.assertIn("Generated new speech", res.stdout)
        [req] = srv.requests
        self.assertEqual(req["method"], "POST")
        self.assertTrue(req["path"].startswith(f"/v1/text-to-speech/{DEXTER}?output_format=mp3_44100_128"))
        self.assertEqual(req["headers"].get("xi-api-key"), FAKE_KEY)
        body = json.loads(req["body"])
        self.assertEqual(body["model_id"], "eleven_multilingual_v2")
        self.assertEqual(body["voice_settings"], {"speed": 0.95})

    def test_denied_voice_points_to_share_link_and_tries_no_other_voice(self):
        srv = self.server({"/v1/": (404, "application/json", json_body("voice_not_found", "Voice not found"))})
        res = self.speak(srv.url, "--confirm-billable")
        self.assertEqual(res.returncode, 1)
        self.assertIn("can't use Dexter", res.stderr)
        self.assertIn("voice-lab/share/", res.stderr)
        self.assertIn("No other voice was tried", res.stderr)
        self.assertEqual(len(srv.requests), 1)
        self.assertEqual(list(self.tmp.glob("*.mp3")) + list(self.tmp.glob("*.part")), [])

    def test_bad_key_and_quota_are_told_apart(self):
        srv = self.server({"/v1/": (401, "application/json", json_body("invalid_api_key", "Invalid API key"))})
        self.assertIn("rejected the API key", self.speak(srv.url, "--confirm-billable").stderr)
        srv2 = self.server({"/v1/": (401, "application/json", json_body("quota_exceeded", "quota exceeded"))})
        self.assertIn("out of character credits", self.speak(srv2.url, "--confirm-billable").stderr)

    def test_validation_error_suggests_default_model(self):
        srv = self.server({"/v1/": (422, "application/json", json_body("invalid_model", "model not supported"))})
        res = self.speak(srv.url, "--confirm-billable", "--model", "eleven_v3")
        self.assertIn("--model eleven_multilingual_v2", res.stderr)

    def test_refused_connection_means_nothing_was_processed(self):
        res = self.speak(closed_port_url(), "--confirm-billable")
        self.assertEqual(res.returncode, 1)
        self.assertIn("Could not reach ElevenLabs", res.stderr)
        self.assertIn("No request was processed", res.stderr)
        self.assertFalse((self.tmp / "take.mp3").exists())

    def test_dropped_connection_after_send_reports_unknown_billing_and_does_not_retry(self):
        srv = self.server({"/v1/": ("hangup", "", b"")})
        res = self.speak(srv.url, "--confirm-billable")
        self.assertEqual(res.returncode, 1)
        self.assertIn("unknown whether ElevenLabs generated audio or charged credits", res.stderr)
        self.assertNotIn("Nothing was generated", res.stderr)
        self.assertEqual(len(srv.requests), 1)
        self.assertEqual(list(self.tmp.glob("*.mp3")) + list(self.tmp.glob("*.part")), [])

    def test_redirect_is_refused_so_the_key_never_reaches_another_host(self):
        elsewhere = self.server({"/": (200, "audio/mpeg", b"stolen")})
        srv = self.server({"/v1/": (302, "text/plain", b"", {"Location": elsewhere.url + "/collect"})})
        res = self.speak(srv.url, "--confirm-billable")
        self.assertEqual(res.returncode, 1)
        self.assertIn("redirect", res.stderr)
        self.assertEqual(elsewhere.requests, [])
        env = dict(self.env, ELEVENLABS_API_KEY=FAKE_KEY)
        chk = run_script("tts.py", "check", "--voice", "Dexter", "--api-base", srv.url, env=env)
        self.assertEqual(chk.returncode, 1)
        self.assertEqual(elsewhere.requests, [])
        self.assertFalse((self.tmp / "take.mp3").exists())

    def test_server_text_that_echoes_the_key_is_redacted(self):
        echo = json_body("invalid_api_key", f"Key {FAKE_KEY} is not valid")
        srv = self.server({"/v1/": (401, "application/json", echo)})
        res = self.speak(srv.url, "--confirm-billable")  # speak() asserts the key never appears in output
        self.assertIn("[redacted]", res.stderr)

    def test_html_instead_of_audio_saves_nothing(self):
        srv = self.server({"/v1/": (200, "text/html", b"<html>oops</html>")})
        res = self.speak(srv.url, "--confirm-billable")
        self.assertEqual(res.returncode, 1)
        self.assertEqual(list(self.tmp.glob("*.mp3")) + list(self.tmp.glob("*.part")), [])

    def test_output_path_safety_checked_before_sending(self):
        srv = self.server({"/": (200, "audio/mpeg", b"audio")})
        (self.tmp / "exists.mp3").write_bytes(b"keep")
        cases = {"exists.mp3": "already exists", "missing/take.mp3": "does not exist", "take.wav": "should end in .mp3"}
        for out, msg in cases.items():
            with self.subTest(out=out):
                res = self.speak(srv.url, "--confirm-billable", out=out)
                self.assertEqual(res.returncode, 1)
                self.assertIn(msg, res.stderr)
        self.assertEqual((self.tmp / "exists.mp3").read_bytes(), b"keep")
        self.assertEqual(srv.requests, [])

    def test_key_only_goes_to_official_api_or_loopback(self):
        res = self.speak("https://example.com", "--confirm-billable")
        self.assertEqual(res.returncode, 1)
        self.assertIn("--api-base may only point", res.stderr)

    def test_out_of_range_speed_is_rejected_locally(self):
        srv = self.server({"/": (200, "audio/mpeg", b"audio")})
        res = self.speak(srv.url, "--confirm-billable", "--speed", "2")
        self.assertIn("between 0.7 and 1.2", res.stderr)
        self.assertEqual(srv.requests, [])

    def test_check_reports_access_without_generating(self):
        payload = json.dumps({"voice_id": DEXTER, "name": "Dexter", "category": "professional"}).encode()
        srv = self.server({f"/v1/voices/{DEXTER}": (200, "application/json", payload)})
        env = dict(self.env, ELEVENLABS_API_KEY=FAKE_KEY)
        res = run_script("tts.py", "check", "--voice", "dexter", "--api-base", srv.url, env=env)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Your account can see Dexter", res.stdout)
        self.assertEqual(srv.requests[0]["method"], "GET")
        self.assertNotIn(FAKE_KEY, res.stdout + res.stderr)

    def test_check_rejects_a_response_for_a_different_voice(self):
        payload = json.dumps({"voice_id": "SomeOtherVoice123456", "name": "Someone else"}).encode()
        srv = self.server({"/v1/voices/": (200, "application/json", payload)})
        env = dict(self.env, ELEVENLABS_API_KEY=FAKE_KEY)
        res = run_script("tts.py", "check", "--voice", "Dexter", "--api-base", srv.url, env=env)
        self.assertEqual(res.returncode, 1)
        self.assertIn("isn't confirmed", res.stderr)
        self.assertNotIn("Your account can see", res.stdout)


if __name__ == "__main__":
    unittest.main()
