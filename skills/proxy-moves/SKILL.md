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
Nothing important should happen until the user makes the Move.

## Core Shape

Create Moves with `proxy_create_move`.

Required fields:

- `id`: stable unique move id.
- `title`: short headline; the decision.
- `lede`: one or two sentence hook; the one fact that makes it matter.
- `context`: two or three short plain sentences on why this matters, shown on
  the card. Simple words. No lists, no headings, no ids.
- `blocks`: typed block objects. Each block carries a `type`.

Optional fields:

- `quick_actions`: short suggested feedback prompts, shown as buttons beside
  the Move.
- `about`: array of Life Map node ids the Move is about. Every Move is about
  something: search the map first (`proxy_search`) and create the node if it
  is missing. `link_to` is the older single-id spelling; prefer `about`.

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

- Make the user's decision obvious.
- Keep implementation details out of user-facing copy.
- Ask for exactly the missing judgment, not every possible preference.
- Use `quick_actions` for move-specific feedback prompts.
- Include enough context that the user can say yes, no, later, or ask for a
  change without opening a separate transcript.
- If the source conversation matters, link the Move to it.

## Feedback Loop

When the user asks a clarifying question or requests changes:

1. Read the Move with `proxy_get_move`.
2. Preserve the user's feedback as source context.
3. Update the Move with `proxy_update_move` instead of creating a
   near-duplicate. It replaces `title`, `lede`, `context`, `blocks`,
   `quick_actions`, `resolve_label` (the label on the primary resolve button)
   or `status`.
4. Keep the Move smaller and clearer after revision.
5. Refresh `quick_actions` if better prompts are now obvious.

## Resolution

Use `proxy_make_move` when the user approves or rejects a Move.

- `made_by` is required: the resolver id, normally `user`.
- `status: "made"` means approved/executed (the default).
- `status: "rejected"` means declined.
- `response` should contain structured user answers keyed by block id.

Do not infer approval from silence. "Later" is not rejection.

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
