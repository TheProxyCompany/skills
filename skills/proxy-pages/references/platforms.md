# Link previews, platform by platform

What each consumer reads, the image limits that actually bite, and how it
fetches. Numbers are from platform docs where they exist (Meta, X archive,
LinkedIn help, Apple TN3156 / Tech Talk 205, Bluesky lexicon, Slack robots
page) and from repeatable 2024-2026 tests otherwise. "Sender-side" means the
device that shares the link fetches the page and embeds the card; the
receiver never fetches.

## The one image that works everywhere

- 1200 x 630 px, JPEG, sRGB, baseline, no transparency, **300 KB or less**
  (target 120-220 KB). 1200x630 is Meta's number, clears LinkedIn's 1200x627
  minimum, Apple's >= 900 px, X's 300x157, WhatsApp's >= 300 px and <= 4:1,
  and is exactly Bluesky's crop box. The byte ceiling is WhatsApp: its doc
  says under 600 KB and images between 300 and 600 KB are dropped often
  enough in practice that 300 KB is the safe line. Bluesky re-encodes over
  1,000,000 bytes, X and LinkedIn cap at 5 MB, Facebook at 8 MB, Apple at
  10 MB for all subresources together.
- One `og:image` only. Every consumer takes the first; a second (square)
  image is ignored or, on iMessage, can flip which set of tags wins.
- Absolute `https://` URL, direct 200, `Content-Type: image/jpeg`, no
  redirect, no auth, no `Content-Disposition: attachment`. A query string is
  fine and is how you bust crawler caches after a republish (X and Meta cache
  the image by URL for about 7 and 30 days).
- Put text you need on the image: X shows only the image and the domain.
  Keep the subject inside the central 60% (Teams and Instagram stories crop
  toward square).

## Tags, in the order the publisher emits them

| Tag | Who needs it |
| --- | --- |
| `<title>` | iMessage fallback, Mastodon (refuses a page without a title), search |
| `<meta name="description">` | fallback description everywhere |
| `<link rel="canonical">` | Facebook object identity, search |
| `<meta name="theme-color">` | Discord embed colour |
| `og:type`, `og:url` | WhatsApp requires `og:url` non-empty and undecorated |
| `og:title` | everyone; iMessage wants no branding here (use `og:site_name`) |
| `og:description` | WhatsApp requires it; X, Slack, Discord, Telegram, LinkedIn show it |
| `og:site_name` | Discord, Slack, Telegram, iMessage |
| `og:locale` | Meta recommends |
| `og:image` + `:secure_url` + `:type` + `:width` + `:height` + `:alt` | width/height let Meta render on the first share instead of async; Discord/Slack use them for large-vs-thumbnail |
| `twitter:card=summary_large_image` | X, and (community) Discord and Telegram choose the large layout from it; without it X shows the small square card |
| `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt` | X; Slack fallback |
| `<link rel="icon">`, `<link rel="apple-touch-icon">` | iMessage, Slack, Discord, Notion show the site icon; otherwise they probe `/apple-touch-icon.png` and `/favicon.ico` at the site root |

Tags must be in the raw HTML `<head>`, near the top: WhatsApp reads the
first 300 KB, Meta 512 KB-1 MB (it sends `Range: bytes=0-524287`; answer 200
with the whole document or a 206 that contains the head, never 416), Slack a
small range (~32 KB reported), Apple caps the document at 1 MB. Nobody runs
JavaScript.

## Fetchers

| Consumer | User-Agent | Notes |
| --- | --- | --- |
| iMessage / Mail / Notes (LinkPresentation) | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0`; images via `com.apple.WebKit.Networking` | sender-side, from the sender's own IP; link must be the whole message or at its start/end, one link per message |
| X | `Twitterbot/1.0`, AS13414 | honours robots.txt; caches ~7 days |
| Facebook, Instagram DM, Messenger, Threads | `facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)`, `meta-externalagent/1.1`, `Facebot` | gzip/deflate only; fetches images asynchronously unless width/height are given; re-scrape via Sharing Debugger or Graph API `?scrape=true` |
| WhatsApp | `WhatsApp/2.x.y.z A|I|N` | sender-side on the phone, ~10 s budget for page + image |
| Signal | `WhatsApp/2` (deliberately) | sender-side |
| Slack | `Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)`, images via `Slack-ImgProxy` | same URL not unfurled twice in an hour per channel; oEmbed discovery overrides OG |
| Discord | `Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)`; image proxy may use a Firefox UA | robots.txt Disallow kills the embed; cache ~30 min |
| Telegram | `TelegramBot (like TwitterBot)` | caches until told otherwise: send the URL to @WebpageBot to refresh |
| LinkedIn | `LinkedInBot/1.0` | cache ~7 days; Post Inspector refreshes |
| Bluesky | `Mozilla/5.0 (compatible; Bluesky Cardyb/1.1; +mailto:support@bsky.app)` | public extractor: `https://cardyb.bsky.app/v1/extract?url=<urlencoded>` |
| Mastodon | `Mastodon/4.x (+https://instance/)` | needs HTTP 200 and `text/html` |
| Teams / Skype | `SkypeUriPreview Preview/0.5` | center-crops toward square |

## Serving rules that break previews

- A bot challenge (Cloudflare Bot Fight Mode, WAF managed challenge, Under
  Attack) is scraped and cached as the card ("Just a moment..."). Verified
  bots pass; a spoofed UA from a residential IP (iMessage!) does not if the
  zone challenges "definitely automated" traffic.
- A 503 or maintenance page with a real `<title>` gets cached as the card
  (Meta ~30 days, X ~7, Telegram indefinitely). An offline page must carry
  no OG tags, a neutral title, `noindex`, `Cache-Control: no-store` and
  `Retry-After`.
- Relative or `http://` image URLs, a redirect on the image, a wrong
  `Content-Type`, brotli-only encoding for Meta, HTTP/2-only origins.
- Meta expects an AAAA record after a hostname change; Cloudflare-proxied
  hosts have one.
- On Cloudflare, `s-maxage` disables `stale-while-revalidate` and
  `stale-if-error`; a zone-level Browser Cache TTL can override `max-age`
  (jckwind.proxy.ing currently rewrites to `max-age=14400`).
