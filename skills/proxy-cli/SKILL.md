---
name: proxy-cli
description: >
  Control a running Proxy instance via the proxy CLI. Use when: creating party sessions,
  sending messages to agents, managing teams/agents/models, checking system health,
  configuring harnesses/integrations, or any programmatic interaction with Proxy.
  Triggers: "create a party", "send to proxy", "proxy session", "talk to agents",
  "start a party about X", "proxy team", "proxy model", "proxy harness", "proxy config".
  Requires Proxy to be running (port 51711 default, or $PROXY_PORT).
---

# Proxy CLI

Binary: `proxy` (installed at `~/.local/bin/proxy`, or build with `cd Proxy/proxy-cli && cargo build --release` → `target/release/proxy-cli`)
Requires: Proxy running on localhost:51711 (or `$PROXY_PORT`)

## Global Flags

- `-p, --port <PORT>` — HTTP port (default 51711, reads `$PROXY_PORT`)
- `-f, --format json|human` — output format (default json)
- `--host <HOST>` — target host (default 127.0.0.1)

Use `-f human` for readable output. Use default json when parsing responses programmatically.

## Core Workflow: Create a Party Session

This is the primary use case — spin up a multi-agent conversation about a topic.

```bash
# 1. List available teams (teams have pre-assigned agents)
proxy team list -f human

# 2. Create a session with a team (auto-seats all team agents)
proxy party session create --title "Business Model Discussion" --team <TEAM_ID>

# 3. Send a message (triggers full agent round — all seated agents respond)
proxy party session send <SESSION_ID> --content "Analyze this pricing model: ..."

# 4. Read the responses
proxy party session messages <SESSION_ID> -f human

# 5. Continue the conversation
proxy party session send <SESSION_ID> --content "What about per-model margin tiers?"
```

### Creating a session without a team

```bash
# Create empty session
proxy party session create --title "Quick Chat"

# Manually add participants
proxy party session add-participant <SESSION_ID> '{"agent_id":"<AGENT_ID>","role":"participant"}'
```

### Session config (set working directory for all agents)

```bash
proxy party session set-config <SESSION_ID> '{"working_directory":"/path/to/repo"}'

# Per-participant config
proxy party session set-config <SESSION_ID> <PARTICIPANT_ID> '{"working_directory":"/other/path"}'
```

### Format override (change conversation style per-message)

```bash
# List available formats
proxy party format list -f human

# Send with specific format
proxy party session send <SESSION_ID> --content "Debate this" --format-id debate
```

## Commands Reference

### Party (sessions, messages, search)

```bash
proxy party session list [--limit N] [--include-archived]
proxy party session create [--title TEXT] [--team TEAM_ID] [--json '{}']
proxy party session get <ID>
proxy party session update <ID> '{"title":"New Title"}'
proxy party session delete <ID>
proxy party session participants <ID>
proxy party session add-participant <ID> '{"agent_id":"...","role":"participant"}'
proxy party session remove-participant <SESSION_ID> <PARTICIPANT_ID>
proxy party session set-config <ID> [PARTICIPANT_ID] '{"working_directory":"..."}'
proxy party session messages <ID> [--limit N]
proxy party session send <ID> --content "message" [--format-id FORMAT]
proxy party search --query "text" [--limit N]
proxy party format list
proxy party format roles <FORMAT_ID>
```

### Teams

```bash
proxy team list
proxy team get <ID>
proxy team create '{"name":"Research","format_id":"swarm","mode":"parallel"}'
proxy team update <ID> '{"name":"New Name"}'
proxy team delete <ID>
proxy team assign add <TEAM_ID> '{"role":"participant","agent_id":"...","position":0}'
proxy team assign remove <ASSIGNMENT_ID>
proxy team assign update-config <ASSIGNMENT_ID> '{"working_directory":"/path"}'
proxy team roles <FORMAT_ID>
```

### Agents

```bash
proxy agent list
proxy agent get <ID>
proxy agent create '{"name":"...","model_family_id":"...","system_prompt":"..."}'
proxy agent update <ID> '{"name":"..."}'
proxy agent delete <ID>
proxy agent sync          # sync from remote registry
proxy agent reset         # force-reset to registry defaults
proxy agent defaults list [--scope party]
proxy agent defaults set '{"agent_id":"...","scope":"party"}'
proxy agent defaults remove <ID>
```

### Models

```bash
proxy model list [--provider X] [--family X] [--embedding]
proxy model get <ID>
proxy model family list [--party-only]
proxy model family set-variant <FAMILY_ID> <VARIANT_ID>
proxy model family set-slot <FAMILY_ID> [SLOT]
proxy model resolve <IDENTIFIER>
proxy model provider list [--category X]
proxy model provider get <ID>
proxy model provider access-modes <PROVIDER_ID>
proxy model provider set-access-mode <PROVIDER_ID> <MODE_ID>
proxy model target list / create / update / delete
```

### Providers (API keys)

```bash
proxy provider list
proxy provider key set <PROVIDER> <KEY>
proxy provider key remove / status / test <PROVIDER>
```

### Harnesses (Claude Code, Codex, OpenCode)

```bash
proxy harness list / status
proxy harness configure / unconfigure <ID>
proxy harness connect / disconnect <ID>
proxy harness set-path <ID> <PATH>
proxy harness run <ID> -- <ARGS>
proxy harness discover <ID>
proxy harness config <ID>
proxy harness config-set <ID> <KEY> <VALUE>
proxy harness schema <ID>
proxy harness tunnel get / set / clear
```

### Integrations (MCP servers)

```bash
proxy integration list [--connected]
proxy integration get / add / remove <ID>
proxy integration connect stdio <ID> '{"command":"...","args":["--stdio"]}'
proxy integration connect http <ID> '{"url":"..."}'
proxy integration disconnect <ID>
proxy integration tools <ID>
proxy integration import          # import from Claude Desktop config
proxy integration registry search / refresh / install
proxy integration key set / delete
```

### Loadouts & Skills

```bash
proxy loadout list / create / delete / activate / tuning
proxy loadout skill list / equip / unequip
proxy loadout integration list / equip / unequip
proxy skill source list / add / remove
proxy skill defaults
```

### Config & System

```bash
proxy config list / get <KEY> / set <KEY> <VALUE>
proxy config gc get / update
proxy system health
proxy system snapshot create / list / restore
proxy system orchard status / start / stop
proxy system navigate widget / party / attic
proxy screenshot [--output path.png]
```

## Tips

- **Always check `proxy system health` first** if commands fail — Proxy may not be running.
- **`--team` on session create is the fast path** — it auto-seats all assigned agents.
- **`send` triggers a full agent round** — all participants respond. This is async; poll `messages` to see responses.
- **JSON payloads must be valid JSON objects** — use single quotes around the JSON to avoid shell escaping issues.
- **Port differs in worktrees** — worktree slot N uses port 51711+N. Check `$PROXY_PORT`.
