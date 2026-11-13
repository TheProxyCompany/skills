# The Proxy Company Skills

Public agent skills for using Proxy, Orchard, and The Proxy Company developer
tools.

## Skills

- `life-map` - Work with Proxy's user-owned Life Map graph.
- `proxy-cli` - Control a running Proxy instance from the command line.
- `proxy-mcp` - Connect agent clients to Proxy's MCP server.
- `proxy-moves` - Create, revise, and resolve user-reviewed Moves.
- `proxy-pages` - Publish a page to a proxy.ing address with a link preview that renders everywhere.
- `proxy-parties` - Work with multi-agent Party sessions and source chats.

## Validation

GitHub Actions runs the skill contract checks on every pull request. These parse
all skill metadata and the documented party examples, check explicit existing-agent
and loadout bindings, and reject regressions such as roster creation, global
activation, missing equipment, and conflicting model overrides. No Proxy app,
private repository, credentials, or model calls are needed.

```bash
python3 -m pip install -r tests/requirements.txt
python3 -m unittest discover -s tests -v
```

To additionally replay the documented workflow through a real installed Proxy CLI:

```bash
PROXY_CLI=/path/to/proxy-cli python3 -m unittest discover -s tests/integration -v
```

The integration suite uses a loopback HTTP fixture on an ephemeral port; it never
contacts the running Proxy app. It fails if no CLI is available instead of silently
skipping. Hosted checks validate the documentation contract, not real model
execution or a sidecar's interpretation of the instructions.
