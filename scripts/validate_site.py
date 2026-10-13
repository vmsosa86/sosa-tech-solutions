#!/usr/bin/env python3
"""Validate public Sosa Tech Solutions pages, local links, metadata, and structured data."""

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import parse_qs, quote, unquote, urlparse
import xml.etree.ElementTree as ET

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATTERNS = [
    "index.html",
    "privacy-policy/index.html",
    "data-deletion/index.html",
    "terms/index.html",
    "blog/index.html",
    "blog/*/index.html",
    "services/*/index.html",
]
WHATSAPP_MESSAGE = re.compile(
    r"^(?:Hi Sosa Tech Solutions, I'd like to talk about (?P<en>.+)"
    r"|Hola Sosa Tech Solutions, quiero hablar sobre (?P<es>.+))\. \[web-(?P<slug>[a-z0-9-]+)\]$"
)
SITE = "https://sosatechsolutions.com"
TITLE_SUFFIX = "| Sosa Tech Solutions"
TITLE_MAX = 60
DESCRIPTION_RANGE = (140, 155)
# The brand is always "Sosa Tech Solutions": no "Sosa Tech", "SosaTech", "SOSA TECH" or variants split by
# spaces, line breaks or &nbsp;. Domains, paths and storage keys are lowercase, so they never match.
_GAP = r"(?:\s|&nbsp;|&#160;)"
SHORT_BRAND = re.compile(
    rf"Sosa{_GAP}+Tech(?!{_GAP}+Solutions)|SosaTech|SOSA{_GAP}+TECH(?!{_GAP}+SOLUTIONS)|SOSATECH"
)
# Public scripts hold copy too (homepage dictionary, navigation and WhatsApp labels).
PUBLIC_SCRIPTS = "assets/*.js"
FORBIDDEN_SCHEMA_KEYS = {"aggregateRating", "review", "reviews"}
SITE_URL = re.compile(r"https://sosatechsolutions\.com/[^\s)<>\"']*")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.h1 = 0
        self.description = ""
        self.canonical = ""
        self.links = []  # type: List[str]
        self.json_ld = []  # type: List[str]
        self._in_json_ld = False
        self._json_buffer = []  # type: List[str]
        self.whatsapp_links = []  # type: List[dict]
        self.floating_whatsapp = 0
        self.autoplay_videos = 0
        self._whatsapp_wrapper_depth = 0  # >0 while inside the .wa-float wrapper
        self.html_attrs = {}  # type: dict

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.html_attrs = values
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta" and values.get("name") == "description":
            self.description = values.get("content", "")
        elif tag == "link" and "canonical" in values.get("rel", "").split():
            self.canonical = values.get("href", "")
        elif tag in {"a", "img", "script", "link", "source"}:
            reference = values.get("href") or values.get("src")
            if reference:
                self.links.append(reference)
            # Language-specific image sources (swapped by the page script) must exist too.
            for key in ("data-src-en", "data-src-es"):
                if values.get(key):
                    self.links.append(values[key])
        elif tag == "video":
            # Example videos: the poster and any direct src must exist; autoplay is never allowed.
            for reference in (values.get("poster"), values.get("src")):
                if reference:
                    self.links.append(reference)
            if "autoplay" in values:
                self.autoplay_videos += 1
        if self._whatsapp_wrapper_depth and tag == "div":
            self._whatsapp_wrapper_depth += 1
        elif tag == "div" and "wa-float" in (values.get("class") or "").split():
            self._whatsapp_wrapper_depth = 1
        if tag == "a" and (values.get("href") or "").startswith(("https://wa.me/", "https://api.whatsapp.com/")):
            self.whatsapp_links.append(values)
            if self._whatsapp_wrapper_depth and "floating-whatsapp" in (values.get("class") or "").split():
                self.floating_whatsapp += 1
        if tag == "script" and values.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_buffer = []

    def handle_endtag(self, tag):
        if tag == "div" and self._whatsapp_wrapper_depth:
            self._whatsapp_wrapper_depth -= 1
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self._in_json_ld = False
            self.json_ld.append("".join(self._json_buffer).strip())

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_json_ld:
            self._json_buffer.append(data)


