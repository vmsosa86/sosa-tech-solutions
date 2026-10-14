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

import client_work
import language_checks
import whatsapp_contact

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATTERNS = [
    "index.html",
    "privacy-policy/index.html",
    "data-deletion/index.html",
    "terms/index.html",
    "blog/index.html",
    "blog/*/index.html",
    "services/*/index.html",
    "work/index.html",
]
# Every English page has a Spanish twin at "/es" + its path (scripts/build_language_pages.py).
PUBLIC_PATTERNS += ["es/" + pattern for pattern in PUBLIC_PATTERNS]
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
# Self-served reviews are never structured data, whether as a property or as a node of their own.
FORBIDDEN_SCHEMA_TYPES = {"Review", "AggregateRating", "EmployerAggregateRating", "CriticReview", "UserReview"}
# Pages with the shared primary navigation must offer the client work page.
PRIMARY_NAV_CLASSES = {"site-nav", "primary-nav"}
WORK_PATH = "/work/"
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
        self.images = []  # type: List[dict]
        self.anchors = []  # type: List[dict]
        self.primary_navs = 0
        self.nav_work_links = 0
        self._primary_nav_depth = 0  # >0 while inside a .site-nav/.primary-nav element

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "nav":
            if self._primary_nav_depth:
                self._primary_nav_depth += 1
            elif PRIMARY_NAV_CLASSES & set((values.get("class") or "").split()):
                self._primary_nav_depth = 1
                self.primary_navs += 1
        if tag == "a":
            self.anchors.append(values)
            if self._primary_nav_depth and urlparse(values.get("href") or "").path in {WORK_PATH, "/es" + WORK_PATH}:
                self.nav_work_links += 1
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
            if tag == "img":
                self.images.append(values)
            reference = values.get("href") or values.get("src")
            if reference:
                self.links.append(reference)
            # Every responsive image candidate must exist too.
            for candidate in (values.get("srcset") or "").split(","):
                if candidate.strip():
                    self.links.append(candidate.split()[0])
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
        if tag == "nav" and self._primary_nav_depth:
            self._primary_nav_depth -= 1
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
        # The prefill is in the page language, with that language's topic for the page tag.
        lang = language_checks.page_language(rel)
        if match.group(lang) is None:
            errors.append(f"{rel}: WhatsApp prefill is not in the page language ({lang}) {text!r}")
            continue
        slug = values.get("data-wa-slug")
        if slug is not None:
            topic_en, topic_es = whatsapp_contact.topics_for(slug)
            if match.group("slug") != slug or match.group(lang) != (topic_es if lang == "es" else topic_en):
                errors.append(f"{rel}: WhatsApp href does not match the {lang} topic of [web-{slug}] {href}")
        if "floating-whatsapp" in (values.get("class") or "").split() and values.get("aria-label") != whatsapp_contact.LABELS[lang]:
            errors.append(f"{rel}: floating WhatsApp label must be {whatsapp_contact.LABELS[lang]!r}")
    return errors


def work_image_errors(rel: Path, parser: PageParser) -> List[str]:
    """Client-work screenshots load lazily with explicit dimensions (no layout shift)."""
    errors = []  # type: List[str]
    width, height = (str(value) for value in client_work.WORK_IMAGE_SIZE)
    domains = {client["domain"] for client in client_work.CLIENTS}
    for values in parser.images:
        if not (values.get("src") or "").startswith(client_work.WORK_IMAGE_DIR + "/"):
            continue
        if values.get("loading") != "lazy" or values.get("width") != width or values.get("height") != height:
            errors.append(f"{rel}: work image needs loading=lazy width={width} height={height}: {values.get('src')}")
        if not values.get("alt"):
            errors.append(f"{rel}: work image without alt text {values.get('src')}")
        # Phone screenshots ship every width from client_work.py (sharp on high-DPR screens,
        # small on phone thumbnails); the files themselves are checked with the other links.
        domain = values["src"][len(client_work.WORK_IMAGE_DIR) + 1:-len(".jpg")]
        if domain in domains:
            if values.get("srcset") != client_work.srcset(domain):
                errors.append(f"{rel}: work image srcset differs from client_work.srcset({domain!r})")
            if not values.get("sizes"):
                errors.append(f"{rel}: work image without sizes {values.get('src')}")
    return errors


