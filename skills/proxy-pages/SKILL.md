---
name: proxy-pages
description: "Publish an HTML page or Artifact bundle to a proxy.ing address as a shareable link whose preview card (title, painting, icon) renders on iMessage, X, Instagram, WhatsApp, Slack, Discord, Telegram, LinkedIn, Bluesky and the rest. Use when asked to share, publish or host a page, report, artifact or site on proxy.ing, or to make a link preview look right."
---

# Proxy Pages

A page is served from the user's own Macs at
`https://<username>.proxy.ing/p/<slug>/`. Proxy copies the bundle into
`<data root>/pages/<slug>/`, rewrites the head with link-preview tags,
produces the preview image, and replicates the finished bundle to every Mac
paired to the account: the proxy.ing edge serves it from whichever of those
Macs it reaches, byte-identical, and keeps a durable copy so the link, its
image and its assets keep working while every laptop sleeps. Publish and
`remove` from any of them; a replica lands within seconds on a live mesh
link (worst case one 60 s tick when the fetch succeeds first time; a failed
fetch retries with backoff up to 10 min, see `references/verify.md`
section 6; a Mac that is offline lands it when it next syncs).

```
https://<username>.proxy.ing/p/<slug>/          index.html
https://<username>.proxy.ing/p/<slug>/<path>    any asset in the bundle
https://<username>.proxy.ing/p/<slug>/og.jpg    preview image (1200x630, <= 300 KB)
https://<username>.proxy.ing/p/                 index of published pages
```

`<username>` is the device's proxy.ing username. `<slug>` matches
`^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$`.

## The whole job

Publishing is the last step. A page people will share needs, in order:

1. **A bundle that stands on its own.** A directory with `index.html` plus
   relative assets, or a single `.html`. Artifact-style files (body-only
   markup with `<title>` and `<style>` at the top) are wrapped into a full
   document on publish. Asset paths must be relative (`fonts/x.woff2`, not
   `/fonts/x.woff2`). Fonts that came from a Google Fonts link keep working;
   any other font must ship in the bundle. Pages are served with a CSP
   sandbox (opaque origin): no localStorage, no cookies.
2. **A painting, not a screenshot.** Generate an original image for the page
   with the newest image model, in the aspect ratios you will use:
   `proxy image generate "<prompt>" --size 1536x1024 --quality high -o landscape.png`
   (also `1024x1536` for the phone hero, `1024x1024` for a square icon).
   Prompt shape that works: an oil painting, edge to edge, no frame, no
   border, no text, photorealistic brushwork, depicting the abstract ideas
   of the page as concrete things (an unfinished arch under scaffolding,
   a lit workshop, a mapped terrain, a walker with a lantern). Look at it.
