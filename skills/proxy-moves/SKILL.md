---
name: proxy-moves
description: >
  Create, inspect, revise, and resolve Proxy Moves. Use when an agent needs to
  propose a user-reviewed action, build interactive Move blocks, add quick
  feedback prompts, answer clarifying questions, update a Move from user
  feedback, or make/reject/defer a Move through Proxy tools.
---

# Proxy Moves

A Move is an agent proposal (`https://moves.md`) that waits for the user. It
packages context, interactive inputs, content, diffs, and a clear action
boundary for one person reading on a phone or at his desk in ten seconds.

## When to Make a Move (4 Critical Boundaries)

Routine background scans (reading messages, checking threads, syncing Life Map
state, evidence patrols) must log quiet node updates (`proxy_mutate` with
`entry_type: "update"` and a `dedupe_key`) and NEVER create a Move unless they
hit one of four critical boundaries:

1. **Paywall or financial spend:** spending money, billing caps, paid
   commitments.
2. **External outbound communication:** sending emails, messages, or sensitive
   info outside the machine.
3. **Destructive or production-altering actions:** merging or approving PRs,
   reverting, deploying, releasing, changing settings/access, or deleting user
   data.
4. **Explicit Move-proposing role:** a role the user explicitly created to
   propose Moves.

**Do the work first, gate only the trigger.** Never propose a Move asking
"Should I investigate / draft / check X?" or "Dismiss this card?". Finish all
read-only research, verification, and drafting BEFORE calling
`proxy_moves_propose`, and attach the finished artifact (`copyable` draft,
`diff`, `before_after`) or `on_resolve` callback so one tap executes the work.
Pure status updates ("Done", "Merged", "Built") are rejected and belong on the
node as an `update` entry.

If an open pending Move already exists for the same `about` node or recurring
source, revise it in place instead of creating a near-duplicate. The server
enforces a 2-Move pending cap per source and blocks re-proposing recently
rejected Moves on that node.

## Core Shape (`proxy_moves_propose`)

Create or revise Moves with `proxy_moves_propose` (legacy aliases
`proxy_create_move` and `proxy_update_move` remain silently routed).

Required fields (on create):

