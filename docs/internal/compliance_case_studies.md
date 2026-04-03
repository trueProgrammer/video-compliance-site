# Compliance Case Studies

This document consolidates the trickiest real-world cases we encountered while tuning the ANuvu compliance pipeline. The goal is to preserve the reasoning behind each tweak, highlight where the system failed, and capture the shape of the fix without overfitting to one title.

## How To Read This

Each case study covers:
- `Title / area`
- `What happened`
- `Why it was hard`
- `What we changed`
- `What to watch next`

The themes repeat across titles:
- transcript quality can be a bigger source of error than the classifier
- local scene context helps, but too much window context can create false positives
- visual overlap rules need to distinguish “same moment” from “same scene”
- GPT-style models need simpler policy language than long literal keyword lists

---

## 1. China Sensitivity: Concept Rules Beat Keyword Lists

**Title / area**
- `Brother Orange`
- China politics, maps, Tiananmen, Hong Kong, Taiwan, Dalai Lama

**What happened**
- The client workbook contained a very large China watchlist.
- Many examples were weak or clearly overbroad, such as generic Chinese signs, menus, flags, place names, or language references.
- At the same time, a few real high-value misses existed:
  - marked-up China/Taiwan/Tibet/Mongolia maps
  - Tiananmen / Mao late visuals
  - censorship / jail / internet dialogue

**Why it was hard**
- A literal prompt blacklist on words like `China`, `Chinese`, `Beijing`, `Hong Kong`, `Mandarin` would explode false positives.
- GPT models are good at policy meaning, but not good deterministic keyword engines for giant mixed political watchlists.
- China-sensitive map cases often require not just “it is a map” but “it is a politically sensitive map.”

**What we changed**
- Reframed China handling as:
  - watchlist terms are cues only
  - flag only explicit political/red-line meaning
  - no generic trigger on country/language/place references
- Expanded `AA11` and `AV19` only for the main red-line concepts, not the full list.

**What to watch next**
- Tiny/brief text and maps remain a recall risk.
- If a customer ever wants literal keyword enforcement, that should be a separate transcript/OCR rule layer, not prompt stuffing.

---

## 2. Audio Context Windows: Bigger Is Not Always Better

**Title / area**
- `Brother Orange`
- China jail / censorship dialogue around `01:15`

**What happened**
- The transcript clearly contained the meaning:
  - “we’re dealing with China”
  - “someone could go to jail”
  - “for posting something on the internet”
- But the audio classifier missed it.

**Why it was hard**
- The meaning was split across adjacent windows.
- One window had `China` context.
- The next had the `jail / internet / fear` meaning.
- The prompt was deliberately conservative and required explicit evidence inside the same analyzed unit.

**What we learned**
- Short windows can split political meaning.
- But simply making windows huge is not always better; more context can also dilute local signals and increase false positives.

**What we changed**
- We experimented with larger windows for audio classification.
- Later testing showed that for some titles, window length was not the main problem; prompt scope and transcript packing mattered more.

**What to watch next**
- For language compliance, window tuning and text packing should be tested together.
- The right unit is not “largest possible,” but “enough context without turning one line into the vibe of the whole scene.”

---

## 3. Transcription Is Often the Real Bottleneck

**Title / area**
- `Mobile Suit Gundam: Char's Counterattack`
- official English subtitle file vs our transcript export

**What happened**
- A generated transcript line said:
  - `He's possessed by Allah.`
- The official subtitle at the same time was:
  - `who he lost in the One Year War.`
- Nearby lines showed the likely root cause:
  - the anime name `Lalah` drifted toward `Allah`

**Why it was hard**
- This was not a simple word substitution.
- The pipeline was also reconstructing surrounding sentences incorrectly.
- Anime names, invented terms, military titles, and lore-heavy dialogue are especially fragile under STT + translation.

**What we changed**
- We separated:
  - original-language STT
  - translation as a second step
- We made the main pipeline use translated transcript output when available.
- We established the rule that if official subtitles exist, they are a far better source of truth than STT.

**What to watch next**
- This is the single biggest quality risk for subtitle-heavy content.
- If customers can upload subtitle files, that should be the preferred path.
- STT should remain fallback, not the gold standard, for complex named-entity content.

