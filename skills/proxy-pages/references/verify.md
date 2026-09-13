# Verifying a page's preview

Run these from any Mac after publishing. `URL` is the page, with the
trailing slash.

## 1. Tags and image, as the crawlers see them

```bash
URL="https://<username>.proxy.ing/p/<slug>/"
for ua in "Twitterbot/1.0" \
  "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)" \
  "WhatsApp/2.23.20.0 A" \
  "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)" \
  "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)" \
  "TelegramBot (like TwitterBot)" "LinkedInBot/1.0" \
  "Mozilla/5.0 (compatible; Bluesky Cardyb/1.1; +mailto:support@bsky.app)" \
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.4 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.4 facebookexternalhit/1.1 Facebot Twitterbot/1.0"; do
  printf '%-40.40s ' "$ua"
  curl -sS -m 20 -A "$ua" -o /tmp/p.html -w '%{http_code} ' "$URL"
  grep -c 'property="og:image"' /tmp/p.html
done
# Meta's range fetch must still contain the head
curl -sS --compressed -H 'Range: bytes=0-524288' -A 'facebookexternalhit/1.1' "$URL" | grep -c 'og:image'
# the image: 200, image/jpeg, under 300 KB, no redirect
IMG=$(grep -o 'property="og:image" content="[^"]*"' /tmp/p.html | head -1 | cut -d'"' -f4)
curl -sSI -m 20 "$IMG" | grep -i '^HTTP\|content-type\|content-length\|x-proxy-pages'
```

Every UA must get 200 and the same tags. `x-proxy-pages` is `origin` on the
first fetch and `edge-hit` afterwards; `offline` means the Mac is
unreachable and no durable copy exists yet (open the URL once while the app
is running).

## 2. Third-party extractors (what a platform actually built)

```bash
curl -sS "https://cardyb.bsky.app/v1/extract?url=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$URL")"
curl -sS "https://api.microlink.io/?url=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1],safe=""))' "$URL")" | head -c 800
```

Bluesky's `cardyb` is the exact service its app uses. LinkedIn's Post
Inspector (`https://www.linkedin.com/post-inspector/inspect/<urlencoded>`)
and Facebook's Sharing Debugger need a login but also refresh their caches.
Telegram: message the URL to `@WebpageBot`.

## 3. iMessage, without sending anything

`scripts/lp-preview.swift` fetches the URL through Apple's LinkPresentation
(the same code path Messages uses) and renders the card to a PNG:

```bash
swiftc -O -o /tmp/lp-preview scripts/lp-preview.swift
/tmp/lp-preview "$URL" /tmp/card.png   # prints title, hasImage, hasIcon
```

## 4. iMessage, for real

A link sent by script (AppleScript, Shortcuts, the Messages MCP) goes out
as plain text; the receiver sees "Tap to Load Preview". Previews are
embedded by the *sender's* Messages when the link is typed into the compose
field. To send one that previews automatically, type it: on an unlocked Mac
with Messages open on the conversation,

```applescript
tell application "Messages" to activate
delay 1.5
tell application "System Events" to tell process "Messages"
  keystroke "https://<username>.proxy.ing/p/<slug>/"
  delay 9   -- LinkPresentation fetches the card before you press return
  keystroke return
end tell
```

Confirm in a read-only copy of `~/Library/Messages/chat.db` that the row has
`balloon_bundle_id = com.apple.messages.URLBalloonProvider`; then screenshot
Messages (Proxy's `/mcp/computer` `screenshot` tool works on a Mac whose
screen is unlocked; `screencapture` over SSH does not).

## 5. The page itself

Look at the whole page, not the hero: desktop light and dark, and a real
phone width. Headless Chrome will not open a window narrower than 500 px;
wrap the page in a 390 px iframe or use device emulation. Run
`scripts/overflow-probe.js` to list anything wider than the viewport.
Charts and tables belong inside an `overflow-x: auto` box with a minimum
width; SVGs should carry a `viewBox` and no fixed `width`/`height`.
