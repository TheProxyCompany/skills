---
name: proxy-cli
description: >
  Control a running Proxy instance via the proxy CLI. Use when: running or creating
  party sessions, sending messages to agents, firing standing parties, managing
  agents/loadouts/models, checking system health, configuring harnesses/integrations,
  inspecting Work and workspaces, generating or editing images, generating video,
  or any programmatic interaction with Proxy.
  Triggers: "create a party", "send to proxy", "proxy session", "talk to agents",
  "start a party about X", "fire the party", "proxy model", "proxy harness",
  "proxy config", "proxy work", "proxy image", "proxy video", "generate an image",
  "generate a video".
  Requires Proxy to be running (port 51711 default, or $PROXY_PORT).
---

# Proxy CLI

Binary: `proxy`. `~/.local/bin/proxy` links to the copy inside the installed app bundle (`Proxy.app/Contents/MacOS/proxy-cli`); a worktree build carries its own copy in its bundle. Build only through `Proxy/scripts/dev_cycle.sh`.
Requires: Proxy running on localhost:51711 (or `$PROXY_PORT`).

`proxy --help` and `proxy <group> [<command>] -h` are the source of truth. Below the top level use `-h`: a nested `--help` falls through to the agent shortcut (last section) and errors. This reference was regenerated from the installed binary on 2026-09-02, and the global flags, `party fire`, harness, page, image and video entries were brought up to the CLI source on 2026-09-20; when a command is missing here, `-h` wins.

## Global Flags

- `--port <PORT>` — HTTP port (default 51711, reads `$PROXY_PORT`). Long-only: `-p` is `party fire --prompt`.
- `-f, --format json|human` — output format (default json)
- `--host <HOST>` — target host (default 127.0.0.1)

Use `-f human` for readable output. Use default json when parsing responses programmatically.

## Core Workflow: Run a Party

The fast path seats roster agents by name, posts the prompt, streams the feed to stderr, and prints the transcript when the party goes quiet:

```bash
proxy party run --agents "claude,codex" --name "Pricing review" "Analyze this pricing model: ..."
proxy party run --agents "claude,codex,gemini" --flow 'author -> [reviewer*2] ~> synthesizer' "..."
proxy party run --format-id debate --agents "claude,gemini" --timeout 600 --json "..."
```

`--format-id` takes `forum`, `swarm`, `pair_programming`, or a standing party definition id (default: forum for several agents, swarm for one).

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
proxy party definition fire <ID> [-p TEXT|@FILE|-] [-d DEVICE] [--timeout SECS] [--json]   # fire now and stream to quiescence
proxy party fire <ID> [-p TEXT|@FILE|-] [-d DEVICE] [--timeout SECS] [--json]              # same thing
proxy party definition rollover <ID>      # close the current season, open the next
proxy party devices                       # mesh devices a manifest `device:` can name
proxy party save <SESSION_ID>             # write a live session as a standing party folder
proxy party bench [--definition ID | --conversation ID | --agents NAMES "prompt"] [--rounds N] [--json]
```

`-p/--prompt` is the request this firing carries out (literal text, `@path` to read a file, or `-` for stdin); it is posted as the kickoff ahead of the playbook. `-d/--device` runs this one firing on another mesh device (label, device id, or unique hex prefix) and overrides the manifest's `device:` pin. `--timeout` exits 124 if the party is not quiescent in time.

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

### Harnesses (CLI agent runtimes)

```bash
proxy harness list
proxy harness status <ID>                 # claude-code, codex, opencode, openclaw, gemini-cli, hermes-agent, pi
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

### Images and video

Both run on provider API keys stored with `proxy provider key set <PROVIDER> <KEY>`; `proxy image catalog` and `proxy video catalog` list the providers, their models and defaults, and which have a key.

```bash
proxy image catalog
proxy image generate "<prompt>" [--provider openai|google|fireworks|fal] [--model ID] [--size S] \
  [--quality auto|low|medium|high|xhigh|max] [--background transparent|opaque|auto] \
  [--output-format png|jpeg|webp] [-n N] [-o PATH] [--input '{"seed":7}']
proxy image edit "<prompt>" --image PATH [--provider ID] [--model ID] [--size S] \
  [--output-format png|jpeg|webp] [-n N] [-o PATH] [--input JSON]

proxy video catalog
proxy video generate "<prompt>" [--provider fal|minimax] [--model ID] [--image PATH|URL] [--last-frame PATH|URL] \
  [--duration SECS] [--resolution R] [--aspect W:H] [-o PATH] [--input JSON] [--no-wait] [--timeout SECS]
proxy video status <JOB_ID> [--wait] [--timeout SECS]
proxy video list [--limit N]                     # newest first, default 50
proxy video cancel <JOB_ID>
```

