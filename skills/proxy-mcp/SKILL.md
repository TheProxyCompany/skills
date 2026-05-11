---
name: proxy-mcp
description: >
  Connect and use Proxy's MCP server from agent clients. Use when configuring
  Proxy as a Streamable HTTP MCP server, setting bearer-token environment
  variables, checking available Proxy tools, or debugging agent access to Proxy
  Life Map, Moves, Parties, local context, and tool surfaces.
---

# Proxy MCP

Proxy exposes a local MCP server so agents can work with the user's Life Map,
Moves, Parties, content, and connected tools.

## Setup Pattern

Use the connection details shown inside Proxy settings. Do not guess or retain
private endpoint/token values.

For agent clients that support Streamable HTTP:

1. Add a custom MCP server named `Proxy`.
2. Select Streamable HTTP transport.
3. Paste the Proxy MCP endpoint from Proxy settings.
4. Store the bearer token in an environment variable such as
   `PROXY_BEARER_TOKEN`.
5. Configure the MCP server to read that environment variable.
6. Save the server and list tools.

Treat bearer tokens, personal keys, and endpoint URLs as secrets.

## Verification

After connecting, verify the tool surface before doing work:

- `proxy_overview` for Life Map overview.
- `proxy_search` for graph search.
- `proxy_list` for structured entity listing.
- `proxy_prioritize` for leverage-ranked work.
- `proxy_create_move`, `proxy_list_moves`, `proxy_get_move`,
  `proxy_update_move`, and `proxy_make_move` for Moves.

If the client can list tools but tool calls fail, check:

- Proxy is running.
- Local access is enabled in Proxy settings.
- The bearer token environment variable is present in the agent process.
- The MCP endpoint matches the active Proxy instance.
- The agent client has permission to use local/network tools.

## Operating Rules

- Explore before writing. Use read tools first when context may already exist.
- Prefer Moves for user-visible proposals instead of silently mutating state.
- Never print bearer tokens or personal keys into chat, logs, commits, or docs.
- Preserve exact tool error messages when reporting failures.
- If multiple Proxy instances are open, verify which one owns the MCP endpoint.

## Related Skills

- Use `life-map` for graph modeling and Life Map edit etiquette.
- Use `proxy-moves` for proposal/review workflows.
- Use `proxy-parties` for conversations and multi-agent sessions.
