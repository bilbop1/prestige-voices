# Writing a script for the chosen voice

Read this after the user has picked a voice.

## Length

Most speakers land between 140 and 170 words a minute. Use the voice's pace:

| Pace | Voices | Words per minute to plan for |
|---|---|---|
| Quick | Jett, Pulse, Bilbop, Snap, Reel, Felix | about 170 |
| Medium | Titan, Derek, Dexter, Titan Epic, Havoc, Reverend | about 150 |
| Unhurried | Heisenberg, Timber, Drift | about 130 |

A 60-second Short with Jett is roughly 170 words. A 60-second sleep intro with Drift is closer to 120, because the pauses matter. For screen walkthroughs, onboarding and tutorials, plan about 20 percent fewer words so the viewer has silent beats to watch each click. These are planning numbers. The real timing comes from the first generated take.

## Details you don't have

Never invent product facts and pass them off as real. For a UI walkthrough, use the user's actual menu and button names if they gave them. If they didn't, write the steps with bracketed placeholders, like "Open [Settings], then [Integrations]", and list the placeholders under the script for them to confirm. Do the same for names, prices and dates.

## Sounding like a person

Write for the ear. Read every line as if you were saying it to one listener.

- Vary sentence length on purpose. A short line after a long one gives the voice somewhere to land.
- Use the user's specifics: the product name, the place, the date, the number. Specific nouns carry a read better than adjectives.
- Cut stock phrases ("in today's world", "let's dive in", "game-changer", "unlock"). They sound read, not spoken.
- Use contractions unless the voice's register is formal (Derek on a bulletin, Reverend in a sermon).
- One idea per sentence for support and onboarding. People are following along with their hands.
- Spell out what should be spoken: "twenty twenty-six", "three point five percent", "S-K-U". Numbers, dates, currencies and acronyms are where reads go wrong.

## Matching the voice

- **Hook voices (Snap, Bilbop, Pulse):** put the payoff in the first sentence. If the script needs a slower middle, say so and suggest a calmer voice for the rest instead of stretching the hook voice.
- **Narrative voices (Titan, Heisenberg, Timber):** give them room. Paragraph breaks and full stops do more than exclamation marks.
- **Performance voices (Titan Epic, Felix, Reverend, Havoc):** the script has to justify the size. Write stakes, conflict or conviction into the words. Don't write neutral copy and expect the voice to supply drama.
- **Drift:** short lines, soft consonants, and space. Leave out urgency, prices and calls to action.
- **Dexter and Derek:** lead with the action or the fact. Put names and numbers where they can be heard clearly, not buried mid-clause.

## Pauses and pronunciation in ElevenLabs

These depend on the model the user generates with. In the ElevenLabs app, the model is whatever is selected in Text to Speech, so ask them to check it before relying on tags. When unsure, leave tags out and use punctuation.

- `eleven_multilingual_v2` (the API default, and what `tts.py` uses unless told otherwise) accepts `<break time="1.0s" />` for pauses up to 3 seconds.
- Eleven v3 and v4 don't support break tags. Use ellipses, dashes and sentence structure for pacing.
- For a word that keeps coming out wrong, respell it phonetically in the script ("Worcester" as "Wuss-ter"), or use a pronunciation dictionary in ElevenLabs.

## Hand over

Give the script as plain text the user can paste straight into ElevenLabs, then one line on the estimated length. Offer one alternate opening line if the first sentence is doing heavy lifting.