- `id`: stable unique move id (e.g. `move-20261120-approve-pr-611`).
- `title`: one simple sentence, 10 words or fewer (up to 120 chars), stating
  the decision as a clear action (e.g. "Approve Root PR #611 now that checks
  pass").
- `lede`: one plain-English sentence (<= 140 chars target, 500 max) explaining
  who/what this is and why now. No raw git SHAs, database row IDs, or exact
  clock timestamps on the card surface.
- `context`: full background and technical provenance (2-4 sentences, up to
  1500 chars). Exact commit SHAs, file paths, and verification receipts belong
  here, not on the card surface.
- `blocks`: typed block objects (`https://moves.md/blocks`). Each block carries
  a `type`, and `content` holds up to 2000 chars. Lead with the artifact.
- `about`: array of Life Map node ids the Move is about. Search first with
  `proxy_search` or check a known id with `proxy_read` before inferring
  absence. (`link_to` is the legacy typed-object array alias; prefer `about: [node_id, ...]`.)

Optional fields:

- `resolve_label`: 2-4 words, 28 chars or fewer, naming the exact mechanical
  consequence of clicking the primary button (`"Send Email"`, `"Send Message"`,
  `"Approve PR #611"`). Never use `"Save Gmail Draft"` when the Move card
  already shows the draft and approving fires the send.
- `quick_actions`: short suggested feedback prompts shown as chips beside the
  Move.
- `op`: `"create"` (default) or `"update"` (with existing `id`) to revise a pending Move.
- `deadline`: optional ISO-8601 deadline timestamp.
- `replaces`: optional pending Move ID superseded by this Move.
- `on_resolve`: callback executed when the Move is made with its primary button
  (`https://moves.md/callbacks`).

## Match the Shape to the Decision

- **Single-action Move** (outbound email/message, PR approval, sheet row): show
  the finished artifact first (`copyable`, `before_after`, `diff`, `data`) and
  set a crisp `resolve_label`. Do NOT add a redundant `choice` block (the card
  already has Veto, feedback, and the primary button).
- **True fork (`choice`):** use only for 2-4 genuinely competing positive paths.
  Never include "No / Skip / Hold off" as a radio option (that is what Veto is
  for). Keep every option label under 70 chars so it never truncates; put
  tradeoffs in a `side_by_side` or `data` block above the choice, and mark your
  pick with `(Recommended)` inline.
- **Batch selection (`multi_choice`):** for 2+ independent items, pre-check
  `default_options` so the user can uncheck items in one click.
- **Open taste or steering (`freeform`):** use `freeform` with `quick_actions`
  chips rather than forcing pre-baked radio options.

## Block Catalog (`https://moves.md/blocks`)

Content blocks:
- `copyable`: `content` (required), optional `label`. Verbatim outbound draft
  or command with one-click copy.
- `text`: `content` (required). Short markdown prose (1-2 sentences).
- `info`: `content` (required), optional `label` kicker. Use sparingly for
  non-obvious context not in `lede`.
- `data`: `rows` (`[[String]]`), optional `headers` (`[String]`).
- `code`: `content`, optional `language`.
- `image`: `ref` (from `proxy_store_content`), optional `caption`, `alt`.
- `images`: `images` (`[{ref, caption?, alt?}]`), optional `caption`.
- `video` / `audio`: `ref`, optional `caption`.
- `file`: `ref` and `filename`.
- `terminal`: `content`.
- `kv`: key-value pairs for compact metadata.

Delta and comparison blocks:
- `before_after`: `before`/`after` text, `before_image`/`after_image` refs from
  `proxy_store_content`, or both; optional `label`. Always include screenshots
  for a visible UI change.
- `diff`: `before` and `after`, optional `filename`, `language`.
- `side_by_side`: `left` and `right`, optional `left_label`, `right_label`.
- `timeline`: `events` (`[{timestamp, label, description?, status?}]`).

Input and decision blocks (give each an `id`; user answers return keyed by it):
- `choice`: `question`, `options` (strings or `{label, image}`, each `< 70`
  chars), optional `default_option` (0-based).
- `multi_choice`: `question`, `options`, optional `default_options` (`[Int]`).
- `freeform`: `question`, optional `placeholder`.
- `toggle`: `question`, optional `default_value`.
- `numeric`: `question`, optional `min`, `max`, `step`.
- `ranking`: `question`, `items`.
- `date`, `file_upload`, `color`, `secret`, `rating`, `confirmation`,
  `native_view`.

Reference, signal, and layout blocks:
- `url` (`href`, optional `label`, `description`), `snippet` (`path`, `content`,
  optional `start_line`, `end_line`, `language`, `highlights`), `excerpt`
  (`content`, `source`, optional `source_url`, `highlights`), `person` (`name`,
  optional `role`, `avatar`), `file_path` (`path`), `graph_node` (`node_type`,
  `node_id`), `location` (`lat`, `lng`), `datetime` (`iso`).
- `warning` (`message`), `alert` (`message`, `severity?`), `progress` (`value`,
  `max?`, `label?`), `urgency` (`level`, `message?`), `expiration`
  (`expires_at`, `message?`).
- `section` (`label`, `children`, optional `collapsible`, `collapsed`,
  `condition`), `row` / `column` (`children`, optional child `weight` 1-12;
  nest up to 4 levels; keep interactive blocks at top level), `executable`
  (`label`, optional `description`, `command`, `children`, `strategy`).

## Design Rules

- Make one coherent decision obvious. Keep implementation details out of
  user-facing copy.
- When introducing an unfamiliar person, outlet, or concept, open with one
  plain-English sentence explaining who or what they are.
- Give the actual recommendation, its reason, and material downside. Offer real
  alternatives without shaming refusal.
- Preserve provenance and uncertainty. Attribute source claims; distinguish
  them from verified facts; verify reviewers' claims against primary sources.
- Match the headline, recommendation, and approval consequence. Keep money,
  authority, irreversibility, and uncertainty visible before the user answers.

## Feedback Loop & Inspection

- **Inspect:** Use `proxy_moves_read` (single `id`, or filtered/paginated list
  by `status` (`"pending"`, `"made"`, `"rejected"`, `"deferred"`, `"cancelled"`),
  `about_id`, `about_type`, `limit`, `offset`; v1 aliases `proxy_get_move` and
  `proxy_list_moves` remain routed).
- **Revise:** Use `proxy_moves_propose` with `op: "update"` (or existing `id`)
  instead of creating a near-duplicate. Preserve source context, status, and
  existing user responses; do not remap answers to changed questions.
- **Delete:** Use `proxy_delete_move` (human-gated) to remove a Move that
  should never have existed.

## Resolution (`proxy_make_move`, Human-Gated)

Use `proxy_make_move` only to record a decision the user actually gave.
Resolution can dispatch callbacks; it is not a harmless way to test copy.

- `made_by` is required: the resolver id, normally `user`.
- `status: "made"` records approval (the default), not proof of successful
  execution. The tool can return `success: true` before callbacks finish.
- `status: "rejected"` means declined.
- `response` carries structured user answers keyed by block id.

Do not infer approval from silence. "Later" is not rejection. Read back the
recorded decision and answers, verify the downstream result, and attach a
completion receipt to its action or subject.

For regression review, use [copy-regressions.json](references/copy-regressions.json)
and [reviewer-regressions.json](references/reviewer-regressions.json).
These are synthetic review cases, never instructions to execute.
