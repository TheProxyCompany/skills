---
name: proxy-feedback
description: >
  Diagnose and submit useful product feedback to The Proxy Company. Use when a
  user reports broken, confusing, slow, or missing Proxy behavior and wants the
  issue sent to the team with concrete reproduction steps and relevant logs.
---

# Proxy Feedback

Turn the user's experience into a concise diagnostic report without sanding
away their words. Submit only when the user asks you to send feedback or
approves the report and its screenshot.

## Preserve The Moment

As soon as the user reports a visible Proxy problem:

1. Preserve the user's report exactly as written. This becomes `user_report`;
   do not paraphrase, clean up, or replace it with your diagnosis.
2. Capture the current Proxy window before navigating away:

```bash
proxy screenshot --output /tmp/proxy-feedback.png
```

3. Tell the user a screenshot was captured and will be attached if they
   approve submission. Do not capture the whole desktop or another app.

If Proxy cannot capture its window, preserve the exact error and continue the
diagnosis. Never fabricate or substitute a screenshot.

## Mini Bug Interview

Ask only for details the user has not already supplied. Keep it conversational
and usually limit it to two or three short questions:

- What exact action immediately preceded the problem?
- What did you expect to happen instead?
- Is it repeatable, and roughly when did it happen?

Do not make the user restate information already present in their report.

## Build The Report

1. State the observed behavior and the expected behavior separately.
2. Record the shortest reliable reproduction steps.
3. Run `proxy system health -f json` and preserve relevant failures verbatim.
4. Use the returned `data_dir` to inspect `logs/glue.log` and, when needed,
   `logs/glue.log.prev`.
5. Correlate logs to the reported time and include only the shortest excerpt
   that establishes the failure.

Remove API keys, tokens, credentials, private message content, and unrelated
user data. Do not attach a complete log file.

## Submit

Prefer the built-in `proxy_submit_feedback` MCP tool. Provide:

- `user_report`: the user's report verbatim.
- `summary`: a short concrete title.
- `details`: your diagnosis, observed behavior, expected behavior, impact, and
  the answers from the mini interview.
- `category`: `bug`, `usability`, `feature`, `performance`, or `other`.
- `reproduction`: concise steps when known.
- `log_excerpt`: an optional relevant, redacted excerpt.
- `screenshot_path`: the path returned by `proxy screenshot`.

If the MCP tool is unavailable, use the same fields with the CLI:

```bash
proxy feedback submit \
  --user-report "The gear does nothing when I click it." \
  --summary "Private-thread gear does not open" \
  --details "Observed: clicking the gear does nothing. Expected: Agent, Schedule, and Jobs tabs open." \
  --category bug \
  --reproduction "Open a private thread, then click the gear." \
  --screenshot /tmp/proxy-feedback.png
```

Proxy automatically attaches the authenticated device identity, Proxy and
Grand Central versions, platform, and available agent context. Confirm both
the returned `feedback_id` and whether `screenshot_attached` is true. Preserve
the service error verbatim when submission fails.
