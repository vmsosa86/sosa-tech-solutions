"""Shared helpers for the English (default) and Spanish (/es/) versions of every public page.

One URL, one language: an English page lives at its current URL and its Spanish twin at
"/es" + that path. Both are static HTML; nothing is translated in the browser.

- page registry: en_paths(), es_path(), counterpart();
- head: set_head_i18n() writes hreflang alternates (en, es, x-default = en), og:locale and,
  on English pages only, the inline redirect for legacy ?lang=es links;
- body: localize_links() points internal page links at the page language, and
  i18n_replace() fills data-i18n elements and data-i18n-* attributes from a dictionary.
"""

from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://sosatechsolutions.com"
BUSINESS_ID = f"{SITE}/#business"
WEBSITE_ID = f"{SITE}/#website"
LANGUAGES = ("en", "es")
OG_LOCALE = {"en": "en_US", "es": "es_US"}
I18N_DIR = ROOT / "content" / "i18n"
LEGAL_PAGES = ("privacy-policy", "terms", "data-deletion")

# Old social posts and Reels link to EN URLs with ?lang=es. This inline snippet (EN pages only,
# no network request) replaces the visit with the Spanish twin, keeping utm_* and the #hash.
LEGACY_REDIRECT = (
    "<script data-lang-redirect>(function(){try{var q=new URLSearchParams(location.search);"
    "if(q.get('lang')!=='es')return;q.delete('lang');var s=q.toString();"
    "location.replace('/es'+location.pathname+(s?'?'+s:'')+location.hash);}catch(e){}})();</script>"
)


# --- page registry -------------------------------------------------------------------------

def en_paths(root: Path = ROOT) -> List[str]:
    """URL paths of the English public pages, in a stable order (home, services, work, blog, legal)."""
    paths = ["/"]
    paths += sorted(f"/services/{p.parent.name}/" for p in (root / "services").glob("*/index.html"))
    if (root / "work" / "index.html").exists():
        paths.append("/work/")
    if (root / "blog" / "index.html").exists():
        paths.append("/blog/")
    paths += sorted(f"/blog/{p.parent.name}/" for p in (root / "blog").glob("*/index.html"))
    paths += [f"/{name}/" for name in LEGAL_PAGES if (root / name / "index.html").exists()]
    return paths


def is_es(path: str) -> bool:
    return path == "/es/" or path.startswith("/es/")


def es_path(path: str) -> str:
    return path if is_es(path) else "/es" + path


def en_path(path: str) -> str:
    return path[3:] if is_es(path) else path


def counterpart(path: str, lang: str) -> str:
    return es_path(path) if lang == "es" else en_path(path)


def page_file(path: str, root: Path = ROOT) -> Path:
    return root / path.strip("/") / "index.html" if path.strip("/") else root / "index.html"


def absolute(path: str) -> str:
    return SITE + path


def load_json(name: str) -> dict:
    return json.loads((I18N_DIR / name).read_text(encoding="utf-8"))