def navigation_errors(rel: Path, parser: PageParser) -> List[str]:
    """The shared primary navigation always links to the client work page."""
    if parser.primary_navs and not parser.nav_work_links:
        return [f"{rel}: primary navigation has no {WORK_PATH} link"]
    return []


def client_link_errors(rel: Path, parser: PageParser) -> List[str]:
    """Links to client sites open in a new tab without giving the client page access to ours."""
    errors = []  # type: List[str]
    domains = {client["domain"] for client in client_work.CLIENTS}
    for values in parser.anchors:
        host = (urlparse(values.get("href") or "").hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host not in domains:
            continue
        if values.get("target") != "_blank" or "noopener" not in (values.get("rel") or "").split():
            errors.append(f"{rel}: client link needs target=_blank and rel=noopener: {values.get('href')}")
    return errors


def schema_types(node) -> Set[str]:
    types = set()  # type: Set[str]
    if isinstance(node, dict):
        value = node.get("@type")
        if isinstance(value, str):
            types.add(value)
        elif isinstance(value, list):
            types.update(item for item in value if isinstance(item, str))
        for child in node.values():
            types |= schema_types(child)
    elif isinstance(node, list):
        for child in node:
            types |= schema_types(child)
    return types


def client_work_errors(root: Path) -> List[str]:
    """Approved testimonials appear verbatim (EN and ES) and every listed client site is linked."""
    errors = []  # type: List[str]
    sources = {}
    for name in ("work/index.html", "es/work/index.html", "index.html", "es/index.html"):
        path = root / name
        sources[name] = path.read_text(encoding="utf-8") if path.exists() else ""
    home_copy = json.loads((language_checks.I18N_DIR / "home.json").read_text(encoding="utf-8"))
    # English quotes on the English pages, Spanish quotes on the Spanish twins, never the other one.
    pages = {"EN": ("work/index.html", "index.html"), "ES": ("es/work/index.html", "es/index.html")}
    for item in client_work.TESTIMONIALS:
        quote = dict(zip(("EN", "ES"), item["quote"]))
        for language, (work, home) in pages.items():
            other = quote["ES" if language == "EN" else "EN"]
            if quote[language] not in sources[work]:
                errors.append(f"{work}: {language} testimonial from {item['name']} is missing or not verbatim")
            if other != quote[language] and (other in sources[work] or other in sources[home]):
                errors.append(f"{work}/{home}: testimonial from {item['name']} shown in the wrong language")
            if item["name"] in client_work.HOMEPAGE_QUOTES and quote[language] not in sources[home]:
                errors.append(f"{home}: {language} testimonial from {item['name']} is missing or not verbatim")
            if item["name"] in client_work.HOMEPAGE_QUOTES and quote[language] not in home_copy[language.lower()].values():
                errors.append(f"content/i18n/home.json: {language} testimonial from {item['name']} is missing or not verbatim")
    for work in ("work/index.html", "es/work/index.html"):
        for client in client_work.CLIENTS:
            if f'href="https://{client["domain"]}/"' not in sources[work]:
                errors.append(f"{work}: no link to {client['domain']}")
    for home in ("index.html", "es/index.html"):
        for domain in client_work.HOMEPAGE_SITES:
            if f'href="https://{domain}/"' not in sources[home]:
                errors.append(f"{home}: no link to featured client {domain}")
    return errors


# /services/agents/ presents two different agents (approved 2026-10-13). Inquiry replies are not
# reviewed by the team before sending; only the content agent's work is approved before publishing.
AGENT_PAGES = {"services/agents/index.html": "", "es/services/agents/index.html": "/es"}
AGENT_RELATED = ("/services/ai-spokesperson/", "/services/automation/")
RETIRED_AGENT_CLAIMS = ("Your team reviews it before sending", "Tu equipo lo revisa antes de enviarlo")


def agents_page_errors(root: Path) -> List[str]:
    errors = []  # type: List[str]
    for rel, prefix in AGENT_PAGES.items():
        path = root / rel
        if not path.exists():
            continue  # reported as a missing page/twin
        source = path.read_text(encoding="utf-8")
        cards = re.findall(r'<article class="agent-card"[\s\S]*?</article>', source)
        if len(cards) != 2:
            errors.append(f"{rel}: expected 2 agent cards (inquiry agent, content agent), found {len(cards)}")
        for index, card in enumerate(cards, 1):
            if card.count('class="agent-list') != 2:
                errors.append(f"{rel}: agent card {index} needs what it does and what reaches the owner")
        for target in AGENT_RELATED:
            if f'href="{prefix}{target}"' not in source:
                errors.append(f"{rel}: missing link to {prefix}{target}")
        for claim in RETIRED_AGENT_CLAIMS:
            if claim in source:
                errors.append(f"{rel}: retired claim {claim!r} (inquiry replies are not reviewed before sending)")
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
        for match in SHORT_BRAND.finditer(source):
            errors.append(f"{rel}: short brand name {source[max(0, match.start() - 30):match.end() + 30]!r}")
        # One language per page, so exactly one h1 (no hidden second-language copy).
        if parser.h1 != 1:
            errors.append(f"{rel}: expected exactly 1 h1, found {parser.h1}")
        if parser.canonical != SITE + language_checks.url_path(rel):
            errors.append(f"{rel}: canonical must be the page's own URL {SITE + language_checks.url_path(rel)}, found {parser.canonical!r}")
        if parser.canonical.startswith("https://sosatechsolutions.com/"):
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
            forbidden_types = schema_types(data) & FORBIDDEN_SCHEMA_TYPES
            if forbidden_types:
                errors.append(f"{rel}: JSON-LD {index} has @type {sorted(forbidden_types)}")
        errors.extend(whatsapp_errors(rel, parser))
        errors.extend(language_checks.page_errors(rel, source, root))
        errors.extend(work_image_errors(rel, parser))
        errors.extend(navigation_errors(rel, parser))
        errors.extend(client_link_errors(rel, parser))
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
        errors.extend(language_checks.sitemap_alternate_errors(url, node))
    if 'xmlns:xhtml="http://www.w3.org/1999/xhtml"' not in (root / "sitemap.xml").read_text(encoding="utf-8"):
        errors.append("sitemap.xml: missing xmlns:xhtml namespace for hreflang alternates")
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
        if re.match(re.escape(SITE) + r"/(?:(?:services|blog)/[^/]+|work)/$", canonical) and canonical not in llms_urls:
            errors.append(f"llms.txt: page not listed {canonical}")
        # The "## En español" section lists every Spanish page.
        if canonical.startswith(SITE + "/es/") and canonical not in llms_urls:
            errors.append(f"llms.txt: Spanish page not listed {canonical}")
    if "## En español" not in llms:
        errors.append("llms.txt: missing '## En español' section")

    errors.extend(client_work_errors(root))
    errors.extend(agents_page_errors(root))
    errors.extend(language_checks.site_errors(root, pages))

    scripts = sorted(root.glob(PUBLIC_SCRIPTS))
    for script in scripts:
        text = script.read_text(encoding="utf-8")
        for match in SHORT_BRAND.finditer(text):
            errors.append(f"{script.relative_to(root)}: short brand name {text[max(0, match.start() - 30):match.end() + 30]!r}")
        errors.extend(language_checks.script_errors(script.relative_to(root), text))

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
