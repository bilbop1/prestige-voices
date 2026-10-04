# Prestige Voices: launch video plan (as built)

Dispatch: /brag on Opus 5.5 runs brag-slim. Input: this project directory. Format: landscape 1920x1080, 30 fps, 22.0 s. Built with HyperFrames 0.8.124 (pinned).

## What it is, for a stranger
A premier collection of fifteen distinct ElevenLabs voices, plus a Claude plugin that casts the right one for your project. Say what you're making and you get a tailored shortlist. Then you hear the real preview samples and leave with a script and the exact voice ID.

- **Who it's for:** creators, marketers and product teams who need a voiceover without scrolling a voice library.
- **What sets it apart:** broad creative coverage (Shorts, explainers, documentary, story, trailers, support, atmosphere), with each pick matched to the project.
- **Most impressive true claim:** an onboarding video gets the steady instruction voice, and a TikTok explainer gets the fast one. Every pick comes with a real preview you can hear.
- **Visual hook:** the product's own serif headline, "Premier voices. Make it sound exceptional.", set in ink and gold.
- **Share caption:** see share-copy.txt.

## Angle
The video shows the product working. A request goes in, a real shortlist comes out, a real preview plays, and you leave with an ID. There are no invented numbers, testimonials or generated results. The UI is the showcase page from this repo, scaled for a 1920x1080 frame. Every voice name, pick, reason, tag, voice ID and script line comes from actual `voices.py recommend` output or the forward-test skill run. That includes the short row labels "TikTok explainer", "Sci-fi trailer" and "Sleep story", each of which returns the pick shown.

## Tone
Polished and restrained, with a few long holds and dips through the background between scenes.

## Visual identity (from showcase.html)
- **Colors:** ink #0e0d0b, surface #171512 / #211e19, text #f3ede2, muted #a89f90, gold #d9a54a, good #7cc49b.
- **Type:** Instrument Serif for display (gold italic accent), Inter for UI and JetBrains Mono for voice IDs. All are OFL and loaded from local files.
- **Shapes:** rounded cards, with a gold ring on the top pick.

## Sound
An original bed in D major synthesized for this video (work/audio/synth.py, seeded and deterministic):
- A Dmaj7, Bm7, Gmaj7, A, D pad with a soft 100 bpm arpeggio.
- Bells on the hook and outro, low-passed key ticks while the request types, clicks on presses, and air swells on scene changes.
- One shared reverb space for everything.

The bed ducks about 10 dB under the two real preview excerpts, Dexter (source 0.00 to 2.55 s) and Jett (source 0.00 to 1.83 s). Each is his first full phrase, cut at silences found with silencedetect. Master: −16 LUFS integrated, −1.5 dBTP.

## Storyboard (sums to 22.0 s)

| # | Time | Scene | On screen | Audio |
|---|---|---|---|---|
| 1 | 0.0 to 3.4 | Hook | Eyebrow "PRESTIGE VOICES · PREMIER ELEVENLABS COLLECTION". "Premier voices." then gold italic "Make it sound exceptional." | Bell, pad enters |
| 2 | 3.4 to 6.2 | Request | "What are you making?" The request types in: "45-second onboarding video for a dental SaaS. Calm, not salesy." The Shortlist button presses and the card glides up. | Key ticks, button click |
| 3 | 6.2 to 11.2 | Shortlist and audition | "Matched Support and onboarding · calm tone". Dexter (Top pick), Heisenberg and Derek arrive with real reasons, tags and voice IDs. Fit notes stay collapsed. Dexter plays, and the bar fills 2.55/7.78 of his sample. Caption: "Real preview. Hear it before you spend a credit." | Dexter's real phrase, bed ducked |
| 4 | 11.2 to 15.6 | Range | "Every kind of project. The right voice." TikTok explainer → Jett, Sci-fi trailer → Titan Epic, Sleep story → Drift. The Jett row plays, and the bar fills 1.83/10.48. | Jett's real phrase |
| 5 | 15.6 to 18.4 | Hand-off | "Your pick: Dexter" with the opening script lines from the skill run, Voice ID Smxkoz0xiOoHo5WcSskf, the "Copy voice ID" press and the toast "Dexter voice ID copied" | Click |
| 6 | 18.4 to 22.0 | Outro | Icon, "Prestige Voices", "Fifteen premier ElevenLabs voices, cast inside Claude.", and the two install commands | Bell resolves, fade |

Poster: the settled audition frame at 9.5 s (brag.jpg), baked in as frame 0.

## Rights note
The preview excerpts are the collection's public samples from voicefieldguide.com, used under the creator's authorization to demonstrate the audition step in this launch video. The music and effects were synthesized from scratch for this video. The repository's code license does not license the preview audio for re-hosting.

## Delivery
brag.mp4 is a release asset and is gitignored. brag.jpg is the poster. share-copy.txt holds the post. work/ holds the HyperFrames project, fonts, audio stems and stills, and is gitignored.
