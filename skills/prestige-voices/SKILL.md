---
name: prestige-voices
description: 'Pick the right ElevenLabs voice from the Prestige Voices collection for a specific job, audition its real preview, write a natural script for it, and get the exact voice ID, share link and next step. Use when someone wants a narrator or voiceover for a Short, Reel, explainer, documentary, story, trailer, onboarding or support video, broadcast-style update, ad, or calm/ASMR read; asks "which voice should I use", "find me a narrator", or "write a voiceover script"; or names Prestige Voices. Not for cloning a new voice or choosing voices outside this collection.'
allowed-tools: Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/voices.py" *), Bash(python "${CLAUDE_SKILL_DIR}/scripts/voices.py" *), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/voices.py *), Bash(python ${CLAUDE_SKILL_DIR}/scripts/voices.py *), Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" check *), Bash(python "${CLAUDE_SKILL_DIR}/scripts/tts.py" check *)
---

# Prestige Voices

A premier collection of fifteen distinct English ElevenLabs voices that covers short video, explainers, documentary, fiction, trailers, support, broadcast and atmosphere. Each voice is strongest on particular material. Your job is to match the user's project to the voice that will make it sound exceptional, let them hear it, and hand them something they can use right away.

The request, if one was given: $ARGUMENTS

## Flow

1. **Get the job.** You need the format (Short, explainer, documentary, trailer, onboarding...), rough length, and the tone they want. If the request already says enough, don't interview them. Ask one short question only when the format is missing.

2. **Shortlist.** Run the catalog tool and use its ranking as the starting point, not the final word:

   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/voices.py" recommend "<their request in their words>"
   ```

   Use `python` instead of `python3` on Windows. If `${CLAUDE_SKILL_DIR}` was not filled in, the scripts are in this skill's `scripts/` folder. Add `--json` if you want structured output. Give the user 2 or 3 voices. For each one say why it fits *this* project and what the tradeoff is. Say plainly when a voice is a poor fit, too. The catalog marks those as "wrong fit".

3. **Audition.** Give each shortlisted voice's preview link. These are existing samples of 7 to 13 seconds, not audio made for this request, so call them previews. Tell the user what to listen for (the `Listen for` line). `voices.py audition <name> --open` opens one in their browser. `voices.py showcase --out <file>.html --open` writes a page where they can play every voice side by side.

4. **Select and script.** Once they pick, write the script for that voice. If they leave the choice to you, take the strongest fit and say in one line why it beat the runner-up. Follow [references/scripting.md](references/scripting.md). Keep it in their words and their subject, sized to their length at the voice's pace.

5. **Hand off.** Run `voices.py show <name>` and give them the voice ID, the ElevenLabs share link, and the next step: open the share link signed in to ElevenLabs, add the voice to My Voices, then generate in the ElevenLabs app or through the API. Mention that API use of Voice Library voices needs a paid ElevenLabs plan and that generation uses their credits. If they want to generate from here, ask about access or cost, or hit an error, read [references/elevenlabs-setup.md](references/elevenlabs-setup.md).

## Ground rules

- Use only voices in `references/voices.json`. Never invent a voice, a voice ID, a sample, or a link. If nothing fits well, say so and name the closest option with its tradeoff.
- Language: the source metadata lists English for every voice. Don't promise other languages. If asked, say it's untested and they should audition a line first.
- Don't claim ElevenLabs endorsement, ratings, usage numbers, or that a voice will make content perform.
- Generating new audio is optional, uses the user's own ElevenLabs account and credits, and only happens through `scripts/tts.py speak ... --confirm-billable` after the user explicitly says yes to spending credits. Never ask the user to paste an API key into the chat.
- If generation fails because their account can't use the voice, explain why and stop. Don't switch to a different voice on your own.
