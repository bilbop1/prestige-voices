---
name: prestige-voices
description: 'Cast a narrator from the fifteen Prestige Voices for video, podcasts, stories, ads, support or calm reads. Audition real previews, write a script, and provide voice IDs and share links. With their ElevenLabs key and approval, add the chosen voice and generate audio. Use for Prestige Voices, narrator recommendations or voiceover scripts; excludes voice cloning and voices outside this collection.'
allowed-tools: Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/voices.py" *), Bash(python "${CLAUDE_SKILL_DIR}/scripts/voices.py" *), Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/voices.py *), Bash(python ${CLAUDE_SKILL_DIR}/scripts/voices.py *), Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" check *), Bash(python "${CLAUDE_SKILL_DIR}/scripts/tts.py" check *), Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/tts.py" add *), Bash(python "${CLAUDE_SKILL_DIR}/scripts/tts.py" add *)
metadata:
  version: "1.1.0"
---

# Prestige Voices

Match the user's project to one of fifteen English ElevenLabs voices, let them hear its existing preview, and write for that voice's pace. The catalog is the source for voice facts and fit.

The request, if one was given: $ARGUMENTS

## Flow

1. **Get the job.** You need the format (Short, explainer, documentary, trailer, onboarding...), rough length, and the tone they want. If the request already says enough, don't interview them. Ask one short question only when the format is missing.

2. **Shortlist.** Run the catalog tool and use its ranking as the starting point, not the final word:

   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/voices.py" recommend "<their request in their words>"
   ```

   Use `python` instead of `python3` on Windows. If `${CLAUDE_SKILL_DIR}` was not filled in, the scripts are in this skill's `scripts/` folder. Add `--json` if you want structured output. The matcher scores keywords and can count excluded phrases such as "no sales pitch" as positive matches. Read the intent and catalog fit before choosing; use `voices.py list --json` or `show` when its top results miss the job. Give the user 2 or 3 fitting voices, or fewer if only one fits. For each one say why it fits *this* project and what the tradeoff is. Say plainly when a voice is a poor fit, too. The catalog marks those as "wrong fit".

3. **Audition.** Give each shortlisted voice's preview link. These are existing samples of 7 to 13 seconds, not audio made for this request, so call them previews. Tell the user what to listen for (the `Listen for` line). `voices.py audition <name> --open` opens one in their browser. `voices.py showcase --out <file>.html --open` writes a page where they can play every voice side by side.

4. **Select and script.** Once they pick, write the script for that voice. If they leave the choice to you, take the strongest fit and say in one line why it beat the runner-up. Follow [references/scripting.md](references/scripting.md). Keep it in their words and their subject, sized to their length at the voice's pace.

5. **Add or hand off.** Run `voices.py show <name>` and give the voice ID and share link. Offer to add that voice to the user's My Voices. With their explicit yes and their own `ELEVENLABS_API_KEY` set locally, run `tts.py add <name> --confirm`. Without that approval or key, give the share link so they can add it while signed in. Adding a voice changes their library; it generates no speech. Read [references/elevenlabs-setup.md](references/elevenlabs-setup.md) for access, cost or errors.

6. **Offer a render.** The user can paste the script into ElevenLabs or generate here. For local generation, show the `tts.py speak --voice <name> --text-file <path> --out <path>` dry run, including the model and character count. After their explicit yes to spending their own credits, add `--confirm-billable`. Eleven v4 is the helper default; a model-specific HTTP 422 allows its announced one-time fallback to `eleven_multilingual_v2` with the same voice. Include that fallback when requesting approval, and report the actual model and output file. If they require v4 only, offer the ElevenLabs app path.

## Ground rules

- Use only voices in `references/voices.json`. Never invent a voice, a voice ID, a sample, or a link. If nothing fits well, say so and name the closest option with its tradeoff.
- Language: the source metadata lists English for every voice. Don't promise other languages. If asked, say it's untested and they should audition a line first.
- Don't claim ElevenLabs endorsement, ratings, usage numbers, or that a voice will make content perform.
- Generating new audio is optional, uses the user's own ElevenLabs account and credits, and only happens through `scripts/tts.py speak ... --confirm-billable` after the user explicitly says yes to spending credits. Never ask the user to paste an API key into the chat.
- Adding a voice requires the user's explicit yes before `scripts/tts.py add ... --confirm`. Existing authorization for a selected voice does not authorize adding the entire catalog.
- If generation fails because their account can't use the voice, explain why and stop. Don't switch to a different voice on your own.