- **Leave a flag off to get the configured default.** `--provider`, `--model`, `--size`, `--duration`, `--resolution` and `--aspect` are sent only when given. Otherwise Proxy uses the `image.provider` / `image.model` / `video.provider` / `video.model` settings (`proxy config set video.provider fal`), then the provider's default model. Built-in providers: images default to `openai`, video to `fal`.
- **Name the provider when a flag depends on it.** Older CLIs always sent `--provider openai`; this one does not. `--model`, `--size`, `--quality` and `--background` without `--provider` go to whatever `image.provider` names, so a model id can reach a provider that does not know it, and `--quality` / `--background` (OpenAI only) and `--size` (ignored by Google and Fireworks) are dropped without an error. When the result depends on one of them, pass `--provider` too, e.g. `--provider openai --size 1536x1024 --quality high`.
- **Model ids are the provider's own.** OpenAI images: `gpt-image-2.5-sunburst` (quality), `gpt-image-2.5-flare` (fast), `gpt-image-2`; `--quality xhigh|max` is GPT Image 2.5 only. fal images: an endpoint id such as `fal-ai/qwen-image-2.1`. Video: a fal endpoint id such as `minimax/h3/text-to-video` (MiniMax H3, 5-15s, 768P or 2K), or `MiniMax-H3` with `--provider minimax` (4-15s; MiniMax H3 needs a pay-as-you-go key). The catalog is the source of truth.
- **`--size`** is `WIDTHxHEIGHT` or `auto` for OpenAI (edges a multiple of 16, at most 3840); for fal a preset such as `square_hd`, or `W:H` on fal models that take an aspect ratio. Google and Fireworks ignore it.
- **`--input`** merges provider-native fields last into the provider request, as a JSON object (fal and minimax). Use it for anything without a flag.
- **`-o`** is a file or a directory, resolved against your shell's working directory. Without it files land in `<data dir>/images/` or `<data dir>/videos/`. With `-f human` stdout is one written path per line. The image JSON is `{provider, model, paths}` plus `size` only when you passed `--size` (older builds always echoed `1024x1024`), so do not rely on the `size` key.
- **`--image` (`image edit`, `video generate`) / `--last-frame`** take a local PNG, JPEG or WEBP of at most 20 MB; for video also an `http(s)://` URL. The CLI reads a local file and Proxy uploads it to the provider; fal uploads are publicly readable by URL. `--last-frame` needs `--image` and a model that takes first and last frames.
- **Video is a job.** `generate` prints `video job <JOB_ID> submitted (...)` on stderr as soon as the provider accepts it (the job is billed from there, per second of output), then waits. Stdout gets only the final job object, or the paths with `-f human`. `--no-wait` returns the queued job at once. After `--timeout` (default 1800s) the CLI exits 124 with the last job on stdout and the job keeps running: resume with `proxy video status <JOB_ID> --wait`. Ctrl-C only stops waiting; `proxy video cancel <JOB_ID>` cancels at the provider, and a job that already started may still be billed.
- **Exit codes:** 0 done; 1 the job failed or was cancelled, or the CLI lost track of it (see below); 2 Proxy refused the request before any job existed (no stored key, a flag the model does not take, the provider rejected the submit, an unknown job id on `status` / `cancel`), so from `video generate` exit 2 always means nothing was created; 124 `--timeout` ran out.
- **Exit 1 does not always mean the job is dead: read stderr before you resubmit.** `video job <id> failed: ...` and `was cancelled` are final. `lost track of video job <id> after 20 failed polls in a row ... the job keeps running` means Proxy kept failing or refusing the status read (an app restart, a busy database) while the billed job carried on: resume with `proxy video status <id> --wait`. `... the video job may have been submitted anyway` means the submit request died in transit (timeout, dropped connection) and the job id never came back: run `proxy video list` and look for it before retrying, or you pay twice.

### Pages (proxy.ing)

```bash
proxy page publish <PATH> --slug <SLUG> --title <TEXT> [--description TEXT] [--og-image IMAGE] \
  [--username U] [--visibility draft|link|public] [--no-warm] [--json]
proxy page list [--json]
proxy page remove <SLUG>                         # removes it from every paired Mac
```

`<PATH>` is one `.html` file or a directory with `index.html`; the page is served at `https://<username>.proxy.ing/p/<slug>/`. The `proxy-pages` skill covers the folder interface and link previews.

### proxy.ing pairing and feedback

```bash
proxy ing pair [--username U] [--no-wait]        # pair this Mac with its proxy.ing address
proxy ing status
proxy ing tunnel refresh [--username U]          # re-fetch this Mac's tunnel and restart cloudflared
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
