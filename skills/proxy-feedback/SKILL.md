---
name: proxy-feedback
description: >
  Diagnose and submit useful product feedback to The Proxy Company. Use when a
  user reports broken, confusing, slow, or missing Proxy behavior and wants the
  issue sent to the team with concrete reproduction steps and relevant logs.
---

# Proxy Feedback

Turn the user's experience into a concise diagnostic report. Submit only when
the user asks you to send feedback or approves the report.

## Build The Report

1. State the observed behavior and the expected behavior separately.
2. Record the shortest reliable reproduction steps.
3. Run `proxy system health` and preserve relevant failures verbatim.
4. Use the returned `data_dir` to inspect `logs/glue.log` and, when needed,
   `logs/glue.log.prev`.
5. Include only the shortest log excerpt that establishes the failure.

Remove API keys, tokens, credentials, private message content, and unrelated
user data. Do not attach a complete log file.

## Submit

Prefer the built-in `proxy_submit_feedback` MCP tool. Provide:

- `summary`: a short concrete title.
- `details`: observed behavior, expected behavior, and impact.
- `category`: `bug`, `usability`, `feature`, `performance`, or `other`.
- `reproduction`: concise steps when known.
- `log_excerpt`: an optional relevant, redacted excerpt.

If the MCP tool is unavailable, use the same fields with the CLI:

```bash
proxy feedback submit \
  --summary "Private-thread gear does not open" \
  --details "Observed: clicking the gear does nothing. Expected: Agent, Schedule, and Jobs tabs open." \
  --category bug \
  --reproduction "Open a private thread, then click the gear."
```

Proxy automatically attaches the authenticated device identity, Proxy and
Grand Central versions, platform, and available agent context. Return the
`feedback_id` to the user after a successful submission. Preserve the service
error verbatim when submission fails.

