# Using a Prestige voice in ElevenLabs

Read this when the user is ready to generate audio, asks about access or cost, or hits an error.

## Before anything generates

Things that decide whether generation works, in the order people usually hit them:

1. **An ElevenLabs account.** The share link only works when signed in.
2. **The voice in My Voices.** Open the voice's share link (from `voices.py show <name>`) and add it to the library.
3. **Plan.** ElevenLabs says Voice Library voices are not available through the API on the free tier. In the ElevenLabs app, availability depends on the user's plan.
4. **Credits.** Every generation uses the user's own character credits.
5. **Model.** The API default is `eleven_multilingual_v2`. If a request is rejected and the error mentions the model, retry with that one.
6. **The voice owner's sharing settings.** Shared voices can be changed or withdrawn by their owner. If a voice disappears from the share link, it can't be used, and nothing in this plugin can restore it.

## Generating in the ElevenLabs app

Easiest path for most people. Open Text to Speech, choose the voice from My Voices, paste the script, generate. No key or code needed.

## Optional: generate from here with `tts.py`

`scripts/tts.py` calls the official ElevenLabs API with the selected voice ID. It reads the key from the `ELEVENLABS_API_KEY` environment variable in the user's own shell. Tell the user to set it themselves. Never ask them to paste the key into the conversation, and never print it.

Use `python` instead of `python3` on Windows. Give `--text-file` and `--out` as full paths, or run from the folder that holds the script.

Check access first. This is free and generates nothing:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" check --voice Dexter
```

Generating is billable. Show the dry run first. It exits 0, prints the voice, model, character count and output path, and sends nothing:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" speak --voice Dexter --text-file /path/to/script.txt --out /path/to/dexter-take1.mp3
```

Only after the user explicitly agrees to spend credits, add `--confirm-billable`. That run asks for permission every time, by design. Optional flags: `--model`, `--format` (default `mp3_44100_128`), `--speed` (0.7 to 1.2), `--stability`, `--similarity`, `--style`, `--force` to replace an existing file.

The helper refuses to overwrite files without `--force`, writes only to a folder that already exists, and saves nothing unless ElevenLabs returns audio.

## When it fails

The helper explains each failure and stops. It never tries a different voice. Pass that on and help with the specific fix:

| What it says | What to do |
|---|---|
| `ELEVENLABS_API_KEY is not set` | User sets the variable in their shell, then retries. |
| Rejected the API key (401) | Key is wrong, revoked, or lacks text-to-speech permission. |
| Can't use the voice yet (400/403/404) | Add the voice from its share link. Check that the plan allows Voice Library voices through the API. |
| Out of credits, or plan/billing | Their account needs credits or an upgrade. Nothing was generated. |
| Rejected the request (422) | Usually the model or a setting. Retry with `--model eleven_multilingual_v2` and default settings. |
| Rate limiting (429) | Wait and retry. |
| Could not reach ElevenLabs ... No request was processed | Network problem before anything was sent. Safe to retry once it's fixed. |
| Unknown whether ElevenLabs generated audio or charged credits | The connection dropped after the request went out. Don't rerun until the user checks their ElevenLabs history and usage, because a rerun could charge twice. |
| Answered with a redirect | The helper refused to follow it, so the key went nowhere else. Try later. Don't work around it. |
| Didn't return the voice, so access isn't confirmed | The account check came back for a different voice. Treat access as unproven and add the voice from its share link. |

Never describe the preview samples as generated output. Only a successful `speak` run with `--confirm-billable` produces new audio.
