---
name: proxy-moves
description: >
  Create, inspect, revise, and resolve Proxy Moves. Use when an agent needs to
  propose a user-reviewed action, build interactive Move blocks, add quick
  feedback prompts, answer clarifying questions, update a Move from user
  feedback, or make/reject/defer a Move through Proxy tools.
---

# Proxy Moves

A Move is an agent proposal that waits for the user. It packages the minimum
evidence needed to judge a call, plus the exact control to fire it.

Use a Move only when you need user judgment or authority. Do not ask again for
work already authorized, and never turn a status update into a fake vote. Log
progress as an entry on the relevant Life Map subject instead. Do not execute
an action that needs the user's authority until they grant it.

## Core Shape

Create Moves with `proxy_create_move`.

Required fields:

- `id`: stable unique move id.
- `title`: short headline naming the concrete decision (2-6 words).
- `lede`: one punchy sentence naming the payoff or why now.
- `blocks`: typed block objects. Each block carries a `type`.

Optional fields:

- `context`: omit whenever `lede` + blocks already tell the story. Only use
  `context` when 1-2 short plain sentences of extra background genuinely change
  the decision. No lists, no headings, no raw IDs.
- `quick_actions`: short suggested feedback prompts shown beside the Move.
- `resolve_label`: primary button label (2-4 words, e.g. `Send Email`,
  `Book Laser Wolf`, `Approve PR #638`). Changing the label does not change
  execution behavior.
- `about`: array of Life Map node ids the Move is about. Search first
  (`proxy_search`) and verify known ids (`proxy_get`) before linking. Prefer
  `about` over the older `link_to`.

Block types:

- `text`: `content`, one or two short sentences max.
- `choice`: `question` and `options`; single answer.
- `multi_choice`: `question` and `options`; multiple answers.
- `freeform`: `question`; open-ended input.
- `diff`: `before` and `after`.
- `before_after`: text in `before`/`after`, screenshots in `before_image`/
  `after_image` (content refs from `proxy_store_content`), or both.
- `image`: `ref`, a content ref from `proxy_store_content`.
- `info`: a `label` kicker (e.g. `Why this matters`) over short `content`.
- `section`: `label` and `children`.
- `row` / `column`: layout blocks with `children` (optional `weight` 1-12,
  nested up to 4 levels). Keep interactive blocks (`choice`, `multi_choice`,
  `freeform`) at the top level, not inside a row or column.

Give interactive blocks an `id`; user answers return keyed by it.

## Visual Taste & The 3-Second Skim Test

A Move is skimmed, never studied. Write like a sharp chief of staff, not a
compliance memo.

- **3-second test:** If the user cannot grasp the call in three seconds, cut
  half the words before calling `proxy_create_move`.
- **Zero triple-text:** Never restate `title` in `lede`, or `lede` in
  `context`. If a visual block (`image`, `before_after`, `diff`, `choice`)
  speaks for itself, leave `context` empty.
- **Show, do not describe:** Prefer an `image`, `diff`, or `before_after` block
  over a paragraph. For UI work, capture the running app with `proxy screenshot`,
  store both PNGs via `proxy_store_content`, and put both refs in one
  `before_after` block.
- **One coherent call:** Ask for the exact missing judgment, not every possible
  preference. Offer real alternatives without shaming refusal.
- **Match the stakes:** Keep cost, irreversibility, and approval consequence
  obvious before the user clicks. Keep internal implementation jargon out of
  user-facing copy.
- **High-stakes / legal / review Moves:** For sensitive provenance, attribution,
  or risk-hedge rules, load [accuracy-guardrails.md](references/accuracy-guardrails.md).

## Good vs. Bad Taste

Bad (triple-text compliance sludge):
- `title`: "Review and Approve Proposed Saturday Evening Dinner Reservation Options with Ava"
- `lede`: "I researched three well-reviewed restaurants in Brooklyn for your upcoming Saturday evening dinner with Ava and would like your approval on which option to book."
- `context`: "Ava is visiting you in Brooklyn this weekend. Based on your preferences and proximity to Bushwick and Williamsburg, I identified three restaurants with Saturday availability on Resy. Please review the options below and confirm which reservation you want me to proceed with."

Good (3-second skim, zero repetition):
- `title`: "Book Saturday dinner with Ava"
- `lede`: "Kept it to Williamsburg and Bushwick since she's staying near you."
- `context`: *(omitted)*
- `blocks`: one crisp `choice` block (`Laser Wolf · 8:15 PM`, `Eyval · 8:30 PM`, `Lilia · 8:00 PM`).

## Feedback Loop

When the user asks a clarifying question or requests changes:

1. Read the Move with `proxy_get_move`.
2. Preserve source context, status, and existing user responses.
3. Update the existing Move with `proxy_update_move` instead of creating a
   duplicate. Make the revised Move shorter and clearer than before.
4. Refresh `quick_actions` if better follow-ups are now obvious.

## Resolution

Use `proxy_make_move` only to record a decision the user actually gave. The
user normally decides in the app; resolution can fire callbacks, so never use
it to test copy.

- `made_by`: required resolver id (normally `user`).
- `status: "made"` records approval (not proof execution finished).
- `status: "rejected"` means declined.
- `response`: structured user answers keyed by block id.

Never infer approval from silence. "Later" is not rejection. Verify downstream
execution before reporting work complete, and report pending or failed
execution separately from approval.

## Inspection

- `proxy_list_moves`: find Moves by `status` (`pending`, `made`, `rejected`,
  `failed`), `about_type`, or `about_id`.
- `proxy_get_move`: inspect full blocks, response data, quick actions, and
  linked subjects.
- `proxy_update_move`: revise fields, blocks, quick actions, or status.
- `proxy_delete_move`: remove a Move that should never have existed.

## Good Move Smell

- The title names the call in 2-6 words.
- The lede states the payoff in one breath.
- Context is omitted unless it genuinely changes the call.
- Visual blocks carry the weight; prose stays out of the way.
- The primary button matches the real consequence.

For synthetic regression checks, see [copy-regressions.json](references/copy-regressions.json)
and [reviewer-regressions.json](references/reviewer-regressions.json).
