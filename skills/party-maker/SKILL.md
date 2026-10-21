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
manifest, an optional playbook, one prompt file per role, optional loadout files.
Proxy imports the folder, validates it, and fires it on a schedule or on
command. Make the folder right and the party just works.

## Where parties live

```
<data root>/parties/<id>/
  party.yaml          # the manifest (required)
  playbook.md         # optional standing instructions included at kickoff
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
flow: 'scout -> worker ~> reviewer'
schedule:                  # omit entirely for fire-on-command rites
  cron: "0 6 * * *"        # standard 5-field cron, device-local time
  enabled: false           # ship disabled; the user turns it on
device: "Proxy Terminal 1" # device label or id-hex; omit = authoring device
memory: compact            # conversation memory mode
anchor: <LIFE_MAP_NODE_ID>  # optional node whose context informs each firing
hooks:                     # optional shell hooks
  pre_fire: scripts/warm.sh
  post_settle: scripts/report.sh
team:                      # seat -> agent binding
  scout:
    agent: kimi
    loadout: loadouts/scout.md
  worker:
    agent: claude           # use the existing Claude agent's actual id
  reviewer:
    agent: gemini
roles:                     # role -> behavior
  scout:
    prompt: roles/scout.md
    tools: null            # null = defaults for the role kind
    model: null            # null = use the selected seat loadout's model
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
- Each role runs the seats explicitly listed in `team`. Legacy `worker*3`
  syntax is accepted, but does not create three seats or limit the team.
- `,` separates independent clauses

Real examples:

```
interviewer -> [falsifier, witness, buyer, scout] ~> synthesizer
coordinator -> [worker-a, worker-b, worker-c] ~> coordinator
[participant*] ~> moderator, participant => moderator
```

For three workers, list three bindings under `team.worker`, reusing the
existing agent with the desired loadout for each seat. Do not create extra
agent identities to get extra seats.

Design the flow first. It is the org chart of the party: who starts, who
fans out, who has the last word. A party without a clear last word settles
nothing.

## What goes into a good party

**Playbook.** `playbook.md` supplies standing instructions at kickoff; role
prompts carry per-seat detail. Put the party's method, expected results, and
boundaries here. `goal:` is retired and ignored; `goal.md` is not read at
kickoff. Use `anchor:` for a Life Map node whose goals and actions supply
current work, not for an agent identity.

**Roles.** One prompt file per role. Each prompt answers: what this seat
reads first, what it must produce, and when it should stay silent. Roles
that produce nothing should have `produces: []` and exist for their effect
on the conversation, not for artifacts.

**Team.** Bind each seat to an agent from the roster by agent id. Match
model strength to seat difficulty through each seat's loadout: the synthesizer
or reviewer seat earns the strong model; fan-out workers can share the same
agent with cheaper models. Set
`effort: high` only on the seats whose output settles.

**Loadouts.** A loadout configures the seat's model, provider, harness, skills,
integrations, display name, and prompt. Use one when the same agent serves
different seats differently. Bind it explicitly from the team seat; creating
a loadout does not select it automatically. Do not change the agent's global
default to configure a party.

`roles.<role>.model` overrides the loadout at request time. When selecting the
model through a loadout, omit that role override or set it to `null`; keep it
only when intentionally consistent with the requested model/provider/harness.
For an existing live seat, inspect `config_overrides.seat_model` as well as
`loadout_id`—a matching loadout alone does not prove the effective model.

### Model requests reuse agents

Before writing the team, inspect `proxy agent list`, `proxy loadout list`,
`proxy model list`, and `proxy harness list`. “Fable” means the existing Claude
agent with a Fable model and `claude-code` harness. “Gemini Argon” means the
existing Gemini agent with an Argon model. “Astra” means the existing Codex
agent with an Astra model and `codex` harness. Honor explicit compatible
harness choices; otherwise retain Gemini's compatible configured harness.
Use catalog IDs, not guessed aliases. Report missing or ambiguous models
instead of inventing a new agent.

Do not create agents such as “Fable Coder”, “Astra Coder”, or a party-specific
reviewer to configure a seat. Only create a new roster identity when the user
explicitly asks for a new reusable agent. Roles and loadout `display_name`
provide party-specific labels; multiple seats can share one agent identity.

For a Fable seat, use the existing Claude ID in `team`:

```yaml
team:
  worker:
    agent: <EXISTING_CLAUDE_ID>
    loadout: loadouts/fable-worker.md
```

Then write `loadouts/fable-worker.md` (confirm the model and harness IDs in
the local catalogs; use a name containing the party and role to avoid collisions):

```markdown
---
name: Night Watch - Fable worker
display_name: Fable
harness: claude-code
provider: anthropic
model_id: claude-fable-5-1
skills: []
integrations: []
---
Implement the assigned change and report the verification results.
```

The owning agent is inferred from the referencing team seat. `model_id` is
the catalog model; omit `model` (the custom backend override) when using it.
Fill `skills` with discovered skill IDs and `integrations` with the connected
tools this role needs. New file loadouts receive default equipment, not a
copy of the agent's existing loadout. These lists are not exact allowlists:
imports preserve non-file skills, and integrations are additive, so removing
an integration from the file does not unequip it. Inspect `proxy loadout skill
list <ID>` and `proxy loadout integration list <ID>`; explicitly unequip
unwanted extras only on a loadout owned by this party. Reuse an existing
matching loadout without changing shared configuration.

File loadouts are keyed by `(agent_id, name)`, not folder path. Different
parties or roles needing independent configuration must use different names.
An import that collides with a user-created loadout can be skipped; verify
the imported row's model, provider, harness, equipment, and team binding
before firing. Repair an incomplete loadout rather than creating new agents.
For a live session, also verify its participant `loadout_id`: editing the
manifest does not immediately rebind every seat. Manifest-owned seats can
reconcile on a later wake; manually added seats are protected. Use the app's
seat loadout selector for an immediate in-place change, preserving the seat's
identity, and verify the binding before sending work.

### Completing the definition

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
| Party asks the user the same question every run | Move standing instructions into `playbook.md` and current facts into the anchored Life Map node |
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