---

## 4. AA10 Profanity: Generic Swearing Was Over-Driving Audio Counts

**Title / area**
- `Zamal Paradise`
- repeated `fuck` lines

**What happened**
- The system was flagging many lines like:
  - `What the fuck are you doing here?`
  - `What the fuck is wrong with you?`
- The workbook and V3 guidance did not support logging every plain `fuck` line this aggressively.

**Why it was hard**
- Forced-English STT was sometimes producing overly aggressive English.
- Prompt rules were too broad for profanity.
- Repeated mild profanity overwhelmed more meaningful language issues.

**What we changed**
- Narrowed `AA10` to:
  - c-word
  - repeated/sustained strong swearing
  - clearly abusive personal attacks / threats
- Added post-filters so:
  - the same sentence does not keep both `AA10` and a more specific issue
  - mild one-off f-word idioms are suppressed

**What to watch next**
- Plain `bastard` / `asshole` is now more likely to be ignored unless the model emits a stronger abusive reading.
- That is fine for current V3, which mainly cares about c-word and racist language, not every insult.

---

## 5. AA9 Sexual Dialogue: Sentence-Local Meaning Matters More Than Window Vibe

**Title / area**
- `Ted trailer`
- sexual dialogue vs weak innuendo

**What happened**
- We wanted to recover:
  - `You know what I like to do to her? Something I call a dirty fuzzy.`
- But we did not want to also flag:
  - `Not looking up your towel, swear to God.`

**Why it was hard**
- The model was reading sexual meaning from the whole window, not strictly from the quoted sentence.
- Once one clearly sexual line appeared, a nearby teasing/defensive line could inherit the same vibe.

**What we changed**
- Tightened `AA9` so it explicitly says:
  - judge each quoted sentence on its own words
  - do not use nearby sexual lines to turn a non-sexual sentence into `AA9`
  - exclude teasing, defensive denials, voyeur/joke banter, and vague innuendo unless clear sexual act or sexual intent is stated
- Reduced transcript packing and restored `30s / 5s` windows with a lower `max_chars` default.

**What we learned**
- For dialogue classification, the prompt must explicitly tell the model what **not** to inherit from surrounding lines.
- “Window context” is helpful, but must not replace sentence-local evidence.

---

## 6. Audio Scheme Bug: One Per Group Per Window Was Too Aggressive

**Title / area**
- audio classifier design

**What happened**
- The classifier originally collapsed to one issue per group per whole window.
- That meant two distinct `AA9` moments inside one 30s/60s window could collapse into one before later filters even ran.

**Why it was hard**
- This logic was originally meant to reduce spam.
- In practice, it silently deleted legitimate same-group events inside the same window.

**What we changed**
- Changed the internal collapse rule to:
  - one issue per `group + exact sentence span`
  - not one issue per whole window
- Exposed and reduced `max_chars` so shorter windows are not overloaded with text.

**What to watch next**
- This keeps the audio scheme closer to how operators think:
  - one sentence can have one best issue
  - but separate sentences in the same window should survive independently

---

## 7. AV18 Revealing Attire: Over-Protection Against Party Fashion Created Misses

**Title / area**
- `Ted trailer`
- women on couch in revealing party/clubwear

**What happened**
- A wider shot with several women on a couch in very revealing attire was missed.
- A tighter nearby shot of the same scene was detected.

**Why it was hard**
- We had added strong guardrails to avoid overflagging ordinary evening dresses or party wear.
- Those guardrails were useful for titles like `Emily in Paris`, where normal fashion scenes can be very revealing without being policy-relevant.
- But they became too strict for V3 when the frame was “almost naked in effect” without explicit underwear visibility.

**What we changed**
- Simplified `AV18` guidance:
  - do not flag ordinary evening/cocktail/party wear
  - do flag clearly sexualized or unusually revealing presentation even if underwear is not visible
  - allow fishnets, very short dresses, very exposed chest, and provocative posed presentation to trigger

**What we learned**
- “Normal social context” should not override obviously sexualized visual presentation.
- The model needed simpler, more balanced language, not more exceptions.

---