def text_of(value: str) -> str:
    """Plain text of a dictionary value (tags removed, entities decoded, spaces collapsed)."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


# --- links ---------------------------------------------------------------------------------

def localize_href(href: str, lang: str, pages: Iterable[str]) -> str:
    """Point a same-site page link at the page language; files, assets and other sites stay."""
    if lang != "es" or not href.startswith("/") or href.startswith("//"):
        return href
    parts = urlsplit(href)
    if parts.path in set(pages):
        return urlunsplit(("", "", es_path(parts.path), parts.query, parts.fragment))
    return href


_A_TAG = re.compile(r"<a\b[^>]*>")
_HREF = re.compile(r'(\shref=")([^"]*)(")')


def localize_links(text: str, lang: str, pages: Iterable[str]) -> str:
    pages = set(pages)

    def fix(match: re.Match) -> str:
        tag = match.group(0)
        if "data-lang-link" in tag:
            return tag
        return _HREF.sub(lambda m: m.group(1) + localize_href(m.group(2), lang, pages) + m.group(3), tag, count=1)

    return _A_TAG.sub(fix, text)


def switch_links(path: str, lang: str, attrs: str = "", current_attrs: str = "") -> str:
    """EN/ES language links: real anchors to the counterpart URL (assets/whatsapp.js adds the
    current ?query and #hash when clicked). `attrs` go on both links, `current_attrs` on the
    link of the page's own language, which also gets aria-current="true"."""
    links = []
    for target in LANGUAGES:
        extra = f' {current_attrs}' if target == lang and current_attrs else ""
        current = ' aria-current="true"' if target == lang else ""
        space = f" {attrs}" if attrs else ""
        links.append(
            f'<a{space}{extra} href="{counterpart(path, target)}" hreflang="{target}" lang="{target}" '
            f'data-lang-link="{target}"{current}>{target.upper()}</a>'
        )
    return "".join(links)


# --- head ----------------------------------------------------------------------------------

_HEAD_I18N = re.compile(
    r'[ \t]*(?:<link rel="alternate" hreflang="[^"]*" href="[^"]*"\s*/?>'
    r'|<meta property="og:locale(?::alternate)?" content="[^"]*"\s*/?>'
    r'|<script data-lang-redirect>.*?</script>)\n?'
)
_CANONICAL = re.compile(r'([ \t]*)(<link rel="canonical" href=")[^"]*("\s*/?>)')


def head_block(path: str, lang: str) -> List[str]:
    english = en_path(path)
    lines = [
        f'<link rel="alternate" hreflang="en" href="{absolute(english)}">',
        f'<link rel="alternate" hreflang="es" href="{absolute(es_path(english))}">',
        f'<link rel="alternate" hreflang="x-default" href="{absolute(english)}">',
        f'<meta property="og:locale" content="{OG_LOCALE[lang]}">',
        f'<meta property="og:locale:alternate" content="{OG_LOCALE["es" if lang == "en" else "en"]}">',
    ]
    if lang == "en":
        lines.append(LEGACY_REDIRECT)
    return lines


def set_head_i18n(text: str, path: str, lang: str) -> str:
    """Canonical = self; hreflang, og:locale and (EN) the legacy redirect right after it.
    Idempotent: earlier copies of these tags are removed wherever they are in the page."""
    head_end = text.index("</head>")
    head = _HEAD_I18N.sub("", text[:head_end])
    match = _CANONICAL.search(head)
    if not match:
        raise ValueError(f"{path}: no canonical link")
    indent = match.group(1)
    canonical = f'{match.group(1)}{match.group(2)}{absolute(path)}{match.group(3)}'
    block = "".join("\n" + indent + line for line in head_block(path, lang))
    head = head[:match.start()] + canonical + block + head[match.end():]
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1) + absolute(path) + m.group(2), head)
    return head + text[head_end:]


def set_meta(text: str, title: str, description: str, og_title: Optional[str] = None) -> str:
    """Title, meta description and their Open Graph / Twitter copies."""
    t = attr_escape(title)
    d = attr_escape(description)
    o = attr_escape(og_title or title)
    text = re.sub(r"<title>[^<]*</title>", lambda _: f"<title>{html.escape(title, quote=False)}</title>", text, count=1)
    text = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), text, count=1)
    text = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), text)
    text = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1) + d + m.group(2), text)
    text = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + o + m.group(2), text)
    text = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1) + o + m.group(2), text)
    return text


def set_html_lang(text: str, lang: str) -> str:
    return re.sub(r'<html lang="[^"]*"', f'<html lang="{lang}"', text, count=1)


def set_json_ld(text: str, data: object) -> str:
    """Replace the page's single JSON-LD block (compact, UTF-8)."""
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    updated, count = re.subn(
        r'(<script type="application/ld\+json">)[\s\S]*?(</script>)',
        lambda m: m.group(1) + payload + m.group(2), text, count=1)
    if count != 1:
        raise ValueError("expected one JSON-LD block")
    return updated


