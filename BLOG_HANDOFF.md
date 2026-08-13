# Sosa Tech Solutions Blog Handoff

Date: 2026-05-16
Repo: `/Users/victormsosa/Repos/sosa-tech-solutions-new`

## What changed

Added a blog section to the static Sosa Tech Solutions site:

- Blog landing page:
  - `/blog/index.html`
  - Local URL: `http://10.0.0.250:8080/blog/`
  - Production URL: `https://sosatechsolutions.com/blog/`

- Blog posts:
  - `/blog/como-la-inteligencia-artificial-puede-automatizar-tu-negocio-en-miami/index.html`
  - `/blog/automatizacion-de-whatsapp-para-negocios-en-miami/index.html`
  - `/blog/por-que-tu-negocio-en-miami-necesita-un-sitio-web-rapido-y-movil/index.html`
  - `/blog/facebook-ads-vs-google-ads-para-negocios-locales/index.html`
  - `/blog/que-es-n8n-y-como-puede-automatizar-tu-negocio/index.html`

- Updated homepage navigation/footer plus homepage blog preview section:
  - `index.html` links to `/blog/`
  - Added `#latest-insights` section before Contact.

- Updated sitemap:
  - `sitemap.xml` includes `/blog/` and all blog post URLs.

## Language behavior

The blog landing page and blog post both have EN/ES toggle buttons.

- Default language is English.
- Spanish is available via the `ES` button.
- Language choice is saved in `localStorage` as `sosaLang`.
- If a browser previously selected Spanish, it may keep showing Spanish until EN is selected or site data is cleared.

## Blog date policy

Victor does not want dates on blog pages/posts. The article byline should stay as `Sosa Tech Solutions` only. Blog footers should not include a copyright year. Do not add visible publish dates unless explicitly requested.

## SEO details

The blog post includes:

- SEO title and description
- Keywords targeting:
  - artificial intelligence / inteligencia artificial
  - business automation / automatización de negocios
  - Miami
  - small businesses / pequeñas empresas
  - customer service / atención al cliente
  - marketing
  - sales / ventas
  - processes / procesos
- Open Graph metadata
- Twitter card metadata
- JSON-LD `BlogPosting` schema without `datePublished` / `dateModified` fields

The blog landing page includes:

- SEO title and description
- Open Graph metadata
- Twitter card metadata
- JSON-LD `Blog` schema

## Current git status notes

Expected changed/new files from this task:

- `index.html` modified
- `sitemap.xml` modified
- `blog/index.html` new
- `blog/como-la-inteligencia-artificial-puede-automatizar-tu-negocio-en-miami/index.html` new
- `blog/automatizacion-de-whatsapp-para-negocios-en-miami/index.html` new
- `blog/por-que-tu-negocio-en-miami-necesita-un-sitio-web-rapido-y-movil/index.html` new
- `blog/facebook-ads-vs-google-ads-para-negocios-locales/index.html` new
- `blog/que-es-n8n-y-como-puede-automatizar-tu-negocio/index.html` new
- `BLOG_HANDOFF.md` new

Existing unrelated untracked file left untouched:

- `block-blast.html`

Before committing, review whether `block-blast.html` should be committed, ignored, or removed.

## Local preview server

Server was started from:

```bash
cd /Users/victormsosa/Repos/sosa-tech-solutions-new
python3 -m http.server 8080 --bind 0.0.0.0
```

Phone/local Wi-Fi preview URL:

```text
http://10.0.0.250:8080/
```

If the IP changes later, run:

```bash
ipconfig getifaddr en0 || ipconfig getifaddr en1
```

## Quick validation commands

```bash
cd /Users/victormsosa/Repos/sosa-tech-solutions-new

git status --short

python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
class P(HTMLParser): pass
for p in [Path('blog/index.html'), Path('blog/como-la-inteligencia-artificial-puede-automatizar-tu-negocio-en-miami/index.html')]:
    P().feed(p.read_text())
    print(p, 'HTML parse OK')
PY

grep -RIn "data-lang-btn\|function setLang\|How artificial intelligence\|Cómo la inteligencia artificial\|/blog/" blog index.html sitemap.xml
```

## Suggested next Codex prompt

```text
Continue work in /Users/victormsosa/Repos/sosa-tech-solutions-new.
Read BLOG_HANDOFF.md first.
Review the blog landing page and article added under /blog/.
Keep default language English with EN/ES toggle.
Improve the design/content if needed while preserving the static HTML structure.
Do not touch block-blast.html unless explicitly asked.
Run the validation commands from BLOG_HANDOFF.md before finishing.
```