## 8. Visual Overlap: Same Moment vs Same Scene

**Title / area**
- `Zamal Paradise`
- AV4 / AV5 / AV7 / AV8 / AV18 overlap clusters

**What happened**
- One intimate sequence could create many nearby rows:
  - `AV8 intimacy`
  - `AV18 modesty`
  - `AV4 nudity`
  - `AV7 LGBTQ`
- The workbook usually treated this as one event; our system logged several manifestations.

**Why it was hard**
- Some pairs should be kept:
  - different nearby shots with slightly different useful moments
- Some pairs should be mutually exclusive:
  - `AV4 strong nudity` should override nearby `AV8`
  - clear `AV7` can override generic `AV8`
  - generic `AV8` should override weak inferred `AV7`

**What we changed**
- Added local dominance rules in the visual classifier:
  - `AV4 > AV8/AV18` for same-moment overlap
  - explicit `AV7` can beat generic `AV8`
  - weak/inferred `AV7` loses to `AV8`
  - strong `AV18 sexual` can beat weak `AV8`
- Kept merging local, not global.

**What we learned**
- The right abstraction is:
  - same moment -> one best label
  - same scene -> maybe several labels, but only if operator value is real
- The tricky part is not same-shot duplication; it is short cut sequences around the same action.

---

## 9. Background Repetition: Merge Carefully, Locally

**Title / area**
- `Zamal Paradise`
- poster walls, drug-room scenes, repeated background imagery

**What happened**
- Background `AV5` and `AV12` rows could explode across nearby shots.
- We temporarily broadened merge logic to collapse them more aggressively.

**Why it was hard**
- That broader merge reduced noise, but violated the original local-only principle.
- It risked merging non-adjacent recurrences that looked similar but were not truly the same moment.

**What we changed**
- Reverted back toward local-only behavior:
  - same shot
  - adjacent shot
  - tight frame/time proximity

**What we learned**
- For production, local merge rules are safer than broad scene-level collapse.
- It is better to under-merge slightly than to erase genuinely distinct recurrences.

---

## 10. Profiles Bug: Read Path Was Profile-Aware, Write Path Was Not

**Title / area**
- report UI profile mode

**What happened**
- When viewing a report through a selected profile, deleting or editing an issue modified the original/default result instead of the profile result.

**Why it was hard**
- The read path already respected profile folders.
- But create/update/delete API routes still wrote directly to the base `result_path`.

**What we changed**
- Passed the active profile from the report UI in mutation requests.
- Resolved the target result folder with the same profile-aware helper used by report loading.

**What we learned**
- Profile support must be consistent across:
  - read
  - export
  - create
  - update
  - delete

---

## 11. Translation Flow: Original Transcript Must Always Survive

**Title / area**
- STT / translation pipeline

**What happened**
- We needed English transcript output for downstream classification and the UI.
- But forcing English during STT produced bad multilingual results.

**What we changed**
- Made STT run in original language first.
- Translation became a separate step.
- The pipeline now preserves:
  - original transcript
  - translated transcript used downstream

**What we learned**
- This separation is critical for debugging.
- If translation is wrong, you need the original transcript preserved.

---

## Summary Heuristics

These are the practical rules that emerged from all of the above:

- Prefer official subtitle files over STT whenever available.
- Use watchlists as cues, not as literal trigger lists.
- Keep prompt wording simple; too many exceptions can suppress true positives.
- Judge audio issues at the sentence level, not the window “vibe” level.
- For overlap, pick the best label for the same moment.
- Merge locally, not globally.
- Do not let anti-noise logic silently erase real events inside the same window.

---

## Best Candidates For Future Regression Tests

- `Brother Orange`:
  - China-sensitive maps
  - Tiananmen / Mao late visuals
  - censorship / jail / internet dialogue
- `Zamal Paradise`:
  - blasphemy block
  - gesture cases
  - mannequin / artwork nudity
  - intimacy overlap clusters
- `Ted trailer`:
  - revealing partywear wider vs tighter shots
  - AA9 sexual line vs weak nearby banter
- `Mobile Suit Gundam: Char's Counterattack`:
  - subtitle source vs STT drift
  - named entities and lore-heavy translation failures