def attr_escape(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;")


def html_amp(value: str) -> str:
    """Escape bare ampersands in an HTML fragment (entities stay as they are)."""
    return re.sub(r"&(?!#?\w+;)", "&amp;", value)


# --- data-i18n -----------------------------------------------------------------------------

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# data-i18n-<name> sets these attributes; data-i18n-attr-<attribute> sets any other one.
ATTRIBUTE_KEYS = {
    "data-i18n-placeholder": "placeholder",
    "data-i18n-alt": "alt",
    "data-i18n-aria": "aria-label",
    "data-i18n-src": "src",
    "data-i18n-value": "value",
}


def keyed_attributes(attrs: Dict[str, Optional[str]]) -> List[Tuple[str, str]]:
    pairs = []
    for name, key in attrs.items():
        if name in ATTRIBUTE_KEYS:
            pairs.append((ATTRIBUTE_KEYS[name], key or ""))
        elif name.startswith("data-i18n-attr-"):
            pairs.append((name[len("data-i18n-attr-"):], key or ""))
    return pairs


class _Locator(HTMLParser):
    """Finds the inner HTML of data-i18n elements and the start tags with data-i18n-* attributes."""

    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.text = text
        self._line_starts = [0]
        for match in re.finditer("\n", text):
            self._line_starts.append(match.end())
        self.stack = []  # type: List[Tuple[str, Optional[str], int]]
        self.inner = []  # type: List[Tuple[str, int, int]]  # key, start, end
        self.tags = []  # type: List[Tuple[int, int, List[Tuple[str, str]]]]  # start, end, (attribute, key)
        self.feed(text)
        self.close()
        if any(key for _, key, _ in self.stack):
            raise ValueError("unclosed data-i18n element")

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    def _start(self, tag, attrs, closed):
        start = self._offset()
        end = start + len(self.get_starttag_text())
        values = dict(attrs)
        pairs = keyed_attributes(values)
        if pairs:
            self.tags.append((start, end, pairs))
        key = values.get("data-i18n")
        if tag in VOID or closed:
            if key:
                raise ValueError(f"data-i18n on void element <{tag}> ({key})")
            return
        if key and any(k for _, k, _ in self.stack):
            raise ValueError(f"nested data-i18n element {key}")
        self.stack.append((tag, key, end))

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, True)

    def handle_endtag(self, tag):
        position = self._offset()
        while self.stack:
            open_tag, key, inner_start = self.stack.pop()
            if key:
                if open_tag != tag:
                    raise ValueError(f"data-i18n element <{open_tag}> {key} closed by </{tag}>")
                self.inner.append((key, inner_start, position))
            if open_tag == tag:
                break


def i18n_values(text: str) -> Dict[str, List[str]]:
    """Every data-i18n inner HTML and data-i18n-* attribute value in the page, by key."""
    found = {}  # type: Dict[str, List[str]]
    locator = _Locator(text)
    for key, start, end in locator.inner:
        found.setdefault(key, []).append(text[start:end])
    for start, end, pairs in locator.tags:
        tag = text[start:end]
        for attribute, key in pairs:
            match = re.search(rf'\s{re.escape(attribute)}="([^"]*)"', tag)
            found.setdefault(key, []).append(html.unescape(match.group(1)) if match else "")
    return found


def i18n_replace(text: str, table: Dict[str, str], where: str = "") -> str:
    """Fill data-i18n elements (inner HTML) and data-i18n-* attributes from `table`.
    Every key must exist, so a missing translation fails the build instead of shipping English."""
    locator = _Locator(text)
    edits = []  # type: List[Tuple[int, int, str]]
    missing = set()
    for key, start, end in locator.inner:
        if key not in table:
            missing.add(key)
            continue
        edits.append((start, end, html_amp(table[key])))
    for start, end, pairs in locator.tags:
        tag = text[start:end]
        for attribute, key in pairs:
            if key not in table:
                missing.add(key)
                continue
            value = attr_escape(table[key])
            pattern = re.compile(rf'(\s{re.escape(attribute)}=")[^"]*(")')
            if pattern.search(tag):
                tag = pattern.sub(lambda m: m.group(1) + value + m.group(2), tag, count=1)
            else:
                tag = re.sub(r"\s*(/?)>$", lambda m: f' {attribute}="{value}"' + (m.group(1) and "/") + ">", tag, count=1)
        edits.append((start, end, tag))
    if missing:
        raise KeyError(f"{where}: missing translations for {sorted(missing)}")
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text


def same_html(a: str, b: str) -> bool:
    """Compare two HTML fragments ignoring entity spelling (&amp; vs &) and whitespace runs."""
    def norm(value: str) -> str:
        return " ".join(html.unescape(value).split())
    return norm(a) == norm(b)
