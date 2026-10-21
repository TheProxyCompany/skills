---
name: proxy-cli
description: >
  Control a running Proxy instance via the proxy CLI. Use when: running or creating
  party sessions, sending messages to agents, firing standing parties, managing
  agents/loadouts/models, checking system health, configuring harnesses/integrations,
  inspecting Work and workspaces, or any programmatic interaction with Proxy.
  Triggers: "create a party", "send to proxy", "proxy session", "talk to agents",
  "start a party about X", "fire the party", "proxy model", "proxy harness",
  "proxy config", "proxy work".
  Requires Proxy to be running (port 51711 default, or $PROXY_PORT).
---

# Proxy CLI

Binary: `proxy`. `~/.local/bin/proxy` links to the copy inside the installed app bundle (`Proxy.app/Contents/MacOS/proxy-cli`); a worktree build carries its own copy in its bundle. Build only through `Proxy/scripts/dev_cycle.sh`.
Requires: Proxy running on localhost:51711 (or `$PROXY_PORT`).

`proxy --help` and `proxy <group> [<command>] -h` are the source of truth. Below the top level use `-h`: a nested `--help` falls through to the agent shortcut (last section) and errors. This reference was regenerated from the installed binary on 2026-09-02; when a command is missing here, `-h` wins.

## Global Flags

- `-p, --port <PORT>` — HTTP port (default 51711, reads `$PROXY_PORT`)
- `-f, --format json|human` — output format (default json)
- `--host <HOST>` — target host (default 127.0.0.1)

Use `-f human` for readable output. Use default json when parsing responses programmatically.

## Core Workflow: Run a Party

Reuse existing roster agents. A requested model or role is not a new agent:
Fable means Claude with a Fable model and the `claude-code` harness; Gemini
Argon means Gemini with an Argon model; Astra means Codex with an Astra model
and the `codex` harness. Honor an explicitly requested compatible harness;
otherwise retain Gemini's configured compatible harness. Discover actual IDs
with `proxy agent list`, `proxy model list`, and `proxy harness list` rather
than inventing them. If an alias is ambiguous or unavailable, report that;
creating a new agent does not make a model available.

Do not use `proxy agent create` for a party's model, role, tools, or skills.
Create a roster identity only when the user explicitly wants a new reusable
agent. Names such as “Fable Coder” or “Astra Coder” belong on a seat loadout's
`display_name`, not in the agent roster. Multiple seats can use the same agent
with different loadouts.

The fast path seats roster agents by name, posts the prompt, streams the feed to stderr, and prints the transcript when the party goes quiet:

```bash
proxy party run --agents "claude,codex" --name "Pricing review" "Analyze this pricing model: ..."
proxy party run --agents "claude,codex,gemini" --flow 'author -> [reviewer*2] ~> synthesizer' "..."
proxy party run --format-id debate --agents "claude,gemini" --timeout 600 --json "..."
```

`--format-id` takes `forum`, `swarm`, `pair_programming`, or a standing party definition id (default: forum for several agents, swarm for one).

Use that fast path only when the agents' default loadouts already match the
request. For a particular model, harness, tools, or skills, use an explicit
seat loadout as below; `--agents` selects identities, not model aliases.

Or build the session by hand:

```bash
# 1. Create a session. --team accepts only `roster`; stored teams became party definitions.
proxy party session create --title "Business Model Discussion" --team roster

# 2. Or create it empty and seat participants yourself
proxy party session create --title "Quick Chat"
proxy party session add-participant <SESSION_ID> '{"agent_id":"<AGENT_ID>","role":"participant"}'

# 3. Send a message (triggers a full agent round)
proxy party session send <SESSION_ID> --content "Analyze this pricing model: ..."

# 4. Read the responses
proxy party session messages <SESSION_ID> -f human

# 5. Continue the conversation
proxy party session send <SESSION_ID> --content "What about per-model margin tiers?"
```

### Configure a seat without growing the roster

1. Inspect `proxy agent list`, `proxy loadout list`, `proxy model list`, and
   `proxy harness list`. Match the requested model by catalog name/family/variant
   and use its exact ID and provider. Check the chosen harness is available.
2. Reuse a loadout only if its model, harness, skills, and integrations already
   match. Otherwise create a named loadout on the existing agent. Do not edit
   or activate its global default just to configure this party.
3. Equip the requested skills and connected integrations on that loadout,
   then seat the existing `agent_id` with the explicit `loadout_id`.

