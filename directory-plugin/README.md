# Prestige Voices

**Premier voices. Make it sound exceptional.**

A premier collection of fifteen distinct English ElevenLabs voices for short videos, explainers, documentaries, stories, trailers, support and atmosphere. Describe the job, get a tailored shortlist, hear the real audition samples, and receive a natural script with the exact voice ID and ElevenLabs share link.

## Install and use

```text
/plugin marketplace add bilbop1/prestige-voices
/plugin install prestige-voices@prestige-voices-marketplace
```

Start a new Claude session after installing. Try:

```text
/prestige-voices Write a 45-second calm onboarding script for a dentist scheduling app. Choose the voice for me.
/prestige-voices Cast a dramatic narrator for a sci-fi trailer and write a 30-second script.
/prestige-voices Choose a gentle voice for a sleep-story opening and write one minute of narration.
```

The skill reads the bundled catalog and scripting guide. It produces a shortlist with real preview links, then a script and exact ID. Play previews or open the share link in your browser. To generate audio, add the voice to My Voices and use ElevenLabs Text to Speech separately. Your ElevenLabs plan, credits and sharing availability govern access; API use of Voice Library voices needs a paid plan.

This installable folder has no executable helpers, API-key handling, hooks, MCP servers or audio generation. Optional standalone Python utilities and the audition board are available separately in the parent repository; the plugin does not invoke them. Claude handles drafting through your own Claude account. Public websites receive ordinary browser requests only when you open their links. See [PRIVACY.md](PRIVACY.md).

Code and text: MIT. Voice models and preview audio remain subject to ElevenLabs and their respective rights; see [NOTICE.md](NOTICE.md). No endorsement by ElevenLabs or Anthropic is claimed. Support: https://github.com/bilbop1/prestige-voices/issues.
