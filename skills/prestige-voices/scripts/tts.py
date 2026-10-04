#!/usr/bin/env python3
"""Optional ElevenLabs helper for Prestige Voices. Uses YOUR ElevenLabs account.

Reads the API key from the ELEVENLABS_API_KEY environment variable and sends it
only to api.elevenlabs.io. The key is never printed, logged, or written to disk.

  check  Ask ElevenLabs whether your account can see the voice. Not billable.
  speak  Generate new speech with the selected voice. BILLABLE: it uses your
         ElevenLabs character credits, so it only sends the request when you
         pass --confirm-billable. Without that flag it prints a dry run.

There is no fallback voice and no automatic retry. If the selected voice is
unavailable, the helper stops and tells you why. Authenticated requests never
follow redirects, so the key can't be forwarded to another host.

Examples:
  python3 tts.py check --voice Dexter
  python3 tts.py speak --voice Dexter --text-file script.txt --out dexter-take1.mp3
  python3 tts.py speak --voice Dexter --text-file script.txt --out dexter-take1.mp3 --confirm-billable
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import socket
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voices import ToolError, find_voice, load_catalog  # noqa: E402

OFFICIAL_API = "https://api.elevenlabs.io"
DEFAULT_MODEL = "eleven_multilingual_v2"  # the API's documented default model_id
DEFAULT_FORMAT = "mp3_44100_128"
USER_AGENT = "prestige-voices/1.0"
MAX_AUDIO_BYTES = 200 * 1024 * 1024
FORMAT_EXT = {"mp3": ".mp3", "opus": ".opus", "wav": ".wav", "pcm": ".pcm", "ulaw": ".ulaw", "alaw": ".alaw"}


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise ToolError(
            "ELEVENLABS_API_KEY is not set. Create a key in your ElevenLabs account settings, set it in your "
            "own shell, and run this again. Don't paste the key into chat. Nothing was sent.")
    return key


def api_base(override: str | None) -> str:
    """Only the official API, or a loopback test server, may receive the key."""
    if not override:
        return OFFICIAL_API
    parsed = urllib.parse.urlparse(override)
    if parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost"):
        return override.rstrip("/")
    if override.rstrip("/") == OFFICIAL_API:
        return OFFICIAL_API
    raise ToolError("--api-base may only point at the official ElevenLabs API or a local test server.")


class _RefuseRedirects(urllib.request.HTTPRedirectHandler):
    """Authenticated requests never follow redirects, so the key can't be forwarded to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # urllib then raises HTTPError with the 3xx code


_OPENER = urllib.request.build_opener(_RefuseRedirects)


def redact(text: str, key: str) -> str:
    """Strip the key (and anything key-shaped) from server text before showing it."""
    if key:
        text = text.replace(key, "[redacted]")
    text = re.sub(r"\b(sk|xi)_[A-Za-z0-9]{16,}\b", "[redacted]", text)
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", text)
    return text.strip()[:200]


def _error_detail(err: urllib.error.HTTPError, key: str) -> tuple[str, str]:
    try:
        body = json.loads(err.read(64 * 1024).decode("utf-8", "replace"))
        detail = body.get("detail", body) if isinstance(body, dict) else body
        if isinstance(detail, dict):
            status, message = str(detail.get("status", "")), str(detail.get("message", ""))
        elif isinstance(detail, list) and detail and isinstance(detail[0], dict):
            status, message = "validation_error", str(detail[0].get("msg", ""))
        else:
            status, message = "", str(detail)
        return redact(status, key)[:60], redact(message, key)
    except Exception:
        return "", ""


