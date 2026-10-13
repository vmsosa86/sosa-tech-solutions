#!/usr/bin/env python3
"""Build every public page in English (current URLs, the default) and Spanish (/es/...).

One command regenerates the whole site from its sources:

- services and /work/ from build_service_pages.py / build_work_page.py (EN + ES);
- the homepage, blog and legal pages from their English HTML (structure) plus the copy in
  content/i18n/ (home.json, blog/<page>.json, legal.json and legal/<page>.es.html);
- the shared WhatsApp contact and navigation (sync_whatsapp_contact.py);
- hreflang, og:locale and the legacy ?lang=es redirect on every page (site_i18n.py);
- sitemap.xml (both languages, with xhtml:link alternates) and the "## En español"
  section of llms.txt.

    python3 scripts/build_language_pages.py           # write
    python3 scripts/build_language_pages.py --check   # exit 1 if any output is stale

Running it twice changes nothing. scripts/build_public_site.sh runs --check before every
deploy build, so stale Spanish pages cannot be published.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Dict, List
import xml.etree.ElementTree as ET

import build_service_pages
import build_work_page
import site_i18n as i18n
import sync_whatsapp_contact as sync
from site_i18n import BUSINESS_ID, SITE, WEBSITE_ID, counterpart, en_path, es_path

ROOT = i18n.ROOT
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"
LLMS_HEADING = "## En español"


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def link_pages() -> set:
    return build_service_pages.link_pages()


def finish(text: str, path: str, lang: str) -> str:
    return i18n.localize_links(i18n.set_head_i18n(text, path, lang), lang, link_pages())


def drop_keywords(text: str) -> str:
    """The English keyword list is not repeated on Spanish pages."""
    return re.sub(r'[ \t]*<meta name="keywords" content="[^"]*"\s*/?>\n?', "", text)


def set_switch(text: str, container: str, path: str, lang: str, attrs: str = "") -> str:
    """Re-render the EN/ES links inside the language group `container` (a class name)."""
    pattern = rf'(<div class="{container}"[^>]*>\s*)((?:<a\b[^>]*data-lang-link[^>]*>[^<]*</a>)+)'
    updated, count = re.subn(pattern, lambda m: m.group(1) + i18n.switch_links(path, lang, attrs), text, count=1)
    if count != 1:
        raise SystemExit(f"{path}: language switch .{container} not found")
    return updated


# --- homepage ------------------------------------------------------------------------------

def home_schema(copy: Dict[str, str]) -> dict:
    """Spanish homepage: the WebPage and its FAQ in Spanish. The business itself is the
    #business node of the English homepage, referenced by @id."""
    url = SITE + "/es/"
    faq = []
    index = 1
    while f"faq.{index}.q" in copy:
        faq.append({"@type": "Question", "name": i18n.text_of(copy[f"faq.{index}.q"]),
                    "acceptedAnswer": {"@type": "Answer", "text": i18n.text_of(copy[f"faq.{index}.a"])}})
        index += 1
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": copy["seo.title"], "description": copy["seo.description"],
             "inLanguage": "es", "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": BUSINESS_ID}},
            {"@type": "FAQPage", "inLanguage": "es", "mainEntity": faq},
        ],
    }


def render_home(text: str, lang: str) -> str:
    copy = i18n.load_json("home.json")[lang]
    text = i18n.set_html_lang(text, lang)
    text = i18n.set_meta(text, copy["seo.title"], copy["seo.description"], copy["seo.ogTitle"])
    text = i18n.i18n_replace(text, copy, f"home ({lang})")
    text = set_switch(text, "lang-switch", "/", lang, 'class="lang-btn"')
    text = sync.sync_home(text, lang, f"index.html ({lang})")
    if lang == "es":
        text = drop_keywords(text)
        text = i18n.set_json_ld(text, home_schema(copy))
    return finish(text, counterpart("/", lang), lang)


# --- blog ----------------------------------------------------------------------------------

BLOG_ABOUT = {"en": ["business automation", "Miami", "small businesses"], "es": ["automatización de negocios", "Miami", "pequeños negocios"]}
BLOG_NAME = {"en": "Sosa Tech Solutions Blog", "es": "Blog de Sosa Tech Solutions"}


