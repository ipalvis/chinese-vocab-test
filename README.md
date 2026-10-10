# 词汇量 Chinese Vocabulary Test: Cloudflare Pages kit

A static website: one self-contained page plus a few small files. There's no server code, database or build step on Cloudflare's side.

```
public/            ← what Cloudflare serves (the "build output directory")
  index.html         the test (word list and handwriting data built in, about 2.6 MB)
  _headers           security and caching headers for Cloudflare Pages
  favicon.svg        browser-tab icon
  robots.txt         lets search engines index the site
src/               ← how index.html is made (only needed when you change the test)
  template.html      the page source, with __BANK__ / __GLYPHS__ placeholders
  assemble.py        template + data → chinese-vocab-test.html
  deploy.py          chinese-vocab-test.html → public/index.html (adds the full <head>)
  build.py, enrich.py, glyphs.py, overrides.json   data pipeline (see "Rebuilding")
  data/bank2.json    the word bank (built)
  data/glyphs.json   handwriting reference shapes (built)
```

## Before you start

You need a free [GitHub](https://github.com/signup) account and a free [Cloudflare](https://dash.cloudflare.com/sign-up) account. A domain name is optional; without one, the site lives at `your-project.pages.dev`.

## Step 1: Put the kit on GitHub

1. Go to [github.com/new](https://github.com/new).
2. Name the repository (for example `chinese-vocab-test`). Public or Private both work.
3. Leave "Add a README" unchecked, then select **Create repository**.
4. On the empty repository page, select **uploading an existing file**.
5. Unzip this kit on your computer. Drag in **everything inside** the unzipped folder: `public`, `src`, `README.md` and `.gitignore`. Drag their contents, not the outer folder itself.
6. Select **Commit changes**.

If you use git on the command line instead:

```bash
cd chinese-vocab-test        # the unzipped kit
git init && git add . && git commit -m "First version"
git branch -M main
git remote add origin https://github.com/<you>/chinese-vocab-test.git
git push -u origin main
```

## Step 2: Create the Cloudflare Pages project (connected to GitHub)

Connecting to GitHub means every later change you push to GitHub goes live automatically, and you can roll back to an earlier version with one click.

1. Sign in at [dash.cloudflare.com](https://dash.cloudflare.com) and open **Workers & Pages**.
2. Select **Create application**, then the **Pages** tab, then **Connect to Git**.
3. Sign in with GitHub when asked. Allow Cloudflare to access the repository from Step 1, then select **Install & Authorize**.
4. Pick the repository and select **Begin setup**.
5. Fill in **Set up builds and deployments**:

   | Field | Value |
   | --- | --- |
   | Project name | e.g. `cihuiliang`; this becomes `cihuiliang.pages.dev` |
   | Production branch | `main` |
   | Framework preset | **None** |
   | Build command | *leave blank* |
   | Build output directory | `public` |
   | Root directory (advanced) | *leave blank* |

6. Select **Save and Deploy**. After about a minute you get a link like `https://cihuiliang.pages.dev`. The site is live.

> Don't use "Upload assets" (drag-and-drop) if you might want automatic deploys later. Cloudflare can't switch a drag-and-drop project to GitHub afterwards; you'd have to create a new project.

## Step 3: Check the live site

Open the `.pages.dev` link on a laptop and on a phone, and check:

- [ ] The home page shows the 简体/繁體 toggle, the four tests and the credits at the bottom.
- [ ] **Reading:** answers move on after the 3-second bar.
- [ ] **Listening:** the sound check plays a voice. If the card says "No Mandarin voice in this browser", try Chrome, Edge or Safari, or add a Chinese voice in your system settings.
- [ ] **Writing:** the squares read your handwriting and the chime and buzzer play.
- [ ] **Combined:** it runs all three sections and shows the three-skill results page.

## Step 4 (optional): Use your own domain

The cheapest route is buying the domain from Cloudflare (sold at cost, about $10–11/year for a .com), so DNS and HTTPS set themselves up.

1. In the dashboard, open **Domain Registration**, then **Register Domains**, and buy the name.
2. Go to **Workers & Pages**, open your project, then **Custom domains**, then **Set up a domain**. Enter `yourdomain.com` and select **Continue**, then **Activate domain**.
3. Repeat for `www.yourdomain.com` if you want both addresses to work.
4. HTTPS certificates are issued automatically, usually within a few minutes.

If the domain is registered elsewhere:

- **Subdomain** (e.g. `test.yourdomain.com`): add it under **Custom domains** first. Then, at your DNS provider, add a `CNAME` record pointing `test` to `cihuiliang.pages.dev`. Add it in Cloudflare *before* creating the CNAME, or you'll see a 522 error.
- **Root domain** (`yourdomain.com`): this must be a Cloudflare zone. In Cloudflare, add the domain as a site, then change the nameservers at your registrar to the two Cloudflare gives you. After that, add it under **Custom domains**.

## Updating the site later

1. Make the change (or have Claude make it), then rebuild `public/index.html` (see "Rebuilding").
2. Upload or commit the changed files to GitHub. On GitHub's web page, open the `public` folder, select **Add file**, then **Upload files**, and drop in the new `index.html`.
3. Cloudflare redeploys automatically in about a minute.
4. Every deploy is kept. To undo a bad update, go to **Workers & Pages**, open your project, then **Deployments**. On an older deployment, open the **…** menu and select **Rollback to this deployment**.

Pushes to other branches get their own preview link (`<branch>.cihuiliang.pages.dev`), so you can test a change before it goes live.

## Rebuilding index.html

The data files in `src/data` are already built, so a normal change to the page only needs Python 3:

```bash
python3 src/assemble.py src/template.html src/data/bank2.json src/data/glyphs.json chinese-vocab-test.html
python3 src/deploy.py chinese-vocab-test.html public/index.html
```

Changing the word list itself means re-running the full pipeline. That needs `pip install wordfreq ToJyutping`, plus the source downloads: `cedict-json` (npm) and `hanzi-writer-data` (npm).

```bash
python3 src/build.py cedict.json bank.json src/overrides.json
python3 src/enrich.py bank.json cedict.json hanzi-writer-data/ src/data/bank2.json strokes.json
python3 src/glyphs.py hanzi-writer-data/ src/data/glyphs.json
```

## What it costs

- **Hosting:** Cloudflare Pages free plan, $0. Static pages have unlimited bandwidth and requests, so a traffic spike can't pause the site or bill you. Limits are 500 deploys a month and 25 MB per file; `index.html` is about 2.6 MB.
- **Domain:** optional, about $10–11/year.

## Licences and credits

The word data is adapted from CC-CEDICT (CC BY-SA 4.0) and wordfreq (data CC BY-SA 4.0), so the word list is shared under CC BY-SA 4.0. The handwriting shapes come from Make Me a Hanzi (Arphic Public License), and Cantonese readings from ToJyutping (BSD 2-Clause). These credits are shown at the bottom of the home and results pages; keep them there.
