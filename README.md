# Sosa Tech Solutions

The public Sosa Tech Solutions website and its reusable brand/content production system.

**Positioning:** connected websites, WhatsApp automation, AI workflows, marketing systems, reliable infrastructure, and streaming for small businesses.

**Market:** Miami and South Florida, English and Spanish.

**Tagline:** **We build. You grow.**

## Website

The site is static HTML/CSS/JavaScript with no build step. It includes:

- Bilingual English/Spanish homepage and legal pages.
- Five outcome-based offers and evidence-backed operational proof.
- Free systems-review contact funnel and WhatsApp CTA.
- First-touch UTM capture in the contact form.
- LocalBusiness, Organization, WebSite, and FAQ structured data.
- Accessible colors, visible keyboard focus, and reduced-motion support.
- Blog index and five bilingual long-form articles.

Run a local preview from the repository root:

```bash
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.

## Brand system

- `brand/BRAND_GUIDELINES.md` - complete source-of-truth manual.
- `brand/brand-tokens.json` - machine-readable colors, type, sizes, and generation rules.
- `.agents/brand-context.md` - concise context for future AI-assisted production.
- `output/pdf/SOSA_TECH_BRAND_GUIDELINES_V1.pdf` - rendered manual.
- `output/pdf/SOSA_TECH_BRAND_QUICK_REFERENCE_V1.pdf` - one-page production reference.

Rebuild the PDFs:

```bash
python3 scripts/build_brand_pdfs.py
```

## Content system

- `BRAND_CONTENT_GROWTH_PLAN.md` - 90-day brand, website, SEO, and social roadmap.
- `content/calendar.csv` - 30-day publishing calendar.
- `content/launch/LAUNCH_CONTENT_PACK_01.md` - captions, scripts, shot lists, and CTAs.
- `content/assets/social/` - final feed, profile, cover, highlight, and reel exports.
- `content/assets/kie-sources/` - generated source illustrations and provenance metadata.
- `tools/social-studio/` - deterministic carousel renderer.
- `tools/brand-assets/` - profile, Facebook cover, and highlight renderer.
- `tools/reel-studio/` - bilingual vertical-video scene renderer.

Build the six launch Reels from the approved WAV voiceovers in `content/audio/voiceovers/`:

```bash
bash scripts/build_reels.sh
```

Generate a new Kie visual source from a server-side credential:

```bash
KIE_API_KEY='...' python3 scripts/kie_generate_brand_sources.py \
  --name campaign-source \
  --scene 'Describe the business scene here' \
  --aspect-ratio 4:5
```

Never place API keys, Meta tokens, decrypted n8n credentials, client data, or customer messages in this repository.

This GitHub repository is currently public. The deploy allowlist prevents working files from entering the website document root, but it does not make committed files private on GitHub. Store confidential strategy, customer material, credentials, and private operations only in an approved private repository or secured VPS path.

## Key files

```text
index.html                       Homepage
blog/                            Bilingual SEO articles
privacy-policy/                  Privacy policy
data-deletion/                   Meta user-data deletion instructions
terms/                           Terms of service
assets/                          Approved site/logo assets
brand/                           Brand source of truth
content/                         Calendar, copy, and launch assets
tools/                           Deterministic visual renderers
scripts/                         Content and PDF build utilities
output/pdf/                      Final brand documents
robots.txt                       Crawler policy
sitemap.xml                      Public URL inventory
```

## Tracking status

The homepage records `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, and the landing URL with each form inquiry. Meta Pixel is intentionally disabled because no verified Dataset/Pixel is currently assigned to the Sosa Tech business. Do not add a placeholder ID or reuse another client's data source.

When the correct data source exists, validate PageView, Contact, Lead, and booked-review events before enabling paid traffic. The Meta ad account also requires an account-level review before spend.

## Deployment

- GitHub: `vmsosa86/sosa-tech-solutions`
- Branch: `main`
- Public URL: `https://sosatechsolutions.com/`
- Hostinger source checkout: `/home/u876565679/site-sources/sosa-tech-solutions`
- Hostinger document root: `/home/u876565679/domains/sosatechsolutions.com/public_html`

The repository is not the document root. `deploy/public-files.txt` is the explicit public allowlist, and `scripts/build_public_site.sh` creates the ignored `.deploy/public/` artifact. Brand working files, source illustrations, voiceovers, renderers, plans, and repository metadata never enter the web root.

Deploy an intentional commit from the Hostinger source checkout:

```bash
git pull --ff-only origin main
bash scripts/deploy_hostinger.sh --dry-run
bash scripts/deploy_hostinger.sh --apply
```

The apply step creates a timestamped pre-deploy backup under `/home/u876565679/site-backups/`, then synchronizes only the allowlisted public output. Verify the homepage, legal pages, blog, sitemap, social preview image, public campaign media, and contact/WhatsApp links afterward.

## Contact

- WhatsApp: +1 (305) 741-5702
- Email: info@sosatechsolutions.com
- Facebook: `facebook.com/sosatechsolutions`
- Instagram: `instagram.com/sosatechsolutions`

© 2026 Sosa Tech Solutions · Miami, Florida
