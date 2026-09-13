---
name: proxy-pages
description: "Publish an HTML page or Artifact bundle to a proxy.ing address as a shareable link whose preview card (title, painting, icon) renders on iMessage, X, Instagram, WhatsApp, Slack, Discord, Telegram, LinkedIn, Bluesky and the rest. Use when asked to share, publish or host a page, report, artifact or site on proxy.ing, to make a link preview look right, or to change who can see a page."
---

# Proxy Pages

**The folder is the interface.** A page is whatever is in
`~/Proxy/pages/<slug>/`. Write `index.html` there and the running Proxy app
records it, replicates it to every Mac paired to the account, and serves it
at `https://<username>.proxy.ing/p/<slug>/`. There is no command to run;
`proxy page publish` exists as a convenience and does exactly this.

```
~/Proxy/pages/<slug>/
  index.html          yours. Plus any assets, relative paths (fonts/x.woff2).
  page.yaml           yours, optional: visibility, title, description.
  og.png | og.jpg     yours, optional: the 1200x630 preview image.
  icon.png            yours, optional: square PNG >= 180 px, the tab/card icon.
  page.json           Proxy's status file. Never edit. Appears within ~2 s.
  page.error.txt      Proxy's, only when the folder cannot publish. Says why.
```

Proxy never rewrites your files. The link-preview head tags (title,
description, canonical, `og:*`, `twitter:*`, and the icon links when the
document has none) are injected as `index.html` is served, from
`page.json`, so the bytes on disk stay yours and an edit is just an edit.

## Visibility: who can see it

Set in `page.yaml`:

```yaml
visibility: link     # draft | link | public
```

- `draft` — only the owner. Served on their own Macs (`http://127.0.0.1:51711/p/<slug>/`),
  never through the edge (the public URL 404s). **What a new folder starts as.**
- `link` — anyone with the URL. Unlisted, `noindex`. This is what "publish" or
  "share" means: the artifact / Google-Doc "anyone with the link" level.
- `public` — listed on `https://<username>.proxy.ing/p/` and indexable.

A folder that already has a recorded page keeps its visibility until
`page.yaml` says otherwise. **Never raise a page's visibility unless the
person asked for it**; a draft is theirs until they say "publish" or
"share". Lowering it back to `draft` withdraws it from the edge on the
next request.

`page.yaml` may also carry `title:` and `description:` (<= 300 chars),
which override the document's `<title>` and `<meta name="description">`.
Without them the document's own are used; without those, the slug.

## The whole job

Publishing is the last step. A page people will share needs, in order:

1. **A bundle that stands on its own.** `index.html` plus relative assets.
   Artifact-style files (body-only markup with `<title>` and `<style>` at
   the top) are wrapped into a full document as they are served. Asset paths
   must be relative (`fonts/x.woff2`, not `/fonts/x.woff2`). Fonts that
   came from a Google Fonts link keep working; any other font must ship in
   the folder. Pages are served with a CSP sandbox (opaque origin): no
   localStorage, no cookies. File names: letters, digits, `.`, `_`, `-`
   only (no spaces); no symlinks; 16 MiB per file, 64 MiB per page.
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
   1200x630, then put it in the folder as `og.png`. X shows only the image
   and the domain, so the title has to be in the picture. Keep the subject
   in the central 60%. Use the same composition as the page's hero so the
   card and the page match. Without an `og.png`/`og.jpg`, Proxy renders a
   plain typographic card from the title (and re-renders it when the title
   changes); a page worth sharing deserves the painting.
4. **An icon.** `icon.png` at the folder root, square, 512 px, cut from the
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
7. **Write the folder, set the visibility, read `page.json`, verify.** Below.

## Publish

Write the files, then write `page.yaml`. Order matters only in that a folder
with no `index.html` is not a page yet (Proxy waits), so the visibility is
best written last:

```bash
SLUG=my-report; DIR=~/Proxy/pages/$SLUG
mkdir -p "$DIR"
cp -R build/. "$DIR"/                       # index.html, assets, og.png, icon.png
printf 'visibility: link\n' > "$DIR/page.yaml"

# ~2 s later page.json is the receipt: url, version, visibility, warnings.
until [ -f "$DIR/page.json" ] || [ -f "$DIR/page.error.txt" ]; do sleep 1; done
cat "$DIR/page.error.txt" 2>/dev/null
jq -r '.url, .visibility, .version[0:8], (.warnings[]? // empty)' "$DIR/page.json"
```

- Edit any file and save: a new version replicates within seconds. A
  visibility change is a version too.
- Delete the folder (while Proxy is running) and the page is unpublished
  from every Mac about 5 s later. Deleting it while Proxy is off does
  nothing: the mesh record is truth and the folder is rebuilt at boot; use
  `proxy page remove <slug>` then.
- `page.error.txt` names the one problem stopping the publish (a file name
  with a space, a symlink, a file over the limit, a bad `page.yaml`). Fix it
  and save; the file disappears when the page publishes.
- `page.json` -> `warnings` says what Proxy could not do: the preview card
  could not be rendered, an `icon.png` that is not a square PNG >= 180 px,
  an `og.jpg` it could not bring under 300 KB.