def blog_schema(name: str, copy: Dict[str, str], lang: str, path: str) -> dict:
    url = SITE + counterpart(path, lang)
    publisher = {"@type": "Organization", "@id": BUSINESS_ID, "name": "Sosa Tech Solutions", "url": f"{SITE}/"}
    if name == "index":
        return {"@context": "https://schema.org", "@type": "Blog", "name": BLOG_NAME[lang], "url": url, "inLanguage": lang,
                "description": copy["metaDesc"], "publisher": publisher}
    return {
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": i18n.text_of(copy["title"]), "description": copy["metaDesc"],
        "image": f"{SITE}/og-image-2026-10b.png", "author": {"@type": "Organization", "name": "Sosa Tech Solutions"},
        "publisher": {**publisher, "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo-light.png"}},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "inLanguage": lang, "about": BLOG_ABOUT[lang],
    }


def blog_pages() -> List[tuple]:
    pages = [("index", "/blog/", "blog", False)]
    for post in sorted((ROOT / "blog").glob("*/index.html")):
        slug = post.parent.name
        pages.append((slug, f"/blog/{slug}/", f"blog-{slug}", True))
    return pages


def render_blog(text: str, name: str, path: str, slug: str, is_post: bool, lang: str) -> str:
    data = i18n.load_json(f"blog/{name}.json")[lang]
    copy = {**data, **sync.BLOG_CTA[lang]}
    text = i18n.set_html_lang(text, lang)
    text = i18n.set_meta(text, copy["metaTitle"], copy["metaDesc"])
    text = sync.sync_blog(text, slug, is_post, lang, path, f"{path} ({lang})")
    text = i18n.i18n_replace(text, copy, f"{path} ({lang})")
    text = i18n.set_json_ld(text, blog_schema(name, copy, lang, path))
    if lang == "es":
        text = drop_keywords(text)
    return finish(text, counterpart(path, lang), lang)


# --- legal ---------------------------------------------------------------------------------

def render_legal(text: str, page: str, lang: str) -> str:
    path = f"/{page}/"
    copy = i18n.load_json("legal.json")[lang]
    if lang == "es":
        body = (i18n.I18N_DIR / "legal" / f"{page}.es.html").read_text(encoding="utf-8").rstrip("\n")
        text, count = re.subn(r"(<main>\n)[\s\S]*?(\n  </main>)", lambda m: m.group(1) + body + m.group(2), text, count=1)
        if count != 1:
            raise SystemExit(f"{path}: <main> not found")
    text = i18n.set_html_lang(text, lang)
    text = i18n.set_meta(text, copy[f"{page}.title"], copy[f"{page}.description"])
    text = i18n.i18n_replace(text, copy, f"{path} ({lang})")
    text = set_switch(text, "lang-switch", path, lang)
    text = sync.sync_legal(text, page, lang, f"{path} ({lang})")
    return finish(text, counterpart(path, lang), lang)


# --- sitemap and llms.txt ------------------------------------------------------------------

