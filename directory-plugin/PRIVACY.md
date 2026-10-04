# Privacy

Prestige Voices is a casting and script-writing skill. The installed plugin contains public voice metadata and written instructions. It has no backend, executable helpers, account system, analytics, telemetry, authentication or audio-generation capability.

Claude processes the request and drafts the response through the user's own Claude account, subject to Anthropic's [privacy policy](https://www.anthropic.com/legal/privacy) and that account's settings. A request or script may contain personal information supplied by the user; the plugin adds no recipient and retains no separate copy. It reads only the bundled public catalog, not memory, chat history or uploaded files.

The plugin provides public preview and share links. If the user chooses to open or play a preview, voicefieldguide.com receives an ordinary request, including the IP address, user agent and requested public file, subject to that website host's normal handling. No conversation or script is transmitted to that host by this plugin.

If the user opens an ElevenLabs share link or generates audio in ElevenLabs separately, ElevenLabs' [privacy policy](https://elevenlabs.io/privacy-policy) and account settings apply. The plugin does not send scripts, keys or other private data to ElevenLabs itself.

The repository also offers optional standalone Python utilities outside this installable folder. Those utilities are not installed or invoked by this plugin; their separate behavior is documented in the repository's root README and PRIVACY.md.

Support and privacy concerns: https://github.com/bilbop1/prestige-voices/issues.
