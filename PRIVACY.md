# Privacy

This policy covers the repository's audition board and optional standalone Python utilities. The installed Claude skill is scoped to casting and script writing; its separate policy is [directory-plugin/PRIVACY.md](directory-plugin/PRIVACY.md). The marketplace does not install or invoke these standalone utilities.

Prestige Voices has no backend, account system, analytics or telemetry of its own. It never sends your conversations, scripts or keys to the plugin author.

## What runs where

- **On your machine, offline:** the catalog, recommendations and voice lookups (`voices.py list`, `show`, `recommend`, `categories`, and writing the showcase page).
- **Through your Claude account:** when you use the skill, Claude drafts the shortlist explanation and your script. That conversation is handled by Anthropic under the terms and data settings of the Claude product you use. The plugin adds no other recipient.
- **Over the network, only when you ask:** the requests below.

| When | Where it goes | What is sent |
|---|---|---|
| You play a preview in the showcase page, or run `voices.py audition --download` or `check-links` | `voicefieldguide.com`, the public site that hosts the preview samples and voice pages | An ordinary web request for a public file. Like any website, that host sees your IP address, user agent and the file requested. |
| You open a voice's share link | `elevenlabs.io` | Your browser opens the ElevenLabs page, and ElevenLabs' own privacy policy applies. |
| You run `tts.py check` | `api.elevenlabs.io` | Your ElevenLabs API key and the voice ID. |
| You run `tts.py speak --confirm-billable` | `api.elevenlabs.io` | Your ElevenLabs API key, the voice ID, your script text, and the model and voice settings you chose. |

The showcase page carries its fonts inline. It makes no requests to font services or any third party other than the preview host when you press play.

## Your ElevenLabs API key

The optional generation helper reads the key from the `ELEVENLABS_API_KEY` environment variable that you set in your own shell. It sends the key only to `api.elevenlabs.io`, or to a server on your own machine when running the test suite. It refuses to follow redirects on requests that carry the key. It never prints, logs or saves the key, and it strips the key from any server error text before showing it. The skill tells Claude never to ask you to paste a key into a conversation.

Audio you generate is written only to the file path you choose. ElevenLabs handles your script text and the generated audio under its terms, privacy policy and your account settings.

## Contact

For questions or concerns, open an issue at https://github.com/bilbop1/prestige-voices/issues.
