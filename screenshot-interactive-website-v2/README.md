# Screenshot Interactive — production website

Static HTML/CSS/JS site. No build step at runtime. Deploys to any static host (Netlify recommended).

## Deploy in 5 minutes (Netlify, recommended)

1. Make a Netlify account (free) at https://app.netlify.com/signup.
2. Click "Add new site" → "Deploy manually".
3. Drag this entire `site/` folder onto the upload area.
4. Done. Netlify gives you a temporary URL like `screenshot-interactive.netlify.app`.

### Custom domain (point screenshotinteractive.com here)

1. In Netlify: Site settings → Domain management → "Add custom domain".
2. Type `screenshotinteractive.com` and `www.screenshotinteractive.com`.
3. Update your DNS at your registrar to point to Netlify's nameservers (Netlify shows you which).
4. Netlify auto-issues an SSL certificate. Site goes live on the real domain.

### Forms

The contact form uses Netlify Forms. Already wired in. As soon as the site is on Netlify, form submissions appear in your Netlify dashboard → Forms tab. You'll get an email per submission. **Free up to 100 submissions/month.**

To change the email destination: Site settings → Forms → Form notifications.

## Updating content (events, Social Cine' tickets)

Edit `data/content.json`. Toggle `isLive: true` on a Screen Test row when an event is happening — the live banner appears site-wide and the header CTA changes to "🔴 Join the live quiz". Toggle `ticketsOnSale: true` on a Social Cine' edition — the tickets banner appears site-wide.

After editing:
- If you deployed via drag-drop: re-drag the folder onto Netlify.
- If you deployed via git: commit + push, Netlify auto-deploys in ~30 seconds.

Live event takes priority over tickets banner.

## Updating copy or design

All pages are plain HTML in this folder. Open any `.html` file and edit the text directly. The shared header and footer appear in every HTML file — find/replace works across files.

CSS: `assets/styles.css` — change brand colors at the top under `:root`.

JS: `assets/main.js` — only handles banner state and active nav. Most logic is server-rendered HTML.

## Adding more pages

1. Copy any existing page file (e.g. `activations/magic-mirror/index.html`) to a new path.
2. Update the `<title>`, meta description, canonical URL, and the body content.
3. The shared header automatically links to the new page if you add it to the nav (find/replace the nav block across all files).

## File structure

```
site/
├── index.html                  Home
├── activations/
│   ├── index.html              Pillar
│   ├── magic-mirror/index.html
│   ├── 360-video/index.html
│   ├── outdoor-cinema/index.html
│   └── digital-advertising/index.html
├── creators/index.html         Creator Network pillar
├── screen-test/
│   ├── index.html              Pillar
│   ├── players/index.html
│   ├── venues/index.html
│   └── sponsors/index.html
├── play/index.html             Play (embeds quiz subdomain)
├── social-cine/
│   ├── index.html              Pillar
│   ├── schedule/index.html
│   ├── audiences/index.html
│   └── sponsors/index.html
├── work/index.html             Case studies
├── about/index.html
├── contact/index.html
├── 404/index.html
├── assets/
│   ├── styles.css
│   ├── main.js
│   └── favicon.svg
├── data/
│   └── content.json            ← Edit this for banners
├── netlify.toml                Redirects + headers
└── README.md                   This file
```

## Brand spec (in case anyone updates the design)

- Primary: `#0B1F3A` (deep navy)
- Accent: `#FF3B2E` (signal red)
- Off-white: `#F5F4F0`
- Charcoal: `#1A1A1A`
- Headings: Archivo (or Space Grotesk if Archivo isn't loaded)
- Body: Inter
- Both fonts via Google Fonts CDN, no install needed

## Things that are still placeholders

These are marked clearly in the HTML — search for "[Placeholder" or replace with real data:

- Real metrics on case studies (Featured Work tiles, Work page)
- Real testimonials (Home page)
- Real creator roster names + photos (Creator Network page)
- Social Cine' sponsor tier names + benefits (waiting on Slide 10 of the Feb 2026 deck)
- WhatsApp join link (replace the `#` href on Daily WhatsApp Quiz buttons)
- Real photography in heroes (currently using existing Wix CDN images — they'll continue to work but you should replace with high-res new shoots)

## Deploying via git (recommended for ongoing edits)

1. Initialize this folder as a git repo: `git init && git add . && git commit -m "initial site"`
2. Push to a new GitHub repo.
3. In Netlify, "Add new site" → "Import an existing project" → connect GitHub → select the repo.
4. Build command: leave blank. Publish directory: leave blank or `/`.
5. Every `git push` to main auto-deploys in ~30 seconds.

This is the workflow you want long-term — edits are tracked, rollbacks are one click.

---

Built from the redesign plan and HTML mockup in the parent outputs folder. Questions: open the conversation back up.
