#!/usr/bin/env python3
"""Shared WhatsApp contact and navigation for the hand-authored pages, in one language.

Service and work pages get the same markup from build_service_pages.py. The functions
here take a page's HTML and its language and return it updated; build_language_pages.py
applies them to the English pages (homepage, blog, legal) and to their Spanish twins.
They are idempotent:

- every link tagged data-wa-slug gets the prefill of the page language from
  whatsapp_contact.TOPICS;
- blog pages get the shared navigation (with its mobile WhatsApp item), the floating
  button and, on posts, the in-article WhatsApp CTA;
- legal pages get the floating button and the prefilled contact link of their language.

Running this file rebuilds every language page (same as build_language_pages.py).
"""

import re
from pathlib import Path

import whatsapp_contact as wa
from site_navigation import NAV_CSS_HREF, NAV_JS_SRC, render_navigation

ROOT = Path(__file__).resolve().parents[1]

# In-article WhatsApp CTA of every blog post (data-i18n keys wa.title / wa.desc / wa.btn).
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

_LINK_ATTRIBUTE = re.compile(r'\s(?:href|data-wa-slug|data-wa-topic-en|data-wa-topic-es|data-wa-topic|target|rel)="[^"]*"')


def replace_once(text: str, pattern: str, replacement: str, where: str) -> str:
    updated, count = re.subn(pattern, lambda _: replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"{where}: expected pattern {pattern!r}")
    return updated


def normalize_tagged_links(text: str, lang: str) -> str:
    """Rebuild every <a data-wa-slug> with the prefill of the page language (same attribute
    order as whatsapp_contact.link_attributes, right after the class)."""

    def rebuild(match: re.Match) -> str:
        tag = match.group(0)
        slug = re.search(r'data-wa-slug="([^"]+)"', tag).group(1)
        tag = _LINK_ATTRIBUTE.sub("", tag)
        attributes = wa.link_attributes(slug, lang)
        klass = re.match(r'<a\s+class="[^"]*"', tag)
        if klass:
            return tag[:klass.end()] + " " + attributes + tag[klass.end():]
        return "<a " + attributes + tag[2:]

    return re.sub(r'<a\b[^>]*\bdata-wa-slug="[^"]+"[^>]*>', rebuild, text)


def set_floating_button(text: str, slug: str, lang: str, where: str) -> str:
    """Replace the floating button in place, or add it right after the footer."""
    button = wa.floating_button(slug, lang)
    if re.search(r'<(?:aside|div) class="wa-float"', text):
        return replace_once(text, r'<(aside|div) class="wa-float"[\s\S]*?</\1>', button, where)
    end = text.rfind("</footer>\n")
    if end < 0:
        raise SystemExit(f"{where}: missing </footer>")
    indent = re.match(r"[ \t]*", text[text.rfind("\n", 0, end) + 1:]).group(0)
    insert_at = end + len("</footer>\n")
    return text[:insert_at] + indent + button + "\n" + text[insert_at:]


def set_blog_cta(text: str, slug: str, lang: str, where: str) -> str:
    text = re.sub(r'[ \t]*<div class="cta cta-whatsapp">[\s\S]*?</div>\n', "", text)
    copy = BLOG_CTA[lang]
    block = (
        '    <div class="cta cta-whatsapp">\n'
        f'      <h2 data-i18n="wa.title">{copy["wa.title"]}</h2>\n'
        f'      <p data-i18n="wa.desc">{copy["wa.desc"]}</p>\n'
        f'      <a class="btn" {wa.link_attributes(slug, lang)} data-i18n="wa.btn">{copy["wa.btn"]}</a>\n'
        "    </div>\n"
    )
    return replace_once(text, r'(?=    <div class="cta">\n)', block, where)


def set_include(text: str, tag: str, after: str, where: str, indent: str = "") -> str:
    """Point the existing whatsapp.css/js include at `tag`, or add `tag` after the `after` pattern."""
    current = r'<link rel="stylesheet" href="/assets/whatsapp\.css[^"]*"/?>' if tag.startswith("<link") else r'<script src="/assets/whatsapp\.js[^"]*" defer></script>'
    if re.search(current, text):
        return replace_once(text, current, tag, where)
    updated, count = re.subn(after, lambda match: f"{match.group(0)}\n{indent}{tag}", text, count=1)
    if count != 1:
        raise SystemExit(f"{where}: expected pattern {after!r}")
    return updated


def sync_blog(text: str, slug: str, is_post: bool, lang: str, path: str, where: str) -> str:
    """`path` is the page's English path (for the language switch)."""
    nav = render_navigation(whatsapp=slug, current="/blog/", lang=lang, path=path)
    text = replace_once(text, r'<nav class="site-nav"[\s\S]*?</nav>', nav, where)
    text = replace_once(text, r'<link rel="stylesheet" href="/assets/site-nav\.css[^"]*">', f'<link rel="stylesheet" href="{NAV_CSS_HREF}">', where)
    text = replace_once(text, r'<script src="/assets/site-nav\.js[^"]*" defer></script>', f'<script src="{NAV_JS_SRC}" defer></script>', where)
    text = set_include(text, f'<link rel="stylesheet" href="{wa.CSS_HREF}">', r'<link rel="stylesheet" href="/assets/site-nav\.css[^"]*">', where)
    text = set_include(text, f'<script src="{wa.JS_SRC}" defer></script>', r'<script src="/assets/site-nav\.js[^"]*" defer></script>', where)
    if is_post:
        text = set_blog_cta(text, slug, lang, where)
    text = set_floating_button(text, slug, lang, where)
    return normalize_tagged_links(text, lang)


def sync_legal(text: str, slug: str, lang: str, where: str) -> str:
    text = set_include(text, f'<link rel="stylesheet" href="{wa.CSS_HREF}">', r'<link rel="stylesheet" href="/assets/legal\.css[^"]*">', where, "  ")
    text = set_include(text, f'<script src="{wa.JS_SRC}" defer></script>', r'</footer>', where, "  ")
    # The contact block in the policy text: a plain link with the page-language prefill.
    text = re.sub(r'<a href="https://wa\.me/[^"]*">', lambda _: f'<a href="{wa.page_url(slug, lang)}">', text)
    text = set_floating_button(text, slug, lang, where)
    return normalize_tagged_links(text, lang)


def sync_home(text: str, lang: str, where: str) -> str:
    text = set_include(text, f'<link rel="stylesheet" href="{wa.CSS_HREF}"/>', r'<link rel="stylesheet" href="/assets/home\.css[^"]*"/>', where, "  ")
    text = set_include(text, f'<script src="{wa.JS_SRC}" defer></script>', r'<script src="/assets/home\.js[^"]*" defer></script>', where, "  ")
    text = set_floating_button(text, "home", lang, where)
    return normalize_tagged_links(text, lang)


if __name__ == "__main__":
    import build_language_pages

    raise SystemExit(build_language_pages.main([]))