def explain_http_error(err: urllib.error.HTTPError, voice: dict, key: str, model: str | None = None) -> str:
    code = err.code
    if 300 <= code < 400:
        return (f"ElevenLabs answered with a redirect (HTTP {code}). It wasn't followed, so your key went nowhere "
                "else. Nothing was generated. Try again later.")
    status, message = _error_detail(err, key)
    said = f" ElevenLabs said: {message}" if message else ""
    if code == 401 and "quota" in status:
        return f"Your ElevenLabs account is out of character credits for this request.{said}"
    if code == 401:
        return f"ElevenLabs rejected the API key (HTTP 401). Check ELEVENLABS_API_KEY and the key's permissions.{said}"
    if code in (400, 403, 404) and ("voice" in status or "voice" in message.lower() or code == 404):
        return (f"Your account can't use {voice['short_name']} yet (HTTP {code}).{said}\n"
                f"Open the share link while signed in and add the voice to My Voices:\n  {voice['share_url']}\n"
                "Voice Library voices need a paid ElevenLabs plan for API use. No other voice was tried.")
    if code == 402 or "payment" in status or "subscription" in status:
        return f"ElevenLabs says your plan or billing doesn't cover this request (HTTP {code}).{said}"
    if code == 422 or (model and "model" in (status + message).lower()):
        return (f"ElevenLabs rejected the request (HTTP {code}).{said}\n"
                f"If the message mentions the model, try --model {DEFAULT_MODEL}.")
    if code == 429:
        return f"ElevenLabs is rate limiting this account (HTTP 429). Wait a minute and try again.{said}"
    return f"ElevenLabs returned HTTP {code}.{said}"


UNKNOWN_OUTCOME = ("The connection dropped after the request was sent ({reason}), so it's unknown whether "
                   "ElevenLabs generated audio or charged credits. Nothing was saved and nothing was retried. "
                   "Check your ElevenLabs history and usage before running it again.")


def _never_sent(err: BaseException) -> bool:
    """True only when the failure happened before any bytes could reach the server."""
    reason = getattr(err, "reason", err)
    return isinstance(reason, (ConnectionRefusedError, socket.gaierror))


def _network_error(err: BaseException, billable: bool) -> ToolError:
    reason = getattr(err, "reason", err) or type(err).__name__
    if not billable or _never_sent(err):
        return ToolError(f"Could not reach ElevenLabs ({reason}). Check your connection. No request was processed.")
    return ToolError(UNKNOWN_OUTCOME.format(reason=reason))


def _open(req: urllib.request.Request, timeout: float, voice: dict, key: str, model: str | None = None,
          billable: bool = False):
    try:
        return _OPENER.open(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        raise ToolError(explain_http_error(e, voice, key, model))
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException) as e:
        raise _network_error(e, billable)


def cmd_check(args) -> int:
    voice = find_voice(load_catalog(), args.voice)
    key = api_key()
    base = api_base(args.api_base)
    req = urllib.request.Request(f"{base}/v1/voices/{voice['voice_id']}",
                                 headers={"xi-api-key": key, "User-Agent": USER_AGENT})
    with _open(req, args.timeout, voice, key) as resp:
        try:
            data = json.loads(resp.read(1024 * 1024).decode("utf-8", "replace"))
        except (ValueError, OSError, http.client.HTTPException):
            raise ToolError("ElevenLabs sent an unreadable answer, so access to the voice wasn't confirmed.")
    if not isinstance(data, dict) or data.get("voice_id") != voice["voice_id"]:
        raise ToolError(f"ElevenLabs didn't return {voice['short_name']} ({voice['voice_id']}), so access to this "
                        "voice isn't confirmed. Add it from its share link and check again:\n  " + voice["share_url"])
    print(f"Your account can see {voice['short_name']} ({voice['voice_id']}).")
    if data.get("name"):
        print(f"Name in your account: {redact(str(data['name']), key)}")
    if data.get("category"):
        print(f"Category: {redact(str(data['category']), key)}")
    print("This check used no credits. Generation still depends on your plan, credits and model.")
    return 0


def read_text(args) -> str:
    if args.text is not None:
        text = args.text
    else:
        path = Path(args.text_file).expanduser()
        if not path.is_file():
            raise ToolError(f"Script file {path} not found.")
        text = path.read_text(encoding="utf-8")
    text = text.strip()
    if not text:
        raise ToolError("The script is empty. Nothing was sent.")
    return text


def output_path(args) -> Path:
    out = Path(args.out).expanduser()
    expected = FORMAT_EXT.get(args.format.split("_", 1)[0])
    if expected and out.suffix.lower() != expected:
        raise ToolError(f"--out should end in {expected} for format {args.format}.")
    if out.exists() and out.is_dir():
        raise ToolError(f"{out} is a folder. Give a file name.")
    if out.exists() and not args.force:
        raise ToolError(f"{out} already exists. Pick a new name or pass --force.")
    if not out.parent.is_dir():
        raise ToolError(f"Folder {out.parent} does not exist.")
    return out