For example, after confirming these model/harness IDs in the local catalogs
and substituting the IDs returned by the commands:

```bash
proxy loadout create '{"agent_id":"<EXISTING_CLAUDE_ID>","name":"Pricing review - Fable","display_name":"Fable","provider_id":"anthropic","model_id":"claude-fable-5-1","backend_model":null,"harness_id":"claude-code"}'
proxy loadout skill equip <LOADOUT_ID> <SKILL_ID>
proxy loadout integration equip <LOADOUT_ID> <CONNECTED_INTEGRATION_ID>
proxy party session add-participant <SESSION_ID> '{"agent_id":"<EXISTING_CLAUDE_ID>","loadout_id":"<LOADOUT_ID>","role":"participant"}'
proxy party session participants <SESSION_ID>
proxy agent self --session <SESSION_ID> --agent <EXISTING_CLAUDE_ID>
```

Equip only what the task needs; a new loadout receives default equipment, not
a copy of all equipment from the agent's existing loadout. Keep `backend_model`
null when using a catalog `model_id` so a stale custom model does not override
it. For multiple seats of the same agent, inspect each participant's
`loadout_id` and its entry in `proxy loadout list`; `agent self` selects one
seat. Inspect each loadout's equipment with `proxy loadout skill list <ID>`
and `proxy loadout integration list <ID>`; `loadout list` does not include
equipment. Verify model, harness, skills, and integrations before sending work.
Also inspect the participant's `config_overrides.seat_model`: a prior seat
override takes precedence over the loadout's model. Clear a stale override
when configuring the model through the loadout, preserving unrelated config
keys (`set-config` with a participant ID replaces that seat's config object).
For standing parties, put this configuration in `loadouts/*.md` and bind it
from `team.<role>.loadout`; omit or clear a conflicting `roles.<role>.model`
(see `party-maker`).

When changing an already seated participant, verify its current `loadout_id`
after editing the definition. `set-config` changes overrides, not the loadout
binding, and `add-participant` creates another seat. The CLI has no in-place
loadout rebind command; use the party seat's loadout selector in the app to
preserve its identity. Manifest-owned seats can reconcile on a later wake,
but manually added seats are protected. Do not send work through the old
binding or add a duplicate to work around this.

If creating/tuning/equipping fails, stop before seating or sending work.
Inspect the returned loadout ID (or `proxy loadout list`) before retrying:
creation and tuning are separate requests, so a failed tuning step can leave
a partially configured loadout. Repair that party-owned loadout rather than
creating another identity or blindly repeating creation.

### Session config (working directory)

```bash
proxy party session set-config <SESSION_ID> '{"working_directory":"/path/to/repo"}'

# Per-participant config
proxy party session set-config <SESSION_ID> <PARTICIPANT_ID> '{"working_directory":"/other/path"}'
```

### Format override (change conversation style per-message)

```bash
proxy party format list -f human
proxy party format roles <FORMAT_ID>
proxy party session send <SESSION_ID> --content "Debate this" --format-id debate
```

## Standing Parties

A standing party is a folder under `$PROXY_DATA_ROOT/parties/<id>/` (`party.yaml`, `playbook.md`, `roles/*.md`, `loadouts/*.md`); the `proxy-parties` skill covers the folder format.

```bash
proxy party definition list -f human      # id, name, device, cron, enabled, next fire, last fire
proxy party definition get <ID>
proxy party definition enable <ID>        # sets schedule.enabled in party.yaml
proxy party definition disable <ID>
proxy party definition fire <ID> [--timeout SECS] [--json]   # fire now and stream to quiescence
proxy party fire <ID> [--timeout SECS] [--json]              # same thing
proxy party definition rollover <ID>      # close the current season, open the next
proxy party devices                       # mesh devices a manifest `device:` can name
proxy party save <SESSION_ID>             # write a live session as a standing party folder
proxy party bench [--definition ID | --conversation ID | --agents NAMES "prompt"] [--rounds N] [--json]
```

## Commands Reference

### Party (sessions, messages, search)

```bash
proxy party session list [--limit N] [--include-archived]
proxy party session create [--title TEXT] [--team roster] [--message TEXT] [--json '{}']
proxy party session get <ID>
proxy party session update <ID> '{"title":"New Title","pinned":true}'
proxy party session delete <ID>
proxy party session participants <ID>
proxy party session add-participant <ID> '{"agent_id":"...","role":"participant"}'
proxy party session add-external <ID> --thread <THREAD_ID> [--role ROLE] [--name NAME] [--agent-id A] [--loadout-id L]
proxy party session remove-participant <SESSION_ID> <PARTICIPANT_ID>
proxy party session set-config <ID> [PARTICIPANT_ID] '{"working_directory":"..."}'
proxy party session messages <ID> [--limit N] [--all] [--threads]
proxy party session send <ID> --content "message" [--format-id FORMAT]
proxy party search --query "text" [--limit N]
proxy party format list
proxy party format roles <FORMAT_ID>
proxy party external list [--provider codex|claude-code|hermes] [--limit N] [--include-archived] [--no-refresh]
```

### Agents

`create` creates a persistent roster identity. Party setup normally uses an
existing identity and a seat-specific loadout instead (workflow above).

```bash
proxy agent list
proxy agent get <ID>
proxy agent self --session <CONVERSATION_ID> --agent <AGENT_ID>   # your seat: participant, loadout, tools, skills
proxy agent create '{"name":"Scout","accent_color":"#4CBCF2"}'   # backend/model fields belong on the loadout
proxy agent update <ID> '{"name":"..."}'
proxy agent delete <ID>
proxy agent sync          # sync from the remote registry
proxy agent reset         # force-reset to registry defaults
proxy agent defaults list [--scope party]
proxy agent defaults set '{"scope":"party","role":"moderator","agent_id":"...","position":0}'
proxy agent defaults remove '{"scope":"party","role":"moderator","agent_id":"..."}'
proxy agent job list <AGENT_ID>           # agents/<ID>/jobs/<JOB_ID>.json recurring jobs
proxy agent job set <AGENT_ID> '{"id":"morning","name":"Morning check","cron":"0 9 * * 1-5","prompt":"Review open work.","device":"Proxy Terminal 1"}'
proxy agent job remove <AGENT_ID> <JOB_ID>
```

### Models

```bash
proxy model list [--provider X] [--family X] [--embedding]
proxy model get <ID>
proxy model resolve <IDENTIFIER>
proxy model family list [--party-only]
proxy model family set-variant <FAMILY_ID> <VARIANT_ID>
proxy model family set-slot <FAMILY_ID> [SLOT]
proxy model provider list [--category X]
proxy model provider get <ID>
proxy model provider access-modes <PROVIDER_ID>
proxy model provider set-access-mode <PROVIDER_ID> <MODE_ID>
proxy model target list / create '{...}' / update / delete
```

### Providers (API keys)

```bash
proxy provider list
proxy provider key set <PROVIDER> <KEY>
proxy provider key remove / status / test <PROVIDER>
```

### Harnesses (Claude Code, Codex, OpenCode)

```bash
proxy harness list
proxy harness status <ID>                 # claude-code, codex, opencode
proxy harness configure / unconfigure <ID>
proxy harness probe <ID>                  # ACP initialize/session handshake
proxy harness connect / disconnect <ID>
proxy harness set-path <ID> <PATH>
proxy harness run <ID> -- <ARGS>
proxy harness discover <ID>
proxy harness config <ID>
proxy harness config-set <ID> <KEY> <VALUE>
proxy harness schema <ID>
proxy harness tunnel get / set '{...}' / clear
```

### Integrations (MCP servers)

```bash
proxy integration list [--connected]
proxy integration get / remove <ID>
proxy integration add '{"name":"GitHub","slug":"github","transport":"http","transport_config":{"url":"..."}}'
proxy integration connect stdio <ID> '{"command":"...","args":["--stdio"],"env":{}}'
proxy integration connect http <ID> '{"url":"...","headers":{}}'
proxy integration disconnect <ID>
proxy integration tools <ID>
proxy integration import          # import from external MCP config files
proxy integration registry search [--query Q] [--category C] [--sort S] [--limit N] [--offset N]
proxy integration registry refresh
proxy integration registry install <NAME> [--curated]
proxy integration key set <SLUG> <KEY_NAME> <KEY>
proxy integration key delete <SLUG>
```

### Loadouts & Skills

```bash
proxy loadout list
proxy loadout create '{"agent_id":"...","name":"Deep Work","provider_id":"anthropic","model_id":"..."}'
proxy loadout delete / activate <ID>
proxy loadout tuning <ID> '{"provider_id":"...","backend_model":"...","model_id":"...","display_name":"...","temperature":0.7}'
proxy loadout skill list <LOADOUT_ID>
proxy loadout skill equip / unequip <LOADOUT_ID> <SKILL_ID>
proxy loadout integration list <LOADOUT_ID>
proxy loadout integration equip / unequip <LOADOUT_ID> <INTEGRATION_ID>
proxy skill source list
proxy skill source add <ID> <NAME> <PATH>
proxy skill source add-git <ID> <NAME> <REPOSITORY_URL> [--skills-path skills]
proxy skill source add-remote <ID> <NAME> <REMOTE_HOST> <REMOTE_PATH>
proxy skill source sync <ID>
proxy skill source remove <ID>
proxy skill defaults
```

### Work (workspaces)

```bash
proxy work                        # the Work feed (same as `proxy work ls [--hours N]`)
proxy work sites                  # list workspaces
proxy work site show <ID>         # one workspace with a live health probe
proxy work site new [--root PATH | --root-id ID] [--kind git|folder|blank] [--data-root none|fresh|imported] [--wait]
proxy work site lease <ID> [--conversation ID --participant ID | --move ID | --manual] [--goal NODE] [--lifetime firing|work] [--escape sandbox|push-branch|push|apply]
proxy work site apply <ID> [--path P]... [--force]
proxy work site merge <ID>        # commit, rebase and push the submodule work, then bump pointers
proxy work site discard <ID> [--force]
proxy work site unstick <ID>      # abort a frozen rebase/merge and clear stale index locks
proxy work site path <ID>         # cd "$(proxy work site path <ID>)"
proxy work draft <ID>             # what a workspace proposes: its draft against where it started
proxy work root list / add <LABEL> [--path P] [--kind K] / rm
proxy work pool [--root PATH] / set [--target N] [--max N] [--enabled BOOL] [--min-free-gb N] / warm [--root PATH]
proxy work env                    # the checkout you stand in: slot, port, data root, isolation, branch
proxy work doctor                 # per-workspace health: dirty, unpushed, stuck, held, stranded, lost
proxy work reconcile              # reconcile workspace rows against git and disk
```

Whether `proxy work site merge` may push depends on the holder's escape right: `sandbox` keeps the work in the workspace, `push-branch` parks it on `work/<ID>`, `push` lets it reach main. A standing party grants the right per seat with `worksite.escape` in `party.yaml` (spelled `sandbox`, `push_branch`, `push` there).

### Config & System

```bash
proxy config list
proxy config get <KEY> / set <KEY> <VALUE>       # value parsed as JSON when valid
proxy config gc get / update '{...}'
proxy system health
proxy system snapshot create / list / restore <PATH> / merge <PATH> [--include-party]
proxy system orchard status / start / stop
proxy system navigate widget <home|timeline|roster|actions|command|lifeMap> [--tab T] [--node-id ID]
proxy system navigate party [--session-id ID]
proxy system navigate attic [--section general|keys|integrations|accounts|party|orchard|proxyIng|harness]
proxy system update check / status / install     # Sparkle updates
proxy screenshot [--output path.png]
```

### Images, proxy.ing, feedback

```bash
proxy image generate "<prompt>" [--provider openai] [--model gpt-image-2] [--size 1024x1024] [-n N] [-o PATH]
proxy ing pair [--username U] [--no-wait]        # pair this Mac with its proxy.ing address
proxy ing status
proxy feedback submit --user-report "User's exact words" \
  --summary "Short title" --details "Observed and expected behavior" \
  [--category bug|usability|feature|performance|other] \
  [--reproduction "Steps"] [--log-excerpt "Redacted excerpt"] \
  [--screenshot /path/from/proxy-screenshot.png | --no-screenshot]
```

Use the `proxy-feedback` skill before submitting diagnostics. Proxy attaches
the authenticated device and app version automatically. When `--screenshot`
is omitted, Proxy captures its current window unless `--no-screenshot` is set.

### Agent shortcut

Any first word that is not a command group runs a party of one with that roster agent:

```bash
proxy claude "Summarize the open Moves" [--timeout SECS] [--json]
```

## Tips

- **Always check `proxy system health` first** if commands fail — Proxy may not be running.
- **`proxy party run --agents` is the fast path** — it seats, posts and prints the transcript in one call.
- **`send` triggers a full agent round** — all participants respond. This is async; poll `messages` to see responses.
- **JSON payloads must be valid JSON objects** — use single quotes around the JSON to avoid shell escaping issues.
- **Port differs in worktrees** — run `proxy work env`, or `source .worktree-env`, and use its `PROXY_PORT`. A `wt.sh` worktree gets a hashed port; only `proxy work site` worksites use `51711 + slot`.