def whatsapp_errors(rel: Path, parser: PageParser) -> List[str]:
    """Every WhatsApp link must carry a well-formed, page-tagged prefill."""
    errors = []  # type: List[str]
    if parser.floating_whatsapp != 1:
        errors.append(f"{rel}: expected 1 floating WhatsApp button in div.wa-float, found {parser.floating_whatsapp}")
    for values in parser.whatsapp_links:
        href = values["href"]
        parsed = urlparse(href)
        texts = parse_qs(parsed.query).get("text", [])
        if parsed.netloc != "wa.me" or parsed.path != "/13057415702" or len(texts) != 1:
            errors.append(f"{rel}: WhatsApp link without number/prefill {href}")
            continue
        text = texts[0]
        match = WHATSAPP_MESSAGE.match(text)
        if not match:
            errors.append(f"{rel}: unexpected WhatsApp prefill {text!r}")
            continue
        if parsed.query != "text=" + quote(text, safe=""):
            errors.append(f"{rel}: WhatsApp prefill not encoded like assets/whatsapp.js {href}")
        slug = values.get("data-wa-slug")
        if slug is not None:
            if match.group("slug") != slug or match.group("en") != values.get("data-wa-topic-en"):
                errors.append(f"{rel}: WhatsApp href does not match its data-wa-* attributes {href}")
            if not values.get("data-wa-topic-es"):
                errors.append(f"{rel}: WhatsApp link {slug} has no Spanish topic")
    return errors


def public_pages(root: Path) -> List[Path]:
    pages = set()  # type: Set[Path]
    for pattern in PUBLIC_PATTERNS:
        pages.update(root.glob(pattern))
    return sorted(pages)


def resolve_local(reference: str, root: Path) -> Optional[Path]:
    if reference.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    parsed = urlparse(reference)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    target = root / path.lstrip("/")
    if path.endswith("/") or not target.suffix:
        target /= "index.html"
    return target


def schema_keys(node) -> Set[str]:
    keys = set()  # type: Set[str]
    if isinstance(node, dict):
        for key, value in node.items():
            keys.add(key)
            keys |= schema_keys(value)
    elif isinstance(node, list):
        for value in node:
            keys |= schema_keys(value)
    return keys


def site_path(url: str) -> str:
    return urlparse(url).path or "/"


