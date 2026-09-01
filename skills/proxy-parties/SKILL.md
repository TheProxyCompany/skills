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
`party.yaml` manifest, a `playbook.md` (the kickoff text posted at every
firing), `roles/*.md` prompts, and optional loadouts, output schemas, hooks,
and a worksite block. The scheduler fires the definition on its cron; each
firing seats the team into a fresh or rolling session. The canonical field
reference for `party.yaml` is
`grand-central/docs/party/manifest.md` — read it before hand-authoring a
folder. Note: `goal:` is the deprecated spelling of `playbook:`; write
`playbook:`.

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
proxy party session send <SESSION_ID> --text "Review the launch plan." -f human
```

Inspect formats:

```bash
proxy party format list -f human
proxy party format roles <FORMAT_ID> -f human
```

Fire a standing party definition now:

```bash
proxy party fire <DEFINITION_ID>
proxy party session create --definition <DEFINITION_ID>
```

Standing-party definitions also have an HTTP surface on the local instance
(grand-central, `/cli/party/definitions`): `GET /definitions` (list),
`GET /definitions/{id}?files=true` (manifest plus folder files),
`PUT /definitions/{id}` (write), `DELETE /definitions/{id}`,
`POST /definitions/validate` (dry-run a folder write),
`POST /definitions/{id}/fire`, `POST /definitions/{id}/seat` (seat without a
kickoff), `POST /definitions/{id}/rollover`, `POST /definitions/reimport`,
and `GET /definitions/next-fire?cron=<EXPR>` (next fire time in the
instance's timezone). Where the `proxy party definition ...` verbs are
available they wrap these routes one-to-one.

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
