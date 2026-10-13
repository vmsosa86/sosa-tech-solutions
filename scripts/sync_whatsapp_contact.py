#!/usr/bin/env python3
"""Apply the shared WhatsApp contact to the hand-authored static pages.

Service pages get the same markup from build_service_pages.py. This script
updates the homepage, blog and legal pages in place and is safe to re-run:

- every link tagged data-wa-slug gets its English prefill and topics from
  whatsapp_contact.TOPICS (assets/whatsapp.js switches them to Spanish);
- blog pages get the shared navigation (with its mobile WhatsApp item), the
  floating button and, on posts, the in-article WhatsApp CTA;
- legal pages get the floating button and per-language prefilled contact links.
"""

import re
from html import escape
from pathlib import Path

import whatsapp_contact as wa
from site_navigation import NAV_CSS_HREF, NAV_JS_SRC, render_navigation

ROOT = Path(__file__).resolve().parents[1]
LEGAL_PAGES = ["privacy-policy", "terms", "data-deletion"]
LEGAL_JS_SRC = "/assets/legal.js?v=20261013a"

BLOG_CTA = {
    "en": {
        "wa.title": "Want this working in your business?",
        "wa.desc": "Send a quick message about how your business handles it today, in English or Spanish.",
        "wa.btn": wa.CTA_EN,
    },
    "es": {
        "wa.title": "¿Quieres que esto funcione en tu negocio?",
        "wa.desc": "Envía un mensaje rápido sobre cómo lo maneja hoy tu negocio, en español o en inglés.",
        "wa.btn": wa.CTA_ES,
    },
}


def replace_once(text: str, pattern: str, replacement: str, path: Path) -> str:
    updated, count = re.subn(pattern, lambda _: replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"{path.relative_to(ROOT)}: expected pattern {pattern!r}")
    return updated


def normalize_tagged_links(text: str) -> str:
    """Rebuild href and topic attributes of every <a data-wa-slug> from TOPICS."""

    def rebuild(match: re.Match) -> str:
        tag = match.group(0)
        slug = re.search(r'data-wa-slug="([^"]+)"', tag).group(1)
        topic_en, topic_es = wa.topics_for(slug)
        tag = re.sub(r'href="[^"]*"', lambda _: f'href="{escape(wa.url("en", topic_en, slug))}"', tag, count=1)
        tag = re.sub(r'data-wa-topic-en="[^"]*"', lambda _: f'data-wa-topic-en="{escape(topic_en)}"', tag, count=1)
        return re.sub(r'data-wa-topic-es="[^"]*"', lambda _: f'data-wa-topic-es="{escape(topic_es)}"', tag, count=1)

    return re.sub(r'<a\b[^>]*\bdata-wa-slug="[^"]+"[^>]*>', rebuild, text)


def set_floating_button(text: str, slug: str, path: Path) -> str:
    """Replace the floating button in place, or add it right after the footer."""
    button = wa.floating_button(slug)
    if '<aside class="wa-float"' in text:
        return replace_once(text, r'<aside class="wa-float"[\s\S]*?</aside>', button, path)
    end = text.rfind("</footer>\n")
    if end < 0:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing </footer>")
    indent = re.match(r"[ \t]*", text[text.rfind("\n", 0, end) + 1:]).group(0)
    insert_at = end + len("</footer>\n")
    return text[:insert_at] + indent + button + "\n" + text[insert_at:]


def set_blog_cta(text: str, slug: str, path: Path) -> str:
    text = re.sub(r'[ \t]*<div class="cta cta-whatsapp">[\s\S]*?</div>\n', "", text)
    block = (
        '    <div class="cta cta-whatsapp">\n'
        f'      <h2 data-i18n="wa.title">{BLOG_CTA["en"]["wa.title"]}</h2>\n'
        f'      <p data-i18n="wa.desc">{BLOG_CTA["en"]["wa.desc"]}</p>\n'
        f'      <a class="btn" {wa.link_attributes(slug)} data-i18n="wa.btn">{BLOG_CTA["en"]["wa.btn"]}</a>\n'
        "    </div>\n"
    )
    text = replace_once(text, r'(?=    <div class="cta">\n)', block, path)
    text = re.sub(r"'wa\.(?:title|desc|btn)':'[^']*',", "", text)
    for language, opener in (("es", "const translations={es:{"), ("en", "},en:{")):
        entries = "".join(f"'{key}':'{value}'," for key, value in BLOG_CTA[language].items())
        text = replace_once(text, re.escape(opener), opener + entries, path)
    return text