def cmd_speak(args) -> int:
    voice = find_voice(load_catalog(), args.voice)
    text = read_text(args)
    out = output_path(args)
    if args.speed is not None and not 0.7 <= args.speed <= 1.2:
        raise ToolError("--speed must be between 0.7 and 1.2 (ElevenLabs' documented range).")
    for flag in ("stability", "similarity", "style"):
        value = getattr(args, flag)
        if value is not None and not 0.0 <= value <= 1.0:
            raise ToolError(f"--{flag} must be between 0 and 1.")
    settings = {k: v for k, v in (("stability", args.stability), ("similarity_boost", args.similarity),
                                  ("style", args.style), ("speed", args.speed)) if v is not None}
    summary = (f"Voice: {voice['short_name']} ({voice['voice_id']})\nModel: {args.model}\n"
               f"Characters: {len(text)}\nOutput: {out}")
    if not args.confirm_billable:
        print("Dry run. Nothing was sent to ElevenLabs.\n" + summary)
        print("This request would use your ElevenLabs character credits. Re-run with --confirm-billable to generate.")
        return 0
    key = api_key()
    base = api_base(args.api_base)
    body = {"text": text, "model_id": args.model}
    if settings:
        body["voice_settings"] = settings
    query = urllib.parse.urlencode({"output_format": args.format})
    req = urllib.request.Request(
        f"{base}/v1/text-to-speech/{voice['voice_id']}?{query}", method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/*",
                 "User-Agent": USER_AGENT})
    with _open(req, args.timeout, voice, key, args.model, billable=True) as resp:
        ctype = resp.headers.get("Content-Type", "")
        request_id = redact(resp.headers.get("request-id", ""), key)
        if not (ctype.startswith("audio/") or ctype == "application/octet-stream"):
            raise ToolError(f"Expected audio but ElevenLabs sent '{redact(ctype, key)}'. Nothing was saved.")
        fd, tmp = tempfile.mkstemp(dir=out.parent, suffix=".part")
        size = 0
        try:
            with os.fdopen(fd, "wb") as fh:
                while True:
                    try:
                        chunk = resp.read(64 * 1024)
                    except (TimeoutError, OSError, http.client.HTTPException) as e:
                        raise ToolError(UNKNOWN_OUTCOME.format(reason=f"{type(e).__name__} while downloading the audio"))
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_AUDIO_BYTES:
                        raise ToolError("Response was larger than expected. Nothing was saved.")
                    fh.write(chunk)
            if size == 0:
                raise ToolError("ElevenLabs returned no audio. Nothing was saved.")
            os.replace(tmp, out)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    print("Generated new speech with ElevenLabs.\n" + summary)
    print(f"Saved {size} bytes." + (f" Request ID: {request_id}" if request_id else ""))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tts.py", description="Optional ElevenLabs helper. Uses ELEVENLABS_API_KEY.")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("check", "speak"):
        s = sub.add_parser(name)
        s.add_argument("--voice", required=True, help="short name, slug or voice ID from the collection")
        s.add_argument("--timeout", type=float, default=60 if name == "speak" else 20)
        s.add_argument("--api-base", help=argparse.SUPPRESS)
        if name == "speak":
            src = s.add_mutually_exclusive_group(required=True)
            src.add_argument("--text")
            src.add_argument("--text-file")
            s.add_argument("--out", required=True)
            s.add_argument("--model", default=DEFAULT_MODEL)
            s.add_argument("--format", default=DEFAULT_FORMAT)
            s.add_argument("--stability", type=float)
            s.add_argument("--similarity", type=float)
            s.add_argument("--style", type=float)
            s.add_argument("--speed", type=float)
            s.add_argument("--force", action="store_true", help="replace an existing output file")
            s.add_argument("--confirm-billable", action="store_true",
                           help="actually send the request; uses your ElevenLabs credits")
    return p


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        return {"check": cmd_check, "speak": cmd_speak}[args.cmd](args)
    except ToolError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
