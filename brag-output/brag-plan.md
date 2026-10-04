# Prestige Voices: launch video plan

Dispatch: /brag on Opus 5.5 runs brag-slim. Input: this project directory. Format: landscape 1920x1080, 30 fps, 21 s.

## What it is, for a stranger
A premier collection of fifteen distinct ElevenLabs voices, with a Claude plugin that casts the right one for your project. You say what you're making, get a tailored shortlist, hear the real preview samples, and leave with a script and the exact voice ID.

- **Who it's for:** creators, marketers and product teams who need a voiceover and don't want to scroll a voice library.
- **What sets it apart:** broad creative coverage (Shorts, explainers, documentary, story, trailers, support, atmosphere), and each pick is matched to your project rather than a generic list.
- **Most impressive true claim:** ask about an onboarding video and you get the steady instruction voice. Ask about a TikTok and you get the fast one. Every pick comes with a real preview you can hear.
- **Visual hook:** the product's own serif headline, "Premier voices. Make it sound exceptional.", set in ink and gold.
- **Share caption:** see share-copy.txt.

## Angle
Show the product working. A request goes in, a real shortlist comes out, a real preview plays, and you leave with an ID. No invented numbers, testimonials or generated results. The UI is the showcase page from this repo, restyled only for the 1920x1080 frame. Every voice name, pick, reason, tradeoff, voice ID and script line comes from actual tool output or the forward-test skill run.

## Tone
Polished. Restrained, elegant, a few long holds, soft dips through the background between scenes.

## Visual identity (from showcase.html)
Ink #0e0d0b, surface #171512 / #211e19, text #f3ede2, muted #a89f90, gold #d9a54a, good #7cc49b, warn #e3a170. Instrument Serif (display, gold italic accent) and Inter (UI), with a mono face for the voice ID. Rounded 16 px cards with a gold ring on the top pick.

## Sound
An original soft bed in D major written for this video: a warm Dmaj7 / Bm7 / Gmaj7 / A pad, a gentle bell on the hook and the outro, quiet key ticks while the request types, and a low air swell on scene changes. Everything sits in the same key and space. The bed ducks under the two real preview excerpts, Dexter (0.00 to 2.55 s, his first full phrase) and Jett (0.00 to 1.83 s, his first full phrase). Both are cut at natural silences found with silencedetect.

## Storyboard (sums to 21.0 s)

| # | Time | Scene | On screen | Audio |
|---|---|---|---|---|
| 1 | 0.0 to 3.0 | Hook | Eyebrow "PRESTIGE VOICES". "Premier voices." rises in, then gold italic "Make it sound exceptional." | Bell, pad enters |
| 2 | 3.0 to 5.8 | Request | The "What are you making?" box. The request types in: "45-second onboarding video for a dental SaaS. Calm, not salesy." | Soft key ticks |
| 3 | 5.8 to 10.8 | Shortlist and audition | "Matched Support and onboarding · calm tone". Three cards stagger in: Dexter (Top pick, gold ring), Heisenberg, Derek, each with its real reason and best-for tags (fit notes stay collapsed, as on the page). Dexter's play button presses and its progress bar runs. Caption: "Real preview. Hear it before you spend a credit." | Dexter preview phrase, bed ducked |
| 4 | 10.8 to 14.8 | Range | "Different job, different voice." Three request → pick rows land one by one: TikTok explainer → Jett, sci-fi trailer → Titan Epic, sleep story → Drift. The Jett row plays. | Jett preview phrase |
| 5 | 14.8 to 18.0 | Hand-off | Dexter selected. The opening lines of the script from the skill run, "Voice ID Smxkoz0xiOoHo5WcSskf", and a "Copy voice ID" press, then the toast "Dexter voice ID copied". | Soft click |
| 6 | 18.0 to 21.0 | Outro | Icon, "Prestige Voices", the install command, and the GitHub path | Bell resolves |

Highlights: (1) a real shortlist tailored to the job, (2) real preview audio, (3) exact voice ID and script you can paste.
Punchline: the install line.

## Rights note
The preview excerpts are the collection's own public samples from voicefieldguide.com. They're used here to demonstrate the product, and the parent confirms that use before posting. The music and effects were synthesized for this video from scratch.

## Delivery
- brag.mp4 is a release asset and isn't committed (gitignored). brag.jpg is the strongest settled frame and is baked in as frame 0. share-copy.txt holds the post.
- work/ holds the HyperFrames project, fonts, audio stems and stills, and is gitignored.