def set_include(text: str, tag: str, after: str, path: Path, indent: str = "") -> str:
    """Point the existing whatsapp.css/js include at `tag`, or add `tag` after the `after` pattern."""
    current = r'<link rel="stylesheet" href="/assets/whatsapp\.css[^"]*"/?>' if tag.startswith("<link") else r'<script src="/assets/whatsapp\.js[^"]*" defer></script>'
    if re.search(current, text):
        return replace_once(text, current, tag, path)
    updated, count = re.subn(after, lambda match: f"{match.group(0)}\n{indent}{tag}", text, count=1)
    if count != 1:
        raise SystemExit(f"{path.relative_to(ROOT)}: expected pattern {after!r}")
    return updated


def sync_blog(path: Path, slug: str, is_post: bool) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, r'<nav class="site-nav"[\s\S]*?</nav>', render_navigation(whatsapp=slug), path)
    text = replace_once(text, r'<link rel="stylesheet" href="/assets/site-nav\.css[^"]*">', f'<link rel="stylesheet" href="{NAV_CSS_HREF}">', path)
    text = replace_once(text, r'<script src="/assets/site-nav\.js[^"]*" defer></script>', f'<script src="{NAV_JS_SRC}" defer></script>', path)
    text = set_include(text, f'<link rel="stylesheet" href="{wa.CSS_HREF}">', r'<link rel="stylesheet" href="/assets/site-nav\.css[^"]*">', path)
    text = set_include(text, f'<script src="{wa.JS_SRC}" defer></script>', r'<script src="/assets/site-nav\.js[^"]*" defer></script>', path)
    if is_post:
        text = set_blog_cta(text, slug, path)
    text = set_floating_button(text, slug, path)
    path.write_text(normalize_tagged_links(text), encoding="utf-8")


def sync_legal(path: Path, slug: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, r'<script src="/assets/legal\.js[^"]*"></script>', f'<script src="{LEGAL_JS_SRC}"></script>', path)
    text = set_include(text, f'<link rel="stylesheet" href="{wa.CSS_HREF}">', r'<link rel="stylesheet" href="/assets/legal\.css[^"]*">', path, "  ")
    text = set_include(text, f'<script src="{wa.JS_SRC}" defer></script>', r'<script src="/assets/legal\.js[^"]*"></script>', path, "  ")
    # Contact blocks sit inside one language section each, so their prefill is static.
    english, marker, spanish = text.partition('<div data-language="es"')
    if not marker:
        raise SystemExit(f"{path.relative_to(ROOT)}: missing Spanish section")
    topic_en, topic_es = wa.topics_for(slug)
    english = re.sub(r'<a href="https://wa\.me/[^"]*">', lambda _: f'<a href="{wa.url("en", topic_en, slug)}">', english)
    spanish = re.sub(r'<a href="https://wa\.me/[^"]*">', lambda _: f'<a href="{wa.url("es", topic_es, slug)}">', spanish)
    text = set_floating_button(english + marker + spanish, slug, path)
    path.write_text(normalize_tagged_links(text), encoding="utf-8")


def sync_home(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = set_include(text, f'<link rel="stylesheet" href="{wa.CSS_HREF}"/>', r'<link rel="stylesheet" href="/assets/home\.css[^"]*"/>', path, "  ")
    text = set_include(text, f'<script src="{wa.JS_SRC}" defer></script>', r'<script src="/assets/home\.js[^"]*" defer></script>', path, "  ")
    text = set_floating_button(text, "home", path)
    path.write_text(normalize_tagged_links(text), encoding="utf-8")


def main() -> None:
    sync_home(ROOT / "index.html")
    print("index.html")
    sync_blog(ROOT / "blog" / "index.html", "blog", is_post=False)
    print("blog/index.html")
    for post in sorted((ROOT / "blog").glob("*/index.html")):
        sync_blog(post, f"blog-{post.parent.name}", is_post=True)
        print(post.relative_to(ROOT))
    for page in LEGAL_PAGES:
        sync_legal(ROOT / page / "index.html", page)
        print(f"{page}/index.html")


if __name__ == "__main__":
    main()
