---
name: ai-promo-video
description: Builds a 30s animated promo video (16:9 and 9:16 MP4 with music) for Abhilash's AI products in the Live Chat Agent style. Modes are chat (Live Chat Agent), inbound call (Call Eva) and outbound call (Eva calls the customer). Use when asked for a promo, explainer or social video, an animation like the Live Chat Agent / Call Eva video, or a video from dashboard numbers for LinkedIn or Reels.
---

# AI promo video

You turn a product concept, real dashboard numbers and a sample conversation into a finished 30s video. The visual system is fixed: a light pastel background, Inter Display Black headlines, purple, green and magenta gradient numbers, and an orange CTA. You fill in a `concept.json`, check stills, then render.

## What's here
- `template/promo.html`: one data-driven template with 5 scenes, used for both formats. Don't change the scene timings (`T` in the script) because the music is synced to them.
- `template/assets/`: `eva-phone.png` (Eva on a phone) and `lca-logo.png`.
- `scripts/render.js`: `--config x.json --format landscape|vertical`, plus `--stills dir [t...]` or `--out file.mp4`.
- `scripts/music.py --style upbeat|lofi out.wav`: original music generated in code, so there's no licence issue.
- `scripts/build.sh concept.json out_dir [landscape] [vertical]`: renders, adds music, sets loudness to -14 LUFS and writes a contact sheet.
- `examples/call-eva-inbound.json`: the delivered Call Eva video. `examples/lca-chat.json`: chat mode. Start a new concept by copying the closest one.

Needs Playwright with Chromium, ffmpeg, Python with numpy, and the Inter and Inter Display fonts. Claude Code cloud sessions have all of these. If the fonts are missing, install them with `apt-get install fonts-inter` before rendering.

## The 5 scenes (30s)
| Time | Scene | Config |
|---|---|---|
| 0-4.4s | Hook: a big number counts up, then a line and an accent line | `hook.value/prefix/suffix/line/accent` |
| 4.3-9.3s | Problem: a big word, up to 9 floating cards, red tags and a pill subtitle | `problem.word/subtitle/tag/cards` |
| 9.2-19.6s | Demo: the conversation with up to 4 checkmark chips and a result line | `mode`, `demo.*` |
| 19.4-25.6s | Results: 3 stage labels, a moving card and 3 count-up stat cards | `results.*` |
| 25.5-30s | Close: logo, 2 tagline lines (plain + accent), URL pill and CTA button | `close.*` |

Demo modes:
- `chat`: a chat widget only, with no phone, timer or waveform.
- `inbound`: Eva's phone, a live call transcript, a timer and a waveform.
- `outbound`: the same layout, but it opens with a "Calling Sasha..." dialling overlay (`demo.dialing`, `dialingSub`, `dialingPill`) and then switches to `livePill`.

`demo.lines` are `[who, text, stampSeconds]`, where `who` is `agent` or `user`. The stamp drives the call timer and is optional in chat mode. Lines are spaced out automatically. 5 to 9 lines works well. Keep each line under about 70 characters. `demo.chips` are `[title, sub, lineIndex]`, and a chip appears just after that line does. `music` can be one style for both formats or `{ "landscape": ..., "vertical": ... }`. The default is upbeat for 16:9 and lofi for 9:16.

## Workflow
1. **Collect** the mode, the source numbers (a dashboard paste or screenshot), a sample conversation, and any new images (`phoneImage` and `logoImage` in the config, relative to the config file). Use AskUserQuestion for only the things that change the result. Usually that's whether to remove the client's name, which formats to make, and the hook angle.
2. **Pick numbers.** This is the part that needs judgement:
   - Show only numbers that are clear and work for Eva or the product: volume handled, routed or transferred, leads captured, after-hours coverage, speed.
   - Never show failures, unanswered or no-answer counts, unclassified buckets or billed minutes in a prospect video.
   - Check the source adds up (does each part sum to its total, is any department or bucket blank, does the header match the table?). Flag any mismatch to the user in plain words, and use the safer figure.
   - Remove the client's name by default ("one multi-brand dealer group"). Keep caller first names generic (Sasha).
   - Don't invent statistics. Industry stats need a source the user approves.
3. **Write** `concept.json` in the scratchpad, or in the repo if the user wants to keep it.
4. **Check stills** for both formats: `node scripts/render.js --config c.json --format landscape --stills dir`, the same with `vertical`, then tile them with ffmpeg and look. Check for text overflow, cards covering text, chips that fit, no client name, and numbers that match the source. In 9:16, keep key content between y 220 and 1600 (the Reels and LinkedIn safe zone).
5. **Build:** run `scripts/build.sh c.json out_dir` in the background. It takes about 15 min per format. Look at the `_sheet.png` contact sheets, check with ffprobe (30s, 1920x1080 or 1080x1920), then send the MP4s with SendUserFile.
6. **Report:** list the numbers you used and the ones you left out (and why), plus any source inconsistencies. Remind the user the music is generated in code and that Claude can't hear it, so they should play it before posting.

## Limits
- The length is fixed at 30s and there are always 5 scenes. Changing the timings means editing `T` in the template and the scene marks in both music scripts together.
- Up to 9 problem cards, 4 chips and 3 stats. Extra items are ignored.
- Long hook lines or close lines can wrap or overflow, so shorten them and re-check the stills.
