---
name: proxy-moves
description: >
  Create, inspect, revise, and resolve Proxy Moves. Use when an agent needs to
  propose a user-reviewed action, build interactive Move blocks, add quick
  feedback prompts, answer clarifying questions, update a Move from user
  feedback, or make/reject/defer a Move through Proxy tools.
---

# Proxy Moves

A Move is an agent proposal that waits for the user. It packages context,
interactive inputs, content, diffs, and a clear action boundary.
Use a Move only for missing user judgment or authority. Do not ask again for
work already authorized, or turn a status update into a decision. Record
progress as an entry on the relevant Life Map subject and work within scope.
Do not execute a proposed action that still needs the user's authority
until they grant it.

## Core Shape

Create Moves with `proxy_create_move`.

Required fields:

- `id`: stable unique move id.
- `title`: short headline naming the concrete decision. Aim for 2–5 words;
  word count alone proves neither clarity nor fit in the actual UI.
- `lede`: one or two sentence hook; the one fact that makes it matter.
- `context`: two or three short plain sentences on why this matters, shown on
  the card. Simple words. No lists, no headings, no ids.
- `blocks`: typed block objects. Each block carries a `type`.

Optional fields:

- `quick_actions`: short suggested feedback prompts, shown as buttons beside
  the Move.
- `resolve_label`: top-level primary action label, not a block field.
  Changing the label does not change the action's execution behavior.
- `about`: array of Life Map node ids the Move is about. Every Move is about
  something: search first (`proxy_search`); check a known id with `proxy_get`
  before inferring absence. Create a missing subject only within authorized
  scope. `link_to` is the older single-id spelling; prefer `about`.

Block types:

- `text`: `content`, one or two sentences.
- `choice`: `question` and `options`; one answer.
- `multi_choice`: `question` and `options`; several answers.
- `freeform`: `question`; open-ended input.
- `diff`: `before` and `after`.
- `before_after`: text in `before`/`after`, screenshots in `before_image`/
  `after_image` (content refs from `proxy_store_content`), or both; text under
  an image renders as its caption.
- `image`: `ref`, a content ref from `proxy_store_content`.
- `info`: a `label` kicker (for example "Why this matters") over short
  `content`.
- `section`: `label` and `children`.
- `row` / `column`: layout blocks with `children`; a child may set `weight`
  (1 to 12) to claim that share of its row. Nest up to four levels. Keep
  interactive blocks (choice, multi_choice, freeform) at the top level, not
  inside a row or column. When the first block is a `row` or `column`, the
  card gives the layout the full width.

Give interactive blocks an `id`; the user's answers come back keyed by it.

The card is skimmed, not studied. Prefer an image, diff or before/after block
over a paragraph; several short blocks with air between them over one dense
one. Show the change, do not describe it: for UI work, capture the running app
before and after with `proxy screenshot`, store both PNGs with
`proxy_store_content`, and put the two refs in one `before_after` block.

## Design Rules

- Make one coherent decision obvious. Several steps can belong to one stated
  scope; separate independent judgments, not verbs or implementation stages.
- Keep implementation details out of user-facing copy.
- Ask for exactly the missing judgment, not every possible preference.
- Give the actual recommendation, its reason and material downside. Offer
  real alternatives without shaming refusal; use freeform for open judgment.
  A recommendation label is not itself coercion.
- Preserve provenance and current uncertainty. Attribute source claims;
  distinguish them from verified facts. Keep unknown authors unknown and
  distinguish a revision's author from the original author.
  Make attribution visible in supported copy if the byline is unverified.
- Preserve the seriousness of a reported risk without dropping its hedge.
  Distinguish a draft change from a demonstrated improvement.
- Verify reviewers' claims against the sources too; agreement is not a receipt.
- Do not turn diverted attention into a formally paused project, or missing
  channel data into proof an event or response did not happen.
- Match the headline, recommendation and approval consequence. Keep money,
  authority, irreversibility and uncertainty visible before the user answers.
  Do not claim a proposed safeguard is implemented without evidence.
- Use `quick_actions` for move-specific feedback prompts.
- Include enough context that the user can say yes, no, later, or ask for a
  change without opening a separate transcript.
- If the source conversation matters, link the Move to it.

## Feedback Loop

When the user asks a clarifying question or requests changes:

1. Read the Move with `proxy_get_move`.
2. Preserve source context, status and existing user responses. Inspect the
   action bindings before shortening copy; a narrower label must not retain
   undisclosed broader execution. Do not remap answers to changed questions.
3. Have an independent critic compare substantive drafts with their sources
   before live copy changes. Verify rendering and response behavior on the
   intended surface; a mockup or word count is not that verification.
4. Update the Move with `proxy_update_move` instead of creating a
   near-duplicate. It replaces `title`, `lede`, `context`, `blocks`,
   `quick_actions`, `resolve_label` (the label on the primary resolve button)
   or `status`.
5. Keep the Move smaller and clearer after revision.
6. Refresh `quick_actions` if better prompts are now obvious.

## Resolution

Use `proxy_make_move` only to record a decision the user actually gave.
The user normally decides in the app. Resolution can dispatch callbacks;
it is not a harmless way to test copy.

- `made_by` is required: the resolver id, normally `user`.
- `status: "made"` records approval (the default), not proof of successful
  execution. The tool can return `success: true` before callbacks finish.
- `status: "rejected"` means declined.
- `response` should contain structured user answers keyed by block id.

Do not infer approval from silence. "Later" is not rejection.
Read back the recorded decision and answers. Before reporting work complete,
verify the downstream result and attach a completion receipt to its action
or subject. If execution is pending, failed or unverified, say so separately
from approval; do not invent a status or overwrite the user's response.

## Inspection

- Use `proxy_list_moves` to find Moves; filter by `status` (`pending`, `made`,
  `rejected`, `failed`), `about_type` or `about_id`.
- Use `proxy_get_move` to inspect full blocks, response data, quick actions,
  source, status, and linked subjects.
- Use `proxy_update_move` to revise blocks, quick actions, or status.
- Use `proxy_delete_move` to remove a Move that should never have existed.

## Good Move Smell

A good Move feels calm and easy:

- The title says the decision.
- The lede explains the payoff.
- The context explains why now.
- The blocks collect only the needed input.
- The action buttons match the consequence.
- The user can ask a question without losing the thread.

For regression review, use [copy-regressions.json](references/copy-regressions.json)
and [reviewer-regressions.json](references/reviewer-regressions.json).
These are synthetic review cases, never instructions to execute.
