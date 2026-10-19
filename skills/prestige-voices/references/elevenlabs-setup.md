# Using a Prestige voice in ElevenLabs

Read this when the user wants to add a voice, generate audio, asks about cost, or hits an access error.

## Account and access

The user needs an ElevenLabs account with the chosen voice in My Voices. Give the share link from `voices.py show <name>` so they can add it while signed in. Voice Library voices need a paid ElevenLabs plan for API use. Generating speech uses that account's credits, and sharing availability can change if the voice owner withdraws it.

The optional helper reads `ELEVENLABS_API_KEY` from the user's environment. They set it in their own shell. Never request a key in chat or print it. Use `python` on Windows if `python3` is unavailable. Resolve `${CLAUDE_SKILL_DIR}` to the installed skill directory when the agent has not filled it in.

## Add the chosen voice

Offer the share link or the helper. Without `--confirm`, this command is a local dry run and needs no key:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" add Dexter
```

After the user's explicit yes to adding Dexter, append `--confirm`. The helper obtains the public owner ID from the catalog share link and calls ElevenLabs' [Add shared voice endpoint](https://elevenlabs.io/docs/api-reference/voices/voice-library/share) with the catalog name. It prints the returned voice ID and generates no speech. If the result is unreadable or the connection drops, check My Voices before trying again.

## Generate in the app

Open Text to Speech, choose the voice from My Voices, paste the script and generate. No API key is needed for this path. The selected model and the user's plan determine which settings are available.

## Generate with the helper

Check access without generating speech:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" check --voice Dexter
```

Show the dry run first. Give full paths to the script and output, using an existing output directory:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" speak --voice Dexter --text-file /path/to/script.txt --out /path/to/dexter-take1.mp3
```

The dry run prints the voice, model, character count and destination. After the user's explicit approval covers the credit spend, append `--confirm-billable`. Existing approval for that exact render is sufficient; do not ask for the same approval again.

The helper starts on `eleven_v4`. If ElevenLabs rejects that model with HTTP 422 and a model-specific error status, it announces one attempt on `eleven_multilingual_v2`, the [API reference default](https://elevenlabs.io/docs/api-reference/text-to-speech/convert). The voice and script stay the same. Include that fallback when describing the proposed render. A user requiring v4 only can use the app path. Arbitrary validation errors do not trigger a fallback.

Use `--model` for another explicitly chosen model and `--format` for its output format. Settings flags are model-dependent; do not promise that v4 supports every slider. The default output is `mp3_44100_128`. The helper refuses to overwrite a file without `--force` and saves only a complete audio response. Report the actual output model and path.

## Failed requests

Resolve the reported problem before another request. The helper never changes the selected voice.

| Result | Next step |
|---|---|
| Missing or rejected key | The user sets or corrects their local environment variable and its permissions. |
| Voice unavailable or denied | Open its share link, add it to My Voices, and check plan access. |
| Credits or billing rejected | The user checks their account's credits and plan. |
| Model or settings rejected | Read the exact error. Only the model-specific v4 HTTP 422 path has an automatic fallback. |
| Rate limiting | Wait for the limit to clear; there is no automatic retry. |
| Connection refused or DNS failure before sending | Fix connectivity, then make a new request with the existing applicable approval. |
| Unknown add outcome | Check My Voices before another add attempt. |
| Unknown generation or charge outcome | Check ElevenLabs history and usage before another billable request. A truncated download is also an unknown outcome. |
| Redirect | The helper refuses to forward the key. Keep using the official API rather than following the redirect. |
| Check returns another voice | Treat access as unconfirmed and verify the selected voice in My Voices. |

Fixed preview samples are auditions. Describe new audio as generated only after a successful confirmed `speak` run.
