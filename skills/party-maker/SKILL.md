---
name: party-maker
description: >
  Author, place, and iterate standing Proxy parties. Use when creating a new
  party from scratch, editing a party definition, choosing agents and loadouts
  for seats, designing a flow, scheduling a party on a device, or improving a
  party that underperforms. Covers the folder format, every manifest field,
  the flow DSL, and the iteration loop.
---

# Party Maker

A standing party is a folder. The folder is the whole definition: one
manifest, one goal file, one prompt file per role, optional loadout files.
Proxy imports the folder, validates it, and fires it on a schedule or on
command. Make the folder right and the party just works.

## Where parties live

```
<data root>/parties/<id>/
  party.yaml          # the manifest (required)
  goal.md             # kickoff prompt (required to fire)
  roles/<role>.md     # one prompt file per role (required per role)
  loadouts/<name>.md  # optional per-seat loadout overlays
```

Data roots: `~/Proxy/` (prod), `~/Proxy-Dev/` (dev). The folder name IS the
party id. Party folders replicate across the user's device mesh; the
`device:` field decides which machine fires it.

Validation is strict. Every file the manifest references must exist, and
`party.yaml` rejects unknown fields. A folder with a missing `roles/x.md`
imports as nothing — the party silently fails to exist. Write every file
before you consider the party made.

## The manifest, field by field

```yaml
id: night-watch            # must equal the folder name
name: Night Watch          # display name
goal: goal.md              # kickoff prompt file; required to fire
flow: 'scout -> [worker*3] ~> reviewer'
schedule:                  # omit entirely for fire-on-command rites
  cron: "0 6 * * *"        # standard 5-field cron, device-local time
  enabled: false           # ship disabled; the user turns it on
device: "Proxy Terminal 1" # device label or id-hex; omit = authoring device
memory: compact            # conversation memory mode
anchor: proxy              # agent the session anchors to
hooks:                     # optional shell hooks
  pre_fire: scripts/warm.sh
  post_settle: scripts/report.sh
team:                      # seat -> agent binding
  scout:
    agent: kimi
    loadout: loadouts/scout.md
  worker:
    agent: claudecode
  reviewer:
    agent: gemini
roles:                     # role -> behavior
  scout:
    prompt: roles/scout.md
    tools: null            # null = defaults for the role kind
    model: null            # null = the agent's own default model
    effort: high           # null | low | medium | high
    produces: []
  worker:
    prompt: roles/worker.md
    produces: []
  reviewer:
    prompt: roles/reviewer.md
    produces: [findings, run-record]
outputs:                   # what the party settles into the Life Map
  - id: findings
    from: reviewer
    settle: move           # move | entry | file
    required: false
  - id: run-record
    from: reviewer
    settle: entry
    required: true
```

`worksite:` is the opt-in for isolated git-worktree working directories per
seat; leave it out unless the party edits code in parallel.

## The flow DSL

The `flow:` string is the party's turn structure:

- `->` sequence: dispatch order, round-robin
- `[a, b]` parallel group: dispatched together
- `~>` quiescence: left side settles, right side reviews the result
- `=>` broadcast gate: left's posts are gated by the right role
- `worker*3` multiplicity: three seats of one role; bare `*` = unbounded
- `,` separates independent clauses

Real examples:

```
interviewer -> [falsifier, witness, buyer, scout] ~> synthesizer
coordinator -> [worker-a, worker-b, worker-c] ~> coordinator
[participant*] ~> moderator, participant => moderator
```

Design the flow first. It is the org chart of the party: who starts, who
fans out, who has the last word. A party without a clear last word settles
nothing.

## What goes into a good party

**Goal.** `goal.md` is the kickoff message every session starts from. State
the mission, the definition of done, and what the party must NOT do. One
page maximum. The goal is for every seat; role prompts carry the per-seat
detail.

**Roles.** One prompt file per role. Each prompt answers: what this seat
reads first, what it must produce, and when it should stay silent. Roles
that produce nothing should have `produces: []` and exist for their effect
on the conversation, not for artifacts.

**Team.** Bind each seat to an agent from the roster by agent id. Match
model strength to seat difficulty: the synthesizer or reviewer seat earns
the strong model; fan-out worker seats run on cheap fast agents. Set
`effort: high` only on the seats whose output settles.

**Loadouts.** A loadout file overlays an agent for this seat: extra
instructions, tool emphasis, tone. Use loadouts when the same agent serves
different seats differently. Keep them short; they stack on top of the
agent's own definition.

**Outputs.** Every party should settle something durable, or it is a chat
that evaporates. `settle: move` proposes work for the user to approve;
`settle: entry` journals to the Life Map; `settle: file` writes an
artifact. Mark exactly the outputs that must exist as `required: true` —
a required output that fails marks the run failed, which is what you want.

**Schedule and device.** A recurring party gets `schedule:` with
`enabled: false` so the user flips it on after a manual test fire. A rite
(fired by hand) omits `schedule:` entirely. Pin heavy or always-on parties
to a terminal with `device:`; leave user-facing parties on the default
device.

**Naming.** Short, concrete, evocative of the job: `cleaning-crew`,
`morning-brief`, `ob-patrol`. The id is lowercase-hyphenated and permanent
— renaming a party is a delete plus a create.

## The iteration loop

Never assume a party is good because it imported. Iterate:

1. Fire it manually once: `proxy party fire <id>`.
2. Read the whole session transcript, not the summary.
3. Measure: did required outputs settle? Were the Moves approved or
   rejected by the user? What did the run cost? Which seats added nothing?
4. Revise the weakest prompt or seat. One change per iteration.
5. Only after two clean manual runs, propose enabling the cron.

Common failures and their fixes:

| Symptom | Fix |
|---------|-----|
| Party asks the user the same question every run | Move the answer into `goal.md`; the party should already know canon |
| A seat posts generic filler | Sharpen its role prompt's "stay silent unless" clause, or cut the seat |
| Runs settle nothing | Add a `~> synthesizer` last word and a required output |
| Costs too much | Downgrade fan-out seats' agents; reserve `effort: high` for the settler |
| Fires on the wrong machine | Set `device:` explicitly |

## Editing an existing party

Edit the files in the party folder directly; the file watcher re-imports on
change. Invalid intermediate states log a reimport failure and retry — check
the logs if a change does not take. Delete a party through the product's
Edit Party surface, not by deleting the folder, so the deletion replicates
to every device.