3. **The card: title on the image.** Compose `scripts/og-card.html` (painting,
   bottom scrim, eyebrow, the title in the page's display face, a short rule)
   and render it with `scripts/render-card.sh card.html og.png` to exactly
   1200x630. X shows only the image and the domain, so the title has to be
   in the picture. Keep the subject in the central 60%. Use the same
   composition as the page's hero so the card and the page match.
4. **An icon.** `icon.png` at the bundle root, square, 512 px, cut from the
   painting or the brand mark. Without it, iMessage, Slack and Discord show
   the site's root favicon.
5. **The hero.** Put the painting full-bleed at the top of the page with the
   same overlay (portrait crop for narrow viewports via `<picture>`), and
   drop the duplicate title from the masthead.
6. **Review the whole page**, not the hero: desktop light and dark, and a real
   phone width (headless Chrome will not go below 500 px; wrap the page in a
   390 px iframe). Charts and tables go in an `overflow-x: auto` box with a
   minimum width; SVGs carry a `viewBox` and no fixed `width`/`height`;
   labels must fit their gutter. `scripts/overflow-probe.js` lists anything
   wider than the viewport. Never force a light background on `<body>` from
   the wrapper: the page renders in the viewer's theme.
7. **Publish, verify, send.** Below.

## Publish

`proxy` is the installed app's CLI (`~/.local/bin/proxy`), talking to the
running Proxy app.

```bash
proxy page publish <PATH> --slug <slug> --title "<title>" \
  [--description "<one or two sentences, <= 300 chars>"] \
  [--og-image /abs/path/og.png] [--username <u>] [--no-warm] [--json]

proxy page list [--json]
proxy page remove <slug>
```

- `--og-image` takes a PNG or JPEG of exactly 1200x630. The publisher stores
  it as `og.jpg` under 300 KB (re-encoding with `sips` when needed) and
  links it as `og.jpg?v=<hash>` so crawlers that cache images by URL (X
  ~7 days, Meta ~30) refetch after a republish. Without `--og-image` it
  renders a plain typographic card. Bundle files named `og.png` are just
  assets.
- `icon.png` in the bundle root (a square PNG, 180 px or more) becomes
  `<link rel="icon">` and `<link rel="apple-touch-icon">` when the
  document has no icon link of its own. A bundle that links its own
  favicon / touch-icon set keeps every one of those links, and `icon.png`
  is then just an asset (still reported as `icon_url`).
- Title <= 120 chars, description <= 300, bundle <= 64 MiB, 16 MiB per
  file; files over 8 MiB get no durable edge copy.
- After publishing, the CLI fetches the page, `og.jpg` and `icon.png`
  through the public edge (warming the cache and the durable copy, and
  clearing the 60 s cold marker an app restart leaves); `--no-warm` skips
  it. Publishing the same slug again replaces the bundle. Every page
  response names the bundle it came from in `x-proxy-pages-version`; a warm
  answered by a Mac that has not landed this publish yet is reported as a
  warning (`still serving an older version`), not as warmed: the edge stored
  that older copy and refreshes it within 5 min once the mesh lands the
  publish there.
- The publish prints `version: <8 hex>` (the sha256 of the bundle's
  `page.json`). That is what the mesh replicates: the last publish of a slug
  wins on every Mac, including a publish made from another Mac, and the
  loser's bundle is replaced without further warning.
- `proxy page list` prints six tab-separated columns: `slug`, `url`,
  `title`, `published_at`, `source` (`origin` on the Mac that published the
  page, `replica` elsewhere) and `state` (`live` once this Mac serves the
  bytes the mesh record describes, `pending` while it is still landing them,
  `unrecorded` for a bundle with no mesh record). A missing field prints
  `-`. `--json` carries the same fields plus `version` and `origin_device`.
- `proxy page remove <slug>` works from any paired Mac and withdraws the
  page from all of them.

Head tags the publisher owns and rewrites on every publish: title,
description, canonical, `og:*` (type, url, title, description, site_name,
locale, image + secure_url/type/width/height/alt) and `twitter:*` (card,
title, description, image, image:alt). Two are added only when the head has
none of its own and are otherwise left untouched: `theme-color` (Deep
Green `#024645`, the Discord embed edge) and the icon links for `icon.png`.
Anything else in a full document's head is kept.
`references/platforms.md` says which platform reads which.

## Verify before you share

`references/verify.md` has the commands. Minimum:

```bash
URL="https://<username>.proxy.ing/p/<slug>/"
curl -sS -A "Twitterbot/1.0" "$URL" | grep -o '<meta [^>]*\(og:\|twitter:\)[^>]*>'
curl -sSI "${URL}og.jpg" | grep -i '^HTTP\|content-type\|content-length\|x-proxy-pages'
curl -sS "https://cardyb.bsky.app/v1/extract?url=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$URL")"
```

Expect 200s, `image/jpeg` under 307,200 bytes, and cardyb returning the
title and an image. For iMessage, `scripts/lp-preview.swift` renders the
card exactly as Messages will draw it, with no message sent. With more than
one Mac paired, section 6 of `references/verify.md` checks that every Mac
has landed the page and serves the same bytes.

## Sending the link on iMessage

A link sent by script (AppleScript, Shortcuts, a Messages MCP) arrives as
plain text and shows "Tap to Load Preview". Messages embeds the card on the
**sender's** device only when the link is typed into the compose field. To
send a link that previews automatically, type it (UI scripting on an
unlocked Mac; wait ~9 s after typing for the fetch; then Return), send the
link as the whole message, one link per message. `references/verify.md`
has the script and how to confirm the payload was embedded.

## Cache and durability

- `Cache-Control: public, max-age=300, s-maxage=300` from the device; the
  edge keeps a copy per POP for 5 min and a durable KV copy for 30 days,
  refreshed on every origin fetch. A 503 `x-proxy-pages: offline` means no
  Mac is reachable and no durable copy exists yet; a 60 s cold window
  follows an app restart. Warm after publishing.
- Replication window: the edge walks the account's Macs in priority order
  and takes the first one that answers. A Mac that has not landed a slug yet
  answers 404 and the walk moves on to the next Mac (a 404 from one Mac
  never evicts the durable copy while another Mac is cold or has not
  answered). On a republish, a Mac that has not landed the new version
  still answers 200 with its previous bytes (`x-proxy-pages-version` names
  the old bundle); the walk stops there and the edge stores that copy for
  up to 5 min (KV until the next origin fetch). The publish warm reports
  this as `still serving an older version`. `x-proxy-pages-device` on every
  response names the Mac that answered. Within seconds on a live link
  (worst case one 60 s tick when the fetch succeeds first time; a failed
  fetch retries with backoff up to 10 min, see verify.md section 6), every
  Mac serves the same bytes; `proxy page list` shows `pending` until then.
- Unpublish: `proxy page remove` withdraws the page from every Mac (the
  removal replicates like a publish). Each Mac that has seen the removal
  answers 404 with `x-proxy-pages-state: removed`, and the next fetch of
  each path through a live Mac then evicts its edge and KV copies, even
  while another Mac is cold. A removed page stays in KV while any routable
  Mac is cold unless a live Mac answers that `removed` 404; a POP that has
  not re-fetched keeps its edge copy for up to 5 min. Do not publish
  secrets: everything under `/p/` is public.
- The mesh record is the truth about what is published. Deleting or
  renaming `~/Proxy/pages/<slug>` by hand is undone by the mesh, which
  re-materializes the bundle from the record and its content store; use
  `proxy page remove`. A hand edit to a file inside that directory is
  neither replicated nor noticed (only `page.json` is compared with the
  record), so that one Mac silently serves different bytes: edit the source
  and republish.
- Crawlers cache cards by URL. Republishing changes `og.jpg?v=`; the page
  URL itself stays cached on X (~7 days), Meta (Sharing Debugger refreshes),
  Telegram (@WebpageBot refreshes), Slack (an hour per channel).

## Traps

- Query strings are ignored and paths are case-exact (`Index.html` is a 404).
- A slug with uppercase, underscores or a leading hyphen is rejected.
- Scripts in an Artifact bundle you did not write still run in every
  viewer's browser.
- The page dir under `<data root>/pages/` is owned by the mesh: a deletion
  is undone, a hand edit is not replicated. Edit the source and republish,
  or `proxy page remove`.
- A Mac running with `PROXY_MESH_PARTY_AUTHORS=none` (or one that does not
  trust the publishing Mac) never lands pages from the others; its own
  publishes still replicate outward.
- Replication needs a proxy.ing username on the Mac (`proxy ing` pairing);
  without one the Mac lands nothing and never rebuilds its `/p/` listing
  (`proxy page list` still shows the rows, `pending` forever).
- Headless Chrome 152's `--screenshot` never exits; `scripts/render-card.sh`
  waits for the PNG to stop growing and kills it.
