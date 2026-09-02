---
name: proxy-parties
description: >
  Work with Proxy Parties: multi-agent conversations, source chats, rosters,
  participants, messages, formats, and party sessions. Use when creating a
  Party, selecting agents, sending messages, inspecting conversation history,
  opening the source chat behind a Move, or debugging Party behavior through the
  Proxy CLI or product UI.
---

# Proxy Parties

A Party is a conversation space where the user and agents work together. Parties
can have moderators, participants, formats, tools, attachments, source chats,
and Moves that emerge from the discussion.

## Product Model

- A Party session is the conversation container.
- Participants are users or agents seated in the session.
- Formats define roles and turn structure.
- Messages are the durable chat history.
- Moves can be authored from Party context and should link back to their source
  chat when possible.

## Standing vs Session Parties

A session is one live conversation. A standing party is a durable,
schedulable definition: a folder at `$PROXY_DATA_ROOT/parties/<id>/` with a
`party.yaml` manifest, `roles/*.md` prompts, an optional `playbook.md` (the
kickoff text posted at every firing), and optional loadouts, output schemas,
hooks, and a worksite block. The scheduler fires the definition on its cron;
each firing seats the team into a fresh or rolling session. The field
reference for `party.yaml` is the `PartyManifest` struct in
`grand-central/src/party/standing.rs`; the built-in folders under
`grand-central/src/party/parties/` are working examples. Read them before
hand-authoring a folder. The manifest rejects unknown keys.

## CLI Workflow

Use `proxy-cli` when you need direct command-line control.

List sessions:

```bash
proxy party session list -f human
```

Create a session:

```bash
proxy party session create --title "Planning session" -f human
```

Inspect a session:

```bash
proxy party session get <SESSION_ID> -f human
proxy party session participants <SESSION_ID> -f human
proxy party session messages <SESSION_ID> --limit 50 -f human
```

Send a user message:

```bash
proxy party session send <SESSION_ID> --content "Review the launch plan." -f human
```

Inspect formats:

```bash
proxy party format list -f human
proxy party format roles <FORMAT_ID> -f human
```

Standing party definitions:

```bash
proxy party definition list -f human        # id, name, device, cron, enabled, next fire, last fire, source
proxy party definition get <DEFINITION_ID> -f human
proxy party definition enable <DEFINITION_ID>
proxy party definition disable <DEFINITION_ID>
proxy party definition fire <DEFINITION_ID>     # same as: proxy party fire <DEFINITION_ID>
proxy party definition rollover <DEFINITION_ID>
proxy party devices -f human                # mesh devices a manifest `device:` can name
proxy party save <SESSION_ID>               # write a live session as a standing party folder
```

`enable` and `disable` set `schedule.enabled` in the folder's `party.yaml`.
The instance's file watcher re-imports the folder, and the command waits for
the row to follow. Run them on the Proxy host. They refuse registry-managed
(`cdn`) folders and mesh replicas, and they need a `schedule:` block with a
`cron:`.

`last_fired_at` is `null` until the definition fires once.

The HTTP routes behind these verbs, on the local instance:

- `GET /client/v1/party/definitions` lists every definition with `next_fire_at`.
- `POST /client/v1/party/definitions/{id}/fire` fires one. A definition that
  targets another device forwards the request there.
- `GET /client/v1/party/devices` lists mesh devices.
- `POST /client/v1/party/{conversation_id}/save` saves a live session as a folder.
- `POST /cli/party/definitions/{id}/rollover` closes the current season and
  opens the next.

No HTTP route writes or deletes a definition folder. The folder is the source
of truth: edit `party.yaml` (or use the Parties editor in the app) and the file
watcher re-imports it.

## Operating Rules

- Preserve exact Party titles when reporting or debugging.
- Do not create duplicate sessions if an existing source Party already fits.
- When a Move came from a Party, prefer opening or linking the source Party
  instead of creating a detached side conversation.
- Attachments are part of the message context; verify they render in both the
  source Party and any derived Move.
- If a Party has multiple agents, identify which participant authored the
  relevant message or Move.

## Debug Pattern

When a Party flow looks wrong:

1. List sessions and find the exact Party title.
2. Inspect participants.
3. Inspect recent messages.
4. Compare UI state against CLI/API state.
5. Preserve the exact visible title, message preview, attachment label, and
   error text.

## Related Skills

- Use `proxy-moves` when Party work produces an approval proposal.
- Use `proxy-cli` for the full command surface.
