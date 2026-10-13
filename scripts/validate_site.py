#!/usr/bin/env python3
"""Validate public Sosa Tech pages, local links, metadata, and structured data."""

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
        self._in_whatsapp_aside = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta" and values.get("name") == "description":
            self.description = values.get("content", "")
        elif tag == "link" and "canonical" in values.get("rel", "").split():
            self.canonical = values.get("href", "")
        elif tag in {"a", "img", "script", "link"}:
            reference = values.get("href") or values.get("src")
            if reference:
                self.links.append(reference)
        if tag == "aside" and "wa-float" in (values.get("class") or "").split():
            self._in_whatsapp_aside = True
        if tag == "a" and (values.get("href") or "").startswith(("https://wa.me/", "https://api.whatsapp.com/")):
            self.whatsapp_links.append(values)
            if self._in_whatsapp_aside and "floating-whatsapp" in (values.get("class") or "").split():
                self.floating_whatsapp += 1
        if tag == "script" and values.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_buffer = []

    def handle_endtag(self, tag):
        if tag == "aside":
            self._in_whatsapp_aside = False
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
        errors.append(f"{rel}: expected 1 floating WhatsApp button in aside.wa-float, found {parser.floating_whatsapp}")
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    errors = []  # type: List[str]
    pages = public_pages(root)
    expected_canonicals = set()  # type: Set[str]
    for path in pages:
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        rel = path.relative_to(root)
        if not (10 <= len(parser.title.strip()) <= 70):
            errors.append(f"{rel}: title length {len(parser.title.strip())}")
        if not (70 <= len(parser.description.strip()) <= 165):
            errors.append(f"{rel}: description length {len(parser.description.strip())}")
        # Legal pages keep one H1 per language in the source and hide the inactive language.
        if parser.h1 not in {1, 2}:
            errors.append(f"{rel}: expected 1 visible-language h1, found {parser.h1}")
        if not parser.canonical.startswith("https://sosatechsolutions.com/"):
            errors.append(f"{rel}: missing/invalid canonical")
        else:
            expected_canonicals.add(parser.canonical)
        for index, block in enumerate(parser.json_ld, 1):
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: JSON-LD {index}: {exc}")
        errors.extend(whatsapp_errors(rel, parser))
        for reference in parser.links:
            target = resolve_local(reference, root)
            if target and not target.exists():
                errors.append(f"{rel}: missing local target {reference}")

    sitemap = ET.parse(root / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {node.text.strip() for node in sitemap.findall("s:url/s:loc", namespace) if node.text}
    for url in sitemap_urls:
        if "#" in url:
            errors.append(f"sitemap.xml: fragment URL {url}")
        local = resolve_local(url.replace("https://sosatechsolutions.com", ""), root)
        if local and not local.exists():
            errors.append(f"sitemap.xml: missing page {url}")
    for canonical in expected_canonicals:
        if canonical not in sitemap_urls:
            errors.append(f"sitemap.xml: canonical not listed {canonical}")

    if errors:
        print("SITE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"SITE VALIDATION PASSED: {len(pages)} pages, {len(sitemap_urls)} sitemap URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
