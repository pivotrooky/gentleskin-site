# gentleskin.app

The Gentleskin website: a home page and guides that send people to the iOS app.
Static HTML, no framework. Colors and fonts from the app (`shared/tokens.toml`,
Castoro + Albert Sans).

- Edit `content/*.html` (header block, `---`, body), then `python3 build.py`.
  It writes each page's `index.html`, `sitemap.xml`, `robots.txt`, `llms.txt`.
- `{{store}}` in content becomes the App Store link with a campaign token
  (`ct=web` home, `ct=web_guide` guides, `ct=web_nav` the top bar), so App
  Store Connect shows installs from the site.
- Preview: `python3 -m http.server 8765`.
- Hosting: GitHub Pages from this repo, custom domain `gentleskin.app` (`CNAME`), DNS at Cloudflare (DNS only, not proxied).
