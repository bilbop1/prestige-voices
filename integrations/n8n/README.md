Voice Field Guide narration for n8n

Find a voice for a reviewed script and make narration with your ElevenLabs account. The workflow suggests voices and links to their samples before any generation.

Download the JSON from https://raw.githubusercontent.com/bilbop1/prestige-voices/codex/release/integrations/n8n/voice-field-guide-narration.json . Open a new workflow in n8n. Choose Import from File in the workflow menu.

Install the verified @elevenlabs/n8n-nodes-elevenlabs integration if your instance does not have it. Open Edit your narration job and enter a brief and script. Leave generate set to false and run the workflow to see the shortlist. Listen to the samples, add your chosen voice to My Voices through its share link, and enter its exact name in selectedVoice.

To create audio, connect your own ElevenLabs credential in the generation node. Review your script. Set reviewedScript and generate to true, then run the workflow manually. Generation uses your own credits. Voice Library API access requires an eligible account. The workflow does not automatically retry or substitute voices. If a request times out, check your ElevenLabs history before trying again.

The workflow starts inactive. Your script stays in your n8n instance until you choose to generate; the generation request goes to ElevenLabs. Preview audio loads from voicefieldguide.com when played. See https://voicefieldguide.com for the full voice collection.