- The same slug written on two Macs: last writer wins, on every Mac. Pick a
  slug that is not in `proxy page list` when starting a new page.
- Pages published before visibility existed read as `public`; a
  `page.yaml` with `visibility:` changes that.

The CLI does the same thing with a copy:

```bash
proxy page publish <PATH> --slug <slug> --title "<title>" \
  [--description "<one or two sentences, <= 300 chars>"] \
  [--og-image /abs/path/og.png] [--visibility draft|link|public] \
  [--username <u>] [--no-warm] [--json]
proxy page list [--json]        # slug url title published_at visibility source state
proxy page remove <slug>
```

`publish` copies `PATH` into the folder, writes `page.yaml` from the flags
(visibility defaults to `public` here, because the command is called
publish), makes `--og-image` the folder's `og.jpg`, then fetches the page,
`og.jpg` and `icon.png` through the public edge so the copies exist before
anyone shares the link (`--no-warm` skips it; a warm answered by a Mac that
has not landed this version yet is reported as `still serving an older
version`). `list --json` also carries `version`, `origin_device`,
`local_dir` and `error` (the folder's `page.error.txt`, if any).

Limits: title <= 120 chars, description <= 300, folder <= 64 MiB, 16 MiB
per file; files over 8 MiB get no durable edge copy. `og.jpg` is always
served as a JPEG under 300 KB (re-encoded with `sips` when needed) and
linked as `og.jpg?v=<hash>` so crawlers that cache images by URL (X ~7
days, Meta ~30) refetch after a republish. `references/platforms.md` says
which platform reads which tag.

## Verify before you share

`references/verify.md` has the commands. Minimum, once `page.yaml` says
`link` or `public`:

```bash
URL="https://<username>.proxy.ing/p/<slug>/"
curl -sS -A "Twitterbot/1.0" "$URL" | grep -o '<meta [^>]*\(og:\|twitter:\)[^>]*>'
curl -sSI "${URL}og.jpg" | grep -i '^HTTP\|content-type\|content-length\|x-proxy-pages'
curl -sS "https://cardyb.bsky.app/v1/extract?url=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$URL")"
```

Expect 200s, `image/jpeg` under 307,200 bytes, and cardyb returning the
title and an image. A `link` page answers with `X-Robots-Tag: noindex`; a
`draft` answers 404 with `x-proxy-pages-state: draft` (check it locally at
`http://127.0.0.1:51711/p/<slug>/` instead). For iMessage,
`scripts/lp-preview.swift` renders the card exactly as Messages will draw
it, with no message sent. With more than one Mac paired, section 6 of
`references/verify.md` checks that every Mac has landed the page and
serves the same bytes.

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
  follows an app restart.
- Replication: the edge walks the account's Macs in priority order and
  takes the first one that answers. A Mac that has not landed a slug yet
  answers 404 and the walk moves on (a 404 from one Mac never evicts the
  durable copy while another Mac is cold or has not answered). On a
  republish, a Mac that has not landed the new version still answers 200
  with its previous bytes (`x-proxy-pages-version` names the old one); the
  edge stores that copy for up to 5 min. `x-proxy-pages-device` on every
  response names the Mac that answered. Within seconds on a live link
  (worst case one 60 s tick; a failed fetch retries with backoff up to
  10 min, see verify.md section 6), every Mac serves the same bytes;
  `proxy page list` shows `pending` until then.
- Unpublish (folder deleted, `visibility: draft`, or `proxy page remove`):
  every Mac that has seen it answers 404 with `x-proxy-pages-state:
  removed` (or `draft`), and the next fetch through a live Mac evicts the
  edge and KV copies, even while another Mac is cold. A POP that has not
  re-fetched keeps its edge copy for up to 5 min. Do not put secrets in a
  page: `link` and `public` pages are readable by anyone who has the URL.
- Crawlers cache cards by URL. Republishing changes `og.jpg?v=`; the page
  URL itself stays cached on X (~7 days), Meta (Sharing Debugger refreshes),
  Telegram (@WebpageBot refreshes), Slack (an hour per channel).

## Traps

- Query strings are ignored and paths are case-exact (`Index.html` is a 404).
- A slug with uppercase, underscores, spaces or a leading hyphen is not a
  page folder at all: Proxy ignores it. Rename it.
- Proxy's own transient files in the folder are dot-prefixed (`.og-render.png`,
  `.page.json.tmp`); never ship dotfiles yourself, they are not served.
- Scripts in an Artifact bundle you did not write still run in every
  viewer's browser.
- A Mac running with `PROXY_MESH_PARTY_AUTHORS=none` (or one that does not
  trust the publishing Mac) never lands pages from the others; its own
  publishes still replicate outward.
- Replication needs a proxy.ing username on the Mac (`proxy ing` pairing);
  without one a folder gets `page.error.txt: no proxy.ing username
  configured on this Mac`.
- Headless Chrome 152's `--screenshot` never exits; `scripts/render-card.sh`
  waits for the PNG to stop growing and kills it.
