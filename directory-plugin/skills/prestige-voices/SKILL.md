---
name: prestige-voices
description: 'Cast a premier ElevenLabs voice from the Prestige Voices collection, link its real audition sample, write a natural script for the chosen voice and give the exact voice ID and share link. Use for voiceovers, Shorts, Reels, documentaries, explainers, stories, trailers, onboarding, support, ads and calm reads; or when someone asks which Prestige voice to use. Covers casting and script writing; users generate audio separately in ElevenLabs.'
allowed-tools: Read
---

# Prestige Voices

A premier collection of fifteen distinct English ElevenLabs voices for short videos, explainers, documentary, fiction, trailers, support, broadcast and atmosphere. Match the project to the performance that makes it sound exceptional, let the user audition it, and hand over a usable script and the exact voice ID.

The request: $ARGUMENTS

## Cast and audition

Read [references/voices.json](references/voices.json), the complete bundled public catalog. Do not execute code or retrieve remote instructions. All casting metadata, IDs and links are in this file.

Identify the format, approximate duration and tone from the request. Ask one concise question only if a missing detail prevents useful casting. Match the format to the catalog's categories and the tone to its traits. The per-voice `fit` values mean 0 = wrong fit, 1 = possible, 2 = good, 3 = first choice. Prioritize the primary format, then tone and any secondary formats. Read the actual listening notes and tradeoffs before choosing; a high fit score alone doesn't explain a performance.

Give two or three voices with a specific reason each suits this project, a brief fit note, and its exact `preview_url`. Call those existing audition samples, not audio made for this request. Tell the listener what to hear for using `listening_note`. Every public sample lasts 7 to 13 seconds. Opening or playing a link is the user's choice; the installed plugin makes no network requests itself.

## Script and hand off

When the user picks a voice, or delegates the choice, read [references/scripting.md](references/scripting.md) and write for that voice's pace and character. With delegated choice, say why the strongest voice beats the runner-up and proceed without another question. Use bracketed placeholders for product facts, button names, dates or prices that the user hasn't supplied. Size the script to the requested duration and leave headroom for screen actions in tutorials.

Give the selected voice's exact `voice_id` and `share_url` from the catalog, plus the plain-text script and estimated duration. Next step: open the share link signed in to ElevenLabs, add the voice to My Voices, and generate in ElevenLabs Text to Speech. The user's plan, credits and voice availability govern access. Voice Library API access needs a paid ElevenLabs plan.

## Boundaries

- Use only this bundled catalog; never invent voice IDs, samples, links, rankings, endorsement or performance results.
- Source metadata lists English for all fifteen voices. Other languages are untested; recommend auditioning a line rather than promising support.
- This plugin performs casting and script writing. It has no audio generation capability, authentication, API-key handling, hooks, MCP servers or executable helpers. Never ask for credentials or spend credits.
- Use the details in the user's current request. Do not extract memory, chat history or uploaded files.
- Keep useful comparisons concise. Do not imply that all tasks fit every voice.
