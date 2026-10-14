# Sosa Tech Solutions

The public Sosa Tech Solutions website and its reusable brand/content production system.

**Positioning:** connected websites, WhatsApp automation, approval-based AI content, marketing systems, reliable infrastructure, and streaming for small businesses.

**Market:** Miami and South Florida, English and Spanish.

**Tagline:** **We build. You grow.**

## Website

The site is static HTML/CSS/JavaScript with no build step. It includes:

- English and Spanish versions of every page: English (the default) at the current URLs, Spanish at the same path under `/es/` (for example `/es/services/websites/`), each fully rendered in its language and linked with hreflang. See "Languages" below.
- Six outcome-based offers and evidence-backed operational proof.
- Free lead-flow review contact funnel and WhatsApp CTA.
- WhatsApp on every page: floating button (tucked away while it would cover a video's controls), mobile-menu item and page-aware prefill (`[web-<slug>]` tag, EN/ES). Visible buttons say "Message Victor on WhatsApp" / "Escribe a Victor por WhatsApp".
- AI spokesperson videos page (`/services/ai-spokesperson/`) with three example Reels from `assets/site/reels/` (web MP4 + 540x960 WebP poster of ~45-55 KB each, `preload="none"`, never autoplay, every card labeled as AI). The homepage band shows one lazy 360x640 WebP thumbnail per language (English reel in EN, "¿Parezco real?" in ES). Posters and thumbnails are re-encoded on the Radio Mac Studio.
- AI agents page (`/services/agents/`, approved 2026-10-13): two different agents side by side. The 24/7 inquiry agent answers on WhatsApp, Instagram/Facebook messages and the website with approved information, collects the customer's details and alerts the owner when a person is needed (its replies are not reviewed before sending); the content agent drafts posts, captions and AI-presenter videos that the owner approves before anything is scheduled. Content lives in the `agents` offer in `scripts/build_service_pages.py`; the validator checks both agent cards, the related links and that the retired "team reviews it before sending" claim stays gone, also when reworded (a regex over both agents pages and `llms.txt`). The hero lists the two agents with equal styling (`service-journey--equal`).
- Approved starting prices (2026-10-13): one line under the homepage services ("Monthly plans from $500/mo · Websites from $1,500"), "Websites from $1,500" by the closing call to action on `/services/websites/`, and (2026-10-14) the "monthly plans from $500/mo" anchor in the cost sections of the two blog posts on AI agents and AI spokesperson videos. No other page shows prices, and none are in structured data (`PRICE_PAGES` in `scripts/language_checks.py`).
- Client work page (`/work/`, nav item "Work" / "Proyectos"): nine live client sites Victor confirmed he built (2026-10-13), each with a phone screenshot from `assets/site/work/` (600x750 `src` plus 300/900/1200 px `srcset` variants of the same capture; Cafe Travel only 300/780 because its Cloudflare challenge blocks automated recapture; lazy, explicit dimensions), an industry tag, what was built and a "Visit site" link (its screen-reader text names the business and says it opens a new tab, EN/ES), plus six owner-approved testimonials shown verbatim in English and Spanish with name and business only (never as Review/AggregateRating data). The homepage `#proof` section features six of the sites, a link to `/work/` and three of the quotes. Content lives in `scripts/client_work.py`; `scripts/build_work_page.py` renders the page. The `<domain>-desktop.jpg` screenshots are kept for later use and not referenced yet.
- Short contact form (approved 2026-10-13): name and WhatsApp/phone (`name="phone"`, `type=tel`) required; what you need (preselected from `?service=`), message and email optional. It posts to Web3Forms, which emails Victor every field (an empty email is left out of the payload); hidden fields keep `access_key`, `subject`, `from_name`, `botcheck`, `landing_page`, `utm_*` and `language`. Invalid fields get `aria-invalid`, a per-field error in the page language and the browser bubble with the same text; the success panel adds a page-aware WhatsApp button. A required field that holds only spaces is invalid, and the phone needs at least 7 digits (HTML `pattern` plus the same check in `assets/home.js`). The anti-bot 3-second guard never drops a valid form: an early submit waits out the rest in the "Sending…" state. The validator pins the field set, the required fields, the hidden fields (a UUID `access_key`, the same on `/` and `/es/`) and the phone pattern (digits required) on both languages. Test it with `fetch` stubbed in the browser; never submit the live form.
- First-touch UTM capture in the contact form.
- LocalBusiness, Organization, WebSite, and FAQ structured data.
- Accessible colors, visible keyboard focus, and reduced-motion support.
- Blog index and seven bilingual long-form articles. The two newest (2026-10-14: `agente-de-ia-para-whatsapp-en-miami`, `vocero-con-ia-para-negocios`) are long guides with lists, a cited Sources list (`sources.N`), a visible FAQ (keys `faq.N.q` / `faq.N.a`, which also become a FAQPage node next to the BlogPosting in both languages), related links, a comparison table on the WhatsApp post and, on the AI spokesperson post, one AI-labeled example Reel embedded like on `/services/ai-spokesperson/`. A post can set its own BlogPosting `about` topics with an optional `schemaAbout` string in its JSON (`"topic; topic"`); otherwise the site-wide default applies. Meta's WhatsApp pricing changes quarterly (Jan 1, Apr 1, Jul 1, Oct 1): re-check the cost section of the WhatsApp post against https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing after each change.

Run a local preview from the repository root:

```bash
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.

After changing any copy (see "Languages"), service pages, client work (`scripts/client_work.py`), navigation (`scripts/site_navigation.py`) or WhatsApp topics (`scripts/whatsapp_contact.py`), regenerate everything in both languages and validate:

```bash
python3 scripts/build_language_pages.py    # every EN and /es/ page, sitemap.xml, llms.txt (run it twice: the second run changes nothing)
python3 scripts/validate_site.py
```

`scripts/build_public_site.sh` runs `build_language_pages.py --check` first and refuses to build if any generated file is stale, so commit the regenerated pages with the change.

The validator also checks every `<video>` poster and `<source>` file exists and rejects `autoplay`. It enforces the search snippet standard (titles <= 60 characters ending in `| Sosa Tech Solutions`, meta descriptions 140-155 characters, on every English and Spanish page), the full brand name in public HTML, `llms.txt` and `assets/*.js`, that every service and blog page and `/work/` is listed in `sitemap.xml` and `llms.txt`, that the approved testimonials appear verbatim in English on `/work/` and in Spanish on `/es/work/` (and, for the three homepage quotes, on `/` and `/es/` and in `content/i18n/home.json`), never in the other language, that client screenshots are lazy-loaded with explicit dimensions and the `srcset`/`sizes` from `scripts/client_work.py`, that every page with the primary navigation links to `/work/`, that client-site links open in a new tab with `rel="noopener"`, and that no JSON-LD uses review/rating properties or a `Review`/`AggregateRating` type. When adding a page, update both files (the Spanish entries are generated). The language checks (`scripts/language_checks.py`) are listed in "Languages" and in that file's docstring. Service-page titles and descriptions live in the `SEO` and `SEO_ES` maps in `scripts/build_service_pages.py`.

## Languages

One URL, one language. Every public page exists twice: English at its current URL (the default; never redirected) and Spanish at `/es/` + the same path. Both are static HTML in the repository; nothing is translated in the browser, so search engines index the Spanish pages on their own.

- **Where the copy lives.** Services: the `(English, Spanish)` pairs in `scripts/build_service_pages.py` (`OFFERS`, `SEO`, `SEO_ES`); `/work/`: `scripts/build_work_page.py` and `scripts/client_work.py`; navigation labels: `scripts/site_navigation.py`; WhatsApp topics: `scripts/whatsapp_contact.py`. Homepage, blog and legal pages: the English HTML (`index.html`, `blog/`, `privacy-policy/`, `terms/`, `data-deletion/`) holds the structure, and every element with `data-i18n="key"` (or `data-i18n-alt`, `-aria`, `-placeholder`, `-src`, `-value`, `-attr-<attribute>`) takes its text from `content/i18n/home.json`, `content/i18n/blog/<page>.json` or `content/i18n/legal.json`, which keep English and Spanish side by side. The Spanish legal text is `content/i18n/legal/<page>.es.html`. Edit the JSON (both languages), not the text inside a `data-i18n` element: the build rewrites it from the JSON.
- **Generated:** `es/` (21 pages), the English pages' language tags, `sitemap.xml` (42 URLs with `xhtml:link` en/es/x-default alternates) and the `## En español` section of `llms.txt`. `scripts/build_language_pages.py` does all of it; `scripts/site_i18n.py` holds the shared helpers.
- **Every page** has `<html lang>`, a self canonical, reciprocal `hreflang` (en, es, x-default = English), `og:locale` (+ alternate), and internal links to pages of its own language. Spanish pages have Spanish titles, descriptions, JSON-LD (`inLanguage: "es"`; the business stays `https://sosatechsolutions.com/#business`), WhatsApp prefill and contact form (hidden `language` field `es`; English sends `en`).
- **EN/ES switch:** real links to the other version (they work without JavaScript). `assets/whatsapp.js`, loaded on every page, adds the current query (`utm_*`, `service`, ...) and `#hash` and stores the choice under `sosa-language`. Nothing redirects by browser language or stored preference.
- **Old `?lang=es` links** (social posts and Reels) on an English URL: an inline snippet at the top of every English page replaces the visit with the Spanish twin, keeping the other parameters and the hash. It is client-side on purpose: production has no `.htaccess` and the deploy rsync (`--delete`) would own the whole file, a syntax error there takes the site down with a 500, and it cannot be tested locally. A server 301 can be added later after checking the production `.htaccess`.
- **Validator language rules** (beyond twins and hreflang): absolute `https://sosatechsolutions.com/...` links count as internal (page language and target must exist); no link carries `?lang=`; a stop-word heuristic fails any visible text, title or description that reads as the other language (brand, tagline and client names excepted) and any Spanish slot in the sources left identical to an English sentence; the English tagline is `lang="en"` on Spanish pages; FAQPage questions **and answers** match the visible `<details>` and carry the page `inLanguage` (the English homepage FAQPage is generated from `home.json` too); `robots.txt` may not block `/`, `/es/` or any sitemap URL for search crawlers; every sitemap URL is in `llms.txt`; an invalid `sitemap.xml` is reported, not a traceback.
- **Blog dates:** BlogPosting stays without `datePublished`/`dateModified` (Victor's blog date policy in `BLOG_HANDOFF.md`).
- **New page:** add the English page (and its JSON keys), add its `<url>` to `sitemap.xml`, run the build; the validator fails until the Spanish twin, hreflang, sitemap and `llms.txt` entries all exist.

### New Spanish strings (2026-10-13, for Victor's approval)

Spanish written for this branch where no Spanish existed before or where the old Spanish changed (everything else is the previous Spanish, unchanged):

- Homepage: `form.emailPh` "tu@tunegocio.com"; `seo.ogTitle` "Sosa Tech Solutions | No pierdas al próximo cliente." (from the old hero title); `form.namePh` "Tu nombre completo"; `form.phonePh` "Tu número de WhatsApp"; `contact.lead` "Cuéntame cómo manejas las consultas hoy. Te responderé dentro de un día hábil para coordinar la revisión." (was "gestionas" / "en un día laborable"); `form.successMessage` "Te responderé dentro de un día hábil."; specialist card "Agentes de IA e integraciones" / "Un agente responde a tus clientes 24/7 con información aprobada; otro prepara publicaciones y videos que apruebas."; form option "Agentes de IA e integraciones".
- Form (7d893e8): labels, "Mensaje (opcional)", "Correo (opcional)", errors "Escribe tu nombre.", "Escribe un número de WhatsApp o de teléfono.", "Revisa el correo o déjalo en blanco.", "No pudimos enviar el mensaje. Intenta de nuevo o escríbenos por WhatsApp.", and the success WhatsApp button.
- Blog: aria label "Artículos del blog"; tag "Desarrollo web · SEO · Miami" (was the English "Web Development · SEO · Miami").
- Legal: aria labels "Navegación de páginas legales", "Enlaces legales"; titles and descriptions in `content/i18n/legal.json`; sentence case for "Política de privacidad", "Términos de servicio", "Instrucciones para eliminar datos", "Solicitud de eliminación de datos", "Solicitud de privacidad", "Legal y privacidad"; the privacy policy's domain link now points to `/es/`.
- Services: "EVIDENCIA OPERATIVA" (OPERATING PROOF), "PRINCIPIO DE CONSTRUCCIÓN" (BUILD PRINCIPLE), "puntos de control" (was the English "checkpoints"); agents page (f196c95, approved) with "la fecha o la cotización que pide/pidió" (was "presupuesto") and "y recibes la confirmación cuando está publicado".
- Blog (2026-10-14): the two new posts' Spanish copy is the approved draft text; written for the page around it: eyebrows "Agentes de IA · WhatsApp · Atención al cliente" and "Video con IA · Reels · Marketing honesto", "Preguntas frecuentes", "Sigue leyendo", "Fuentes", the closing cards "Conoce los dos agentes de IA" / "Conoce los videos con vocero de IA" (with their descriptions and buttons "Ver agentes de IA e integraciones →" / "Ver videos con vocero de IA →"), the Reel caption "Presentadores generados con IA" / "¿Parezco real?: cuatro presentadores con IA (en español)", and the homepage blog cards "Un agente de IA para tu WhatsApp" and "Vocero con IA, con honestidad" (they replace the AI-automation and WhatsApp-automation cards; the website card stays). The vocero meta description was shortened to fit 140-155 characters: "Videos con vocero de IA para negocios en Miami: cuándo te conviene un presentador con IA, cuándo no y qué piden Meta, la FTC y las leyes estatales."
- English copy changed with them: placeholders "Your full name" / "Your WhatsApp number"; specialist card "AI agents & integrations" / "One agent answers your customers 24/7 with approved information; another drafts posts and videos you approve."; agents card "…, and you get a confirmation when it’s live."

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
index.html                       Homepage (English; structure for es/index.html)
blog/                            SEO articles (English)
work/                            Client work page (generated)
es/                              Spanish version of every page (generated, committed)
content/i18n/                    English/Spanish copy of the homepage, blog and legal pages
privacy-policy/                  Privacy policy
data-deletion/                   Meta user-data deletion instructions
terms/                           Terms of service
assets/                          Approved site/logo assets
brand/                           Brand source of truth
content/                         Calendar, copy, and launch assets
tools/                           Deterministic visual renderers
scripts/                         Content and PDF build utilities
output/pdf/                      Final brand documents
robots.txt                       Crawler policy (opts out of AI training crawlers only)
llms.txt                         Plain-language site summary for AI answer engines
sitemap.xml                      Public URL inventory, both languages (generated)
```

## Tracking status

The homepage records `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, and the landing URL with each form inquiry. Meta Pixel is intentionally disabled because no verified Dataset/Pixel is currently assigned to the Sosa Tech Solutions business. Do not add a placeholder ID or reuse another client's data source.

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
