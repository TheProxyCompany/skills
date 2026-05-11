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