def check_site_url(source: str, url: str, root: Path, pending: Set[str], errors: List[str], notes: List[str]) -> None:
    """A sitemap/llms.txt URL must be a real page, unless explicitly allowed as pending."""
    local = resolve_local(url.replace(SITE, ""), root)
    if not local or local.exists():
        return
    if site_path(url) in pending:
        notes.append(f"{source}: pending page not built yet {url}")
    else:
        errors.append(f"{source}: missing page {url}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--allow-missing",
        action="append",
        default=[],
        metavar="PATH",
        help="URL path (e.g. /services/new-page/) that sitemap.xml and llms.txt may list before the page exists. "
        "Deploys never pass this, so a pending page blocks deployment until it is built.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    pending = set(args.allow_missing)  # type: Set[str]
    errors = []  # type: List[str]
    notes = []  # type: List[str]
    pages = public_pages(root)
    expected_canonicals = set()  # type: Set[str]
    for path in pages:
        source = path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(source)
        rel = path.relative_to(root)
        title = parser.title.strip()
        if not (10 <= len(title) <= TITLE_MAX):
            errors.append(f"{rel}: title length {len(title)} (max {TITLE_MAX})")
        if not title.endswith(TITLE_SUFFIX):
            errors.append(f"{rel}: title must end with '{TITLE_SUFFIX}': {title!r}")
        low, high = DESCRIPTION_RANGE
        if not (low <= len(parser.description.strip()) <= high):
            errors.append(f"{rel}: description length {len(parser.description.strip())} (expected {low}-{high})")
        # Service pages carry the Spanish snippet that assets/service.js applies; same standard.
        title_es = (parser.html_attrs.get("data-title-es") or "").strip()
        description_es = (parser.html_attrs.get("data-description-es") or "").strip()
        if rel.parts[0] == "services" and not (title_es and description_es):
            errors.append(f"{rel}: missing data-title-es / data-description-es on <html>")
        if title_es and (len(title_es) > TITLE_MAX or not title_es.endswith(TITLE_SUFFIX)):
            errors.append(f"{rel}: Spanish title must be <= {TITLE_MAX} chars ending '{TITLE_SUFFIX}': {title_es!r} ({len(title_es)})")
        if description_es and not (low <= len(description_es) <= high):
            errors.append(f"{rel}: Spanish description length {len(description_es)} (expected {low}-{high})")
        for match in SHORT_BRAND.finditer(source):
            errors.append(f"{rel}: short brand name {source[max(0, match.start() - 30):match.end() + 30]!r}")
        # Legal pages keep one H1 per language in the source and hide the inactive language.
        if parser.h1 not in {1, 2}:
            errors.append(f"{rel}: expected 1 visible-language h1, found {parser.h1}")
        if not parser.canonical.startswith("https://sosatechsolutions.com/"):
            errors.append(f"{rel}: missing/invalid canonical")
        else:
            expected_canonicals.add(parser.canonical)
        for index, block in enumerate(parser.json_ld, 1):
            try:
                data = json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: JSON-LD {index}: {exc}")
                continue
            forbidden = schema_keys(data) & FORBIDDEN_SCHEMA_KEYS
            if forbidden:
                errors.append(f"{rel}: JSON-LD {index} uses {sorted(forbidden)}")
        errors.extend(whatsapp_errors(rel, parser))
        if parser.autoplay_videos:
            errors.append(f"{rel}: {parser.autoplay_videos} video(s) with autoplay")
        for reference in parser.links:
            target = resolve_local(reference, root)
            if target and not target.exists():
                errors.append(f"{rel}: missing local target {reference}")

    sitemap = ET.parse(root / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = set()  # type: Set[str]
    for node in sitemap.findall("s:url", namespace):
        url = (node.findtext("s:loc", "", namespace) or "").strip()
        lastmod = (node.findtext("s:lastmod", "", namespace) or "").strip()
        if not url.startswith(SITE + "/"):
            errors.append(f"sitemap.xml: invalid loc {url!r}")
            continue
        if url in sitemap_urls:
            errors.append(f"sitemap.xml: duplicate URL {url}")
        sitemap_urls.add(url)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod):
            errors.append(f"sitemap.xml: missing/invalid lastmod for {url}")
        if "#" in url:
            errors.append(f"sitemap.xml: fragment URL {url}")
        check_site_url("sitemap.xml", url, root, pending, errors, notes)
    for canonical in expected_canonicals:
        if canonical not in sitemap_urls:
            errors.append(f"sitemap.xml: canonical not listed {canonical}")

    robots_path = root / "robots.txt"
    robots = robots_path.read_text(encoding="utf-8") if robots_path.exists() else ""
    if not re.search(r"^User-agent: \*\nAllow: /$", robots, re.M):
        errors.append("robots.txt: must open with 'User-agent: *' / 'Allow: /'")
    if f"Sitemap: {SITE}/sitemap.xml" not in robots.splitlines():
        errors.append("robots.txt: missing Sitemap line")

    llms_path = root / "llms.txt"
    llms = llms_path.read_text(encoding="utf-8") if llms_path.exists() else ""
    if not llms.startswith("# Sosa Tech Solutions\n"):
        errors.append("llms.txt: missing or does not start with '# Sosa Tech Solutions'")
    for match in SHORT_BRAND.finditer(llms):
        errors.append(f"llms.txt: short brand name {llms[max(0, match.start() - 30):match.end() + 30]!r}")
    llms_urls = set(SITE_URL.findall(llms))
    for url in sorted(llms_urls):
        check_site_url("llms.txt", url, root, pending, errors, notes)
    for canonical in sorted(expected_canonicals):
        if re.match(re.escape(SITE) + r"/(services|blog)/[^/]+/$", canonical) and canonical not in llms_urls:
            errors.append(f"llms.txt: page not listed {canonical}")

    scripts = sorted(root.glob(PUBLIC_SCRIPTS))
    for script in scripts:
        text = script.read_text(encoding="utf-8")
        for match in SHORT_BRAND.finditer(text):
            errors.append(f"{script.relative_to(root)}: short brand name {text[max(0, match.start() - 30):match.end() + 30]!r}")

    for note in notes:
        print(f"NOTE {note}")
    if errors:
        print("SITE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"SITE VALIDATION PASSED: {len(pages)} pages, {len(scripts)} scripts, {len(sitemap_urls)} sitemap URLs, {len(llms_urls)} llms.txt URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
