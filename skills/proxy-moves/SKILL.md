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
interactive inputs, content, diffs, confirmations, and a clear action boundary.
Nothing important should happen until the user makes the Move.

## Core Shape

Create Moves with `proxy_create_move`.

Required fields:

- `id`: stable unique move id.
- `title`: short headline.
- `lede`: one or two sentence hook.
- `context`: background and why this Move exists.
- `blocks`: typed block objects.

Optional fields:

- `quick_actions`: short suggested feedback prompts shown beside the Move.
- `link_to`: Life Map node id the Move is about.

Common block types:

- `text`: explanatory content.
- `choice`: one answer from options.
- `multi_choice`: multiple answers from options.
- `freeform`: open-ended user input.
- `confirmation`: explicit confirmation copy.
- `diff`: before/after comparison.
- `section`: nested grouping of blocks.

## Design Rules

- Make the user's decision obvious.
- Keep implementation details out of user-facing copy.
- Do not label UI concepts like "inputs" or "references" unless the user needs
  to know them.
- Ask for exactly the missing judgment, not every possible preference.
- Use `quick_actions` for move-specific feedback prompts. Do not hard-code
  generic prompts in the client.
- Include enough context that the user can say yes, no, later, or ask for a
  change without opening a separate transcript.
- If the source conversation matters, link the Move to its source and expose an
  "open source chat" path in the UI.

## Feedback Loop

When the user asks a clarifying question or requests changes:

1. Read the Move with `proxy_get_move`.
2. Preserve the user's feedback as source context.
3. Update the Move with `proxy_update_move` instead of creating a near-duplicate.
4. Keep the Move smaller and clearer after revision.
5. Refresh `quick_actions` if better prompts are now obvious.

The authoring agent should receive feedback through the same route that created
the Move when the product surface supports it.

## Resolution

Use `proxy_make_move` when the user approves or rejects a Move.

- `status: "made"` means approved/executed.
- `status: "rejected"` means declined.
- `response` should contain structured user answers keyed by block id.

Do not infer approval from silence. "Later" is not rejection.

## Inspection

- Use `proxy_list_moves` to find pending or historical Moves.
- Use `proxy_get_move` to inspect full blocks, response data, quick actions,
  source, status, and linked subjects.
- Use `proxy_update_move` to revise blocks, quick actions, or status.

## Good Move Smell

A good Move feels calm and easy:

- The title says the decision.
- The lede explains the payoff.
- The context explains why now.
- The blocks collect only the needed input.
- The action buttons match the consequence.
- The user can ask a question without losing the thread.