def sitemap(paths: List[str]) -> str:
    """Both languages for every page, each <url> with its en / es / x-default alternates.
    lastmod, changefreq and priority come from the English entry of the current sitemap."""
    existing = {}
    path = ROOT / "sitemap.xml"
    if path.exists():
        ns = {"s": SITEMAP_NS}
        for node in ET.parse(path).findall("s:url", ns):
            loc = node.findtext("s:loc", "", ns).strip()
            existing[loc] = {key: (node.findtext(f"s:{key}", "", ns) or "").strip() for key in ("lastmod", "changefreq", "priority")}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<urlset xmlns="{SITEMAP_NS}" xmlns:xhtml="{XHTML_NS}">']
    for english in paths:
        meta = existing.get(SITE + english)
        if meta is None:
            raise SystemExit(f"sitemap.xml: add {SITE + english} (lastmod, changefreq, priority) before building")
        for page in (english, es_path(english)):
            lines.append("  <url>")
            lines.append(f"    <loc>{SITE + page}</loc>")
            for hreflang, target in (("en", english), ("es", es_path(english)), ("x-default", english)):
                lines.append(f'    <xhtml:link rel="alternate" hreflang="{hreflang}" href="{SITE + target}"/>')
            for key in ("lastmod", "changefreq", "priority"):
                if meta[key]:
                    lines.append(f"    <{key}>{meta[key]}</{key}>")
            lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def llms_section() -> str:
    home = i18n.load_json("home.json")["es"]
    legal = i18n.load_json("legal.json")["es"]
    rows = [f"- [Inicio]({SITE}/es/): {home['seo.description']}"]
    for offer in build_service_pages.OFFERS:
        rows.append(f"- [{offer['name_es']}]({SITE}/es/services/{offer['slug']}/): {offer['seo_description_es']}")
    rows.append(f"- [{build_work_page.COPY['label'][1]}]({SITE}/es/work/): {build_work_page.SEO_ES[1]}")
    for name, path, _, _ in blog_pages():
        copy = i18n.load_json(f"blog/{name}.json")["es"]
        label = "Blog" if name == "index" else i18n.text_of(copy["title"])
        rows.append(f"- [{label}]({SITE}{es_path(path)}): {copy['metaDesc']}")
    for page in i18n.LEGAL_PAGES:
        rows.append(f"- [{legal[f'{page}.title'].replace(' | Sosa Tech Solutions', '')}]({SITE}/es/{page}/)")
    intro = ("Cada página tiene su versión en español bajo /es/, con el mismo contenido que la versión en inglés "
             "(el idioma predeterminado, en las URL sin /es/).")
    return f"{LLMS_HEADING}\n\n{intro}\n\n" + "\n".join(rows) + "\n"


def llms(text: str) -> str:
    """Replace the "## En español" section, or add it before "## Contact"."""
    section = llms_section()
    pattern = re.compile(rf"^{re.escape(LLMS_HEADING)}\n[\s\S]*?(?=^## |\Z)", re.M)
    if pattern.search(text):
        return pattern.sub(lambda _: section + "\n", text, count=1)
    marker = text.index("## Contact")
    return text[:marker] + section + "\n" + text[marker:]


# --- build ---------------------------------------------------------------------------------

def build() -> Dict[str, str]:
    """Every generated file: repository path -> content. Reads sources only."""
    out = dict(build_service_pages.outputs())
    english = render_home(read("index.html"), "en")
    out["index.html"] = english
    out["es/index.html"] = render_home(english, "es")
    for name, path, slug, is_post in blog_pages():
        rel = path.strip("/") + "/index.html"
        english = render_blog(read(rel), name, path, slug, is_post, "en")
        out[rel] = english
        out["es/" + rel] = render_blog(english, name, path, slug, is_post, "es")
    for page in i18n.LEGAL_PAGES:
        rel = f"{page}/index.html"
        english = render_legal(read(rel), page, "en")
        out[rel] = english
        out["es/" + rel] = render_legal(english, page, "es")
    paths = i18n.en_paths(ROOT)
    out["sitemap.xml"] = sitemap(paths)
    out["llms.txt"] = llms(read("llms.txt"))
    return out


def stray_spanish_pages(out: Dict[str, str]) -> List[str]:
    """Pages under es/ that the build does not produce (e.g. a removed English page)."""
    return sorted(str(p.relative_to(ROOT)) for p in (ROOT / "es").glob("**/index.html") if str(p.relative_to(ROOT)) not in out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="do not write; exit 1 if any generated file is stale")
    args = parser.parse_args(argv)
    out = build()
    stale = []
    for rel, text in out.items():
        target = ROOT / rel
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == text:
            continue
        stale.append(rel)
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
    strays = stray_spanish_pages(out)
    if args.check:
        if stale or strays:
            print("LANGUAGE PAGES STALE: run python3 scripts/build_language_pages.py and commit the result")
            for rel in stale:
                print(f"- {rel}")
            for rel in strays:
                print(f"- {rel} (no English source)")
            return 1
        print(f"LANGUAGE PAGES UP TO DATE: {len(out)} files")
        return 0
    for rel in stale:
        print(rel)
    for rel in strays:
        print(f"WARNING {rel}: no English source; delete it")
    print(f"{len(stale)} of {len(out)} files updated")
    return 1 if strays else 0


if __name__ == "__main__":
    raise SystemExit(main())
