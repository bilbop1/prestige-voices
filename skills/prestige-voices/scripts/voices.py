#!/usr/bin/env python3
"""Prestige Voices catalog and audition tool.

Works offline for list/show/recommend. Network is used only when you ask for it
(audition --download, check-links). No API key, no account, nothing billable.

Examples:
  python3 voices.py recommend "60-second TikTok explaining compound interest, upbeat"
  python3 voices.py show Dexter
  python3 voices.py audition "Titan Epic" --open
  python3 voices.py audition Drift --download ./previews
  python3 voices.py showcase --out ./prestige-voices.html --open
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = SKILL_DIR / "references" / "voices.json"
SHOWCASE_TEMPLATE = SKILL_DIR / "assets" / "showcase.html"
USER_AGENT = "prestige-voices/1.0 (+https://github.com/bilbop1/prestige-voices)"
FIT_LABEL = {0: "wrong fit", 1: "possible", 2: "good", 3: "first choice"}
MAX_PREVIEW_BYTES = 3 * 1024 * 1024


class ToolError(Exception):
    """An expected failure with a message meant for the user."""


# ---------------------------------------------------------------- catalog

def load_catalog(path: Path = CATALOG_PATH) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ToolError(f"Catalog not found at {path}. Reinstall the plugin.")


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def find_voice(catalog: dict, query: str) -> dict:
    q = _norm(query)
    for v in catalog["voices"]:
        if q in (_norm(v["short_name"]), _norm(v["slug"]), v["voice_id"].lower(), _norm(v["voice_id"])):
            return v
    names = [v["short_name"] for v in catalog["voices"]]
    close = difflib.get_close_matches(query, names, n=3, cutoff=0.5)
    hint = f" Did you mean: {', '.join(close)}?" if close else ""
    raise ToolError(f"No voice named '{query}'.{hint} Voices: {', '.join(names)}")


def fmt_duration(seconds: float) -> str:
    return f"0:{round(seconds):02d}"


# ---------------------------------------------------------------- matching

def _consume(text: str, table: dict[str, list[str]]) -> tuple[list[str], str]:
    """Match longest phrases first and blank them out, so "sleep story" doesn't also count as "story".
    Returns keys ordered by where they first appear in the text."""
    pairs = sorted(((w, k) for k, words in table.items() for w in words), key=lambda p: -len(p[0]))
    first_pos: dict[str, int] = {}
    for word, key in pairs:
        pattern = r"(?<![a-z0-9])" + re.escape(word) + r"(?![a-z0-9])"
        for m in list(re.finditer(pattern, text)):
            first_pos[key] = min(first_pos.get(key, m.start()), m.start())
            text = text[:m.start()] + " " * len(word) + text[m.end():]
    return sorted(first_pos, key=first_pos.get), text


def match_request(catalog: dict, request: str) -> tuple[list[str], list[str]]:
    text = request.lower()
    cats, _ = _consume(text, {c: spec["keywords"] for c, spec in catalog["categories"].items()})
    traits, _ = _consume(text, catalog["traits"])
    return cats, traits


def score_voice(voice: dict, cats: list[str], traits: list[str]) -> int:
    """The first format named in the request counts most. A wrong fit (0) costs points."""
    score = 0
    for i, c in enumerate(cats):
        fit = voice["fit"][c]
        weight = 12 if i == 0 else 8
        score += fit * weight if fit else -weight
    score += 4 * sum(1 for t in traits if t in voice["traits"])
    return score


def recommend(catalog: dict, request: str, top: int = 3) -> dict:
    cats, traits = match_request(catalog, request)
    featured_rank = lambda v: v["featured_order"] or 99
    if not cats and not traits:
        picks = sorted((v for v in catalog["voices"] if v["featured_order"]), key=featured_rank)[:top]
        return {"request": request, "matched_categories": [], "matched_traits": [], "no_match": True,
                "picks": [{"voice": v, "score": 0, "reasons": []} for v in picks], "skip": []}

    ranked = sorted(catalog["voices"], key=lambda v: (-score_voice(v, cats, traits), featured_rank(v), v["short_name"]))
    picks = []
    for v in ranked[:top]:
        reasons = [f"{catalog['categories'][c]['label']}: {FIT_LABEL[v['fit'][c]]}" for c in cats]
        reasons += [f"{t} tone" for t in traits if t in v["traits"]]
        picks.append({"voice": v, "score": score_voice(v, cats, traits), "reasons": reasons})
    skip = []
    if cats:
        primary = cats[0]
        skip = [v for v in catalog["voices"] if v["fit"][primary] == 0 and v not in [p["voice"] for p in picks]]
        skip = sorted(skip, key=featured_rank)[:3]
    return {"request": request, "matched_categories": cats, "matched_traits": traits, "no_match": False,
            "picks": picks, "skip": skip}


# ---------------------------------------------------------------- output

def voice_public(v: dict) -> dict:
    keys = ["short_name", "name", "voice_id", "collection", "language", "delivery", "listening_note", "pitch",
            "best_for", "tradeoff", "preview_url", "sample_duration", "page_url", "share_url"]
    return {k: v[k] for k in keys}


def print_voice_card(v: dict, index: int | None = None, reasons: list[str] | None = None) -> None:
    head = f"{index}. " if index is not None else ""
    print(f"{head}{v['short_name']}  ({v['voice_id']})")
    pad = "   " if index is not None else ""
    print(f"{pad}{v['pitch']}")
    if reasons:
        print(f"{pad}Why: {'; '.join(reasons)}")
    print(f"{pad}Fit note: {v['tradeoff']}")
    print(f"{pad}Preview ({fmt_duration(v['sample_duration'])}, existing sample): {v['preview_url']}")
    print(f"{pad}Listen for: {v['listening_note']}")


def cmd_recommend(args, catalog) -> int:
    result = recommend(catalog, args.request, args.top)
    if args.json:
        out = dict(result)
        out["picks"] = [{"score": p["score"], "reasons": p["reasons"], **voice_public(p["voice"])} for p in result["picks"]]
        out["skip"] = [v["short_name"] for v in result["skip"]]
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    print(f'Use case: "{args.request}"')
    if result["no_match"]:
        print("No format or tone words matched. Showing the featured voices instead.")
        print("Add the format (Short, explainer, documentary, trailer, onboarding...) for a sharper shortlist.\n")
    else:
        labels = [catalog["categories"][c]["label"] for c in result["matched_categories"]]
        bits = []
        if labels:
            bits.append("format: " + ", ".join(labels))
        if result["matched_traits"]:
            bits.append("tone: " + ", ".join(result["matched_traits"]))
        print("Matched " + " | ".join(bits) + "\n")
    for i, p in enumerate(result["picks"], 1):
        print_voice_card(p["voice"], i, p["reasons"])
        print()
    if result["skip"]:
        primary = catalog["categories"][result["matched_categories"][0]]["label"]
        print(f"Wrong fit for {primary.lower()}: " + ", ".join(v["short_name"] for v in result["skip"]))
        print()
    print("Next: play the previews, pick one, then run `voices.py show <name>` for its voice ID and share link.")
    return 0


def cmd_show(args, catalog) -> int:
    v = find_voice(catalog, args.voice)
    if args.json:
        print(json.dumps(voice_public(v), indent=2, ensure_ascii=False))
        return 0
    print_voice_card(v)
    print(f"Best for: {', '.join(v['best_for'])}")
    print(f"Language (source metadata): {v['language']}  |  Delivery: {v['delivery']}  |  Collection: {v['collection']}")
    print(f"Voice ID: {v['voice_id']}")
    print(f"ElevenLabs share link (sign-in required): {v['share_url']}")
    print(f"Voice page: {v['page_url']}")
    print("\nTo use it: open the share link while signed in to ElevenLabs and add the voice to My Voices.")
    print("Then pick it in the ElevenLabs app, or call the API with the voice ID above.")
    return 0


def cmd_list(args, catalog) -> int:
    voices = catalog["voices"]
    if args.category:
        if args.category not in catalog["categories"]:
            raise ToolError(f"Unknown category '{args.category}'. Try: {', '.join(catalog['categories'])}")
        voices = sorted((v for v in voices if v["fit"][args.category] >= 2), key=lambda v: -v["fit"][args.category])
    if args.json:
        print(json.dumps([voice_public(v) for v in voices], indent=2, ensure_ascii=False))
        return 0
    for v in voices:
        print(f"{v['short_name']:<11} {v['voice_id']}  {v['collection']:<10} {', '.join(v['best_for'])}")
    return 0


def cmd_categories(args, catalog) -> int:
    for key, spec in catalog["categories"].items():
        print(f"{key:<14} {spec['label']}  (e.g. {', '.join(spec['keywords'][:4])})")
    return 0


def _fetch(url: str, timeout: float, method: str = "GET", headers: dict | None = None):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT, **(headers or {})})
    return urllib.request.urlopen(req, timeout=timeout)


def cmd_audition(args, catalog) -> int:
    v = find_voice(catalog, args.voice)
    print(f"{v['short_name']}: existing preview sample, {fmt_duration(v['sample_duration'])}. Listen for: {v['listening_note']}")
    print(v["preview_url"])
    if args.download:
        target_dir = Path(args.download).expanduser()
        if target_dir.exists() and not target_dir.is_dir():
            raise ToolError(f"{target_dir} exists and is not a folder.")
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{_norm(v['short_name']).replace(' ', '-')}_preview.mp3"
        if target.exists() and not args.force:
            raise ToolError(f"{target} already exists. Use --force to replace it.")
        try:
            with _fetch(v["preview_url"], args.timeout) as resp:
                ctype = resp.headers.get("Content-Type", "")
                if not ctype.startswith("audio/"):
                    raise ToolError(f"Expected audio from {v['preview_url']}, got '{ctype}'. Nothing saved.")
                data = resp.read(MAX_PREVIEW_BYTES + 1)
        except urllib.error.HTTPError as e:
            raise ToolError(f"Preview server returned HTTP {e.code}. Nothing saved. Try the link in a browser.")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            reason = getattr(e, "reason", e)
            raise ToolError(f"Could not reach the preview server ({reason}). Nothing saved.")
        if len(data) > MAX_PREVIEW_BYTES:
            raise ToolError("Preview was larger than expected. Nothing saved.")
        fd, tmp = tempfile.mkstemp(dir=target_dir, suffix=".part")
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, target)
        print(f"Saved the existing preview sample to {target} ({len(data)} bytes). This is not newly generated audio.")
    if args.open:
        webbrowser.open(v["preview_url"])
        print("Opened the preview in your browser.")
    return 0


def cmd_check_links(args, catalog) -> int:
    failures = 0
    for v in catalog["voices"]:
        for label, url in (("preview", v["preview_url"]), ("page", v["page_url"])):
            try:
                with _fetch(url, args.timeout, method="HEAD") as resp:
                    status = resp.status
            except urllib.error.HTTPError as e:
                status = e.code
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                status = f"unreachable ({getattr(e, 'reason', e)})"
            ok = status == 200
            failures += 0 if ok else 1
            print(f"{'OK  ' if ok else 'FAIL'} {v['short_name']:<11} {label:<8} {status}  {url}")
    print("ElevenLabs share links need a signed-in browser, so they are not checked here.")
    print("All public links reachable." if not failures else f"{failures} link(s) failed.")
    return 0 if not failures else 1


def cmd_showcase(args, catalog) -> int:
    out = Path(args.out).expanduser()
    if out.suffix.lower() != ".html":
        raise ToolError("--out must end in .html")
    if out.exists() and not args.force:
        raise ToolError(f"{out} already exists. Use --force to replace it.")
    if not out.parent.is_dir():
        raise ToolError(f"Folder {out.parent} does not exist.")
    html = render_showcase(catalog)
    out.write_text(html, encoding="utf-8")
    print(f"Wrote the audition page to {out}. Previews stream from {catalog['preview_origin']}.")
    if args.open:
        webbrowser.open(out.resolve().as_uri())
    return 0


def render_showcase(catalog: dict) -> str:
    template = SHOWCASE_TEMPLATE.read_text(encoding="utf-8")
    marker = "/*__CATALOG__*/null"
    if marker not in template:
        raise ToolError("Showcase template is missing its data marker.")
    data = json.dumps(catalog, ensure_ascii=False).replace("</", "<\\/")
    return template.replace(marker, data)


# ---------------------------------------------------------------- cli

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="voices.py", description="Prestige Voices catalog and audition tool (no API key needed).")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("recommend", help="shortlist voices for a use case")
    r.add_argument("request", help='what you are making, e.g. "6-minute documentary about the Dust Bowl"')
    r.add_argument("--top", type=int, default=3, choices=range(1, 16), metavar="N")
    r.add_argument("--json", action="store_true")

    s = sub.add_parser("show", help="full details, voice ID and share link for one voice")
    s.add_argument("voice")
    s.add_argument("--json", action="store_true")

    l = sub.add_parser("list", help="list all voices, optionally by category")
    l.add_argument("--category")
    l.add_argument("--json", action="store_true")

    sub.add_parser("categories", help="list the use-case categories")

    a = sub.add_parser("audition", help="print, open or save the existing preview sample")
    a.add_argument("voice")
    a.add_argument("--open", action="store_true", help="open the preview in your browser")
    a.add_argument("--download", metavar="DIR", help="save the existing preview mp3 into DIR")
    a.add_argument("--force", action="store_true", help="replace an existing file")
    a.add_argument("--timeout", type=float, default=20)

    c = sub.add_parser("check-links", help="check that every public preview and page responds")
    c.add_argument("--timeout", type=float, default=10)

    w = sub.add_parser("showcase", help="write a self-contained audition page")
    w.add_argument("--out", required=True)
    w.add_argument("--open", action="store_true")
    w.add_argument("--force", action="store_true")
    return p


COMMANDS = {"recommend": cmd_recommend, "show": cmd_show, "list": cmd_list, "categories": cmd_categories,
            "audition": cmd_audition, "check-links": cmd_check_links, "showcase": cmd_showcase}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.cmd](args, load_catalog())
    except ToolError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
