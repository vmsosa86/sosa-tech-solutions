"""Language checks for validate_site.py: English pages at their URLs, Spanish twins under /es/.

- every English page has its Spanish twin and vice versa;
- <html lang>, canonical = self, og:url, og:locale (+ alternate), reciprocal hreflang
  (en, es, x-default = en) on both versions and the same alternates in sitemap.xml;
- Spanish titles and descriptions differ from the English twin;
- no hidden second-language copy or browser-side translation is left (data-lang, setLang ...);
- data-i18n copy equals content/i18n (EN page = "en", ES page = "es");
- no English UI strings from the dictionaries are visible on Spanish pages;
- internal page links stay in the page language, except the EN/ES switch (absolute
  https://sosatechsolutions.com/... links count as internal), and none carries ?lang=;
- no text, title or description looks like the other language (stop-word heuristic), and
  no Spanish slot in the sources is left identical to an English sentence;
- the English tagline on Spanish pages is marked lang="en";
- JSON-LD inLanguage matches the page, the business @id is unchanged, FAQ questions and
  answers match the visible <details>;
- the legacy ?lang=es redirect is on every English page; the contact form says its language;
- starting prices appear only on the two approved pages per language.
"""

from __future__ import annotations

import ast
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
from urllib.parse import parse_qs, urlsplit

import build_service_pages
import build_work_page
import client_work
import site_i18n
import sync_whatsapp_contact
import whatsapp_contact
from site_navigation import NAV_LABELS

SITE = site_i18n.SITE
I18N_DIR = site_i18n.I18N_DIR
XHTML_NS = "{http://www.w3.org/1999/xhtml}"
OG_LOCALE = site_i18n.OG_LOCALE
# Left over from the old browser-side language switch; none of it may come back.
FORBIDDEN_ATTRIBUTES = re.compile(
    r"\sdata-(?:lang|language|title-es|description-es|alt-en|alt-es|src-en|src-es|wa-topic-en|wa-topic-es|"
    r"wa-label-en|wa-label-es|set-lang|set-language|nav-lang|nav-text|lang-btn)="
)
FORBIDDEN_PAGE_CODE = ("const translations=", "setLang(", "localStorage.getItem('sosaLang')")
FORBIDDEN_SCRIPT_CODE = ("searchParams.set('lang'", 'searchParams.set("lang"', "setLanguage(", "sosaWhatsApp", "data-i18n")
# Visible on Spanish pages by design: brand tagline and names.
ALLOWED_ENGLISH = {"We build. You grow.", "Sosa Tech Solutions"}
# Plain UI strings outside the dictionaries that must never appear on a Spanish page.
ENGLISH_UI = [
    "Skip to content", "Visit site", "opens in a new tab", "Read article", "Message sent.", "Primary navigation",
    "Legal page navigation", "Legal links", "Open navigation menu", "Close navigation menu", "Request a free review",
    "Request my free review", "Message Victor on WhatsApp", "Chat with Sosa Tech Solutions on WhatsApp",
    "you@yourbusiness.com", "Blog posts", "Language selector", "OPERATING PROOF", "BUILD PRINCIPLE",
]
TAGLINE = "We build. You grow."
# Stop words that exist in only one of the two languages. Proper names (brand, tagline, client
# businesses such as "Radio To Be" or "Miami Travel y Más") are removed before counting.
EN_WORDS = set("""the and your you with for to of is are we our that this what how it on from by be or can when
who before after every each will my i they their an into at get do does need not yes have has which more""".split())
ES_WORDS = set("""el la los las de del que y en para con por tu tus un una es su sus lo se al mi más cómo qué sin
cada también te nuestro nuestra sí o antes después puedes tienes necesitas tú ya cuando quién""".split())
SITE_ORIGINS = ("https://sosatechsolutions.com", "https://www.sosatechsolutions.com",
                "http://sosatechsolutions.com", "http://www.sosatechsolutions.com")
# Approved starting prices (2026-10-13): only these pages show them.
PRICE = re.compile(r"\$500/m|\$1,500")
PRICE_PAGES = {"index.html", "services/websites/index.html", "es/index.html", "es/services/websites/index.html"}
EXPECTED_TYPES = {"home": {"FAQPage"}, "services": {"Service", "FAQPage", "BreadcrumbList"}, "work": {"CollectionPage"},
                  "blog-index": {"Blog"}, "blog-post": {"BlogPosting"}}


def url_path(rel: Path) -> str:
    """URL path of a public page file: es/services/x/index.html -> /es/services/x/."""
    parts = Path(rel).parts[:-1]
    return "/" + "/".join(parts) + "/" if parts else "/"


def page_language(rel: Path) -> str:
    return "es" if Path(rel).parts[0] == "es" else "en"


def page_kind(rel: Path) -> str:
    parts = Path(site_i18n.en_path(url_path(rel)).strip("/")).parts
    if not parts:
        return "home"
    if parts[0] == "services":
        return "services"
    if parts[0] == "work":
        return "work"
    if parts[0] == "blog":
        return "blog-index" if len(parts) == 1 else "blog-post"
    return "legal"


def norm(text: str) -> str:
    return " ".join(html.unescape(text).split())


class LanguageParser(HTMLParser):
    TEXT_ATTRIBUTES = ("alt", "aria-label", "placeholder", "title")
    META_TEXT = {"description", "og:title", "og:description", "twitter:title", "twitter:description", "og:image:alt"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.alternates = {}  # type: Dict[str, str]
        self.meta = {}  # type: Dict[str, str]
        self.texts = []  # type: List[str]
        self.anchors = []  # type: List[dict]
        self.inputs = []  # type: List[dict]
        self.forms = []  # type: List[dict]
        self.summaries = []  # type: List[str]
        self.answers = []  # type: List[str]  # visible <details> text after its <summary>
        self._details = None
        self._skip = 0
        self._summary = None
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang") or ""
        elif tag == "link" and values.get("rel") == "alternate" and values.get("hreflang"):
            self.alternates[values["hreflang"]] = values.get("href") or ""
        elif tag == "meta":
            key = values.get("property") or values.get("name")
            if key:
                self.meta.setdefault(key, values.get("content") or "")
                if key in self.META_TEXT:
                    self.texts.append(values.get("content") or "")
        elif tag == "a":
            self.anchors.append(values)
        elif tag == "input":
            self.inputs.append(values)
        elif tag == "form":
            self.forms.append(values)
        elif tag == "summary":
            self._summary = []
        elif tag == "details":
            self._details = []
        elif tag == "title":
            self._in_title = True
        if tag in {"script", "style", "svg", "noscript"}:
            self._skip += 1
        for name in self.TEXT_ATTRIBUTES:
            if values.get(name):
                self.texts.append(values[name])

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg", "noscript"} and self._skip:
            self._skip -= 1
        elif tag == "summary" and self._summary is not None:
            self.summaries.append(norm("".join(self._summary)))
            self._summary = None
        elif tag == "details" and self._details is not None:
            self.answers.append(norm(" ".join(self._details)))
            self._details = None
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            self.texts.append(data)
            return
        if self._skip:
            return
        self.texts.append(data)
        if self._summary is not None:
            self._summary.append(data)
        elif self._details is not None:
            self._details.append(data)


# --- dictionaries --------------------------------------------------------------------------

def load(name: str) -> dict:
    return json.loads((I18N_DIR / name).read_text(encoding="utf-8"))


def page_dictionary(rel: Path) -> Dict[str, str]:
    """The content/i18n copy that the page's data-i18n keys must show (homepage, blog, legal)."""
    lang = page_language(rel)
    kind = page_kind(rel)
    if kind == "home":
        return load("home.json")[lang]
    if kind in {"blog-index", "blog-post"}:
        name = "index" if kind == "blog-index" else Path(rel).parts[-2]
        return {**load(f"blog/{name}.json")[lang], **sync_whatsapp_contact.BLOG_CTA[lang]}
    if kind == "legal":
        return load("legal.json")[lang]
    return {}


def _pairs(node, found: List[Tuple[str, str]]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key.endswith("_es"):
                continue
            if isinstance(value, str) and isinstance(node.get(key + "_es"), str):
                found.append((value, node[key + "_es"]))
            else:
                _pairs(value, found)
    elif isinstance(node, tuple) and all(isinstance(item, str) for item in node):
        if len(node) == 2:
            found.append(node)
        elif len(node) == 4:
            found.extend([(node[0], node[2]), (node[1], node[3])])
        elif len(node) == 5:  # related offer: slug, link en, link es, text en, text es
            found.extend([(node[1], node[2]), (node[3], node[4])])
    elif isinstance(node, (list, tuple)):
        for item in node:
            _pairs(item, found)


def source_pairs(module) -> List[Tuple[str, str]]:
    """(English, Spanish) literals written inline in a generator: both("..", ".."), pick("..", "..")
    and 2-string tuples such as offer.get("intro_label", ("What we can build", "Qué podemos crear"))."""
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        items = None
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") in {"both", "pick"}:
            items = node.args
        elif isinstance(node, ast.Tuple) and len(node.elts) == 2:
            items = node.elts
        if items and len(items) == 2 and all(isinstance(i, ast.Constant) and isinstance(i.value, str) for i in items):
            found.append((items[0].value, items[1].value))
    return found


def translation_pairs() -> List[Tuple[str, str]]:
    """Every (English, Spanish) pair the site renders from its sources."""
    pairs = source_pairs(build_service_pages) + source_pairs(build_work_page)  # type: List[Tuple[str, str]]
    _pairs(build_service_pages.OFFERS, pairs)
    _pairs(build_service_pages.STEPS, pairs)
    for slug in build_service_pages.SEO:
        pairs.append((build_service_pages.SEO[slug][0], build_service_pages.SEO_ES[slug][0]))
        pairs.append((build_service_pages.SEO[slug][1], build_service_pages.SEO_ES[slug][1]))
    _pairs(build_work_page.COPY, pairs)
    pairs += list(zip(build_work_page.SEO, build_work_page.SEO_ES))
    _pairs(client_work.CLIENTS, pairs)
    _pairs(client_work.TESTIMONIALS, pairs)
    pairs += [(NAV_LABELS["en"][key], NAV_LABELS["es"][key]) for key in NAV_LABELS["en"]]
    pairs += [(whatsapp_contact.CTA_EN, whatsapp_contact.CTA_ES), (whatsapp_contact.LABEL_EN, whatsapp_contact.LABEL_ES)]
    for name in ["home.json", "legal.json"] + [f"blog/{p.name}" for p in sorted((I18N_DIR / "blog").glob("*.json"))]:
        data = load(name)
        pairs += [(data["en"][key], data["es"].get(key, "")) for key in data["en"]]
    pairs += [(sync_whatsapp_contact.BLOG_CTA["en"][key], sync_whatsapp_contact.BLOG_CTA["es"][key]) for key in sync_whatsapp_contact.BLOG_CTA["en"]]
    return pairs


_ENGLISH_CACHE = []  # type: List[Tuple[str, int]]


def english_strings() -> List[Tuple[str, int]]:
    """English texts that differ from their Spanish and are not used inside any Spanish text."""
    if _ENGLISH_CACHE:
        return _ENGLISH_CACHE
    pairs = translation_pairs()
    spanish = " \n ".join(site_i18n.text_of(es) for _, es in pairs)
    seen = set()
    for en, es in pairs:
        text = site_i18n.text_of(en)
        if not text or text == site_i18n.text_of(es) or text in ALLOWED_ENGLISH or text in seen:
            continue
        if text in spanish or text.startswith("/") or not re.search(r"[A-Za-z]", text):
            continue
        seen.add(text)
        _ENGLISH_CACHE.append((text, len(text.split())))
    _ENGLISH_CACHE.extend((text, len(text.split())) for text in ENGLISH_UI if text not in seen)
    return _ENGLISH_CACHE


# --- language heuristic --------------------------------------------------------------------

_NAMES = []  # type: List[str]


def proper_names() -> List[str]:
    if not _NAMES:
        names = set(ALLOWED_ENGLISH) | {c["name"] for c in client_work.CLIENTS}
        names |= {t["business"] for t in client_work.TESTIMONIALS} | {t["name"] for t in client_work.TESTIMONIALS}
        _NAMES.extend(sorted(names, key=len, reverse=True))
    return _NAMES


def language_votes(text: str) -> Tuple[int, int]:
    """(English, Spanish) stop-word counts of a text, proper names removed."""
    for name in proper_names():
        text = text.replace(name, " ")
    words = re.findall(r"[a-záéíóúñü]+", text.lower())
    return sum(w in EN_WORDS for w in words), sum(w in ES_WORDS for w in words)


def looks_like(text: str, lang: str) -> bool:
    """True when `text` reads as `lang` (at least two of its stop words, more than the other's)."""
    en, es = language_votes(text)
    return (en >= 2 and en > es) if lang == "en" else (es >= 2 and es > en)


def source_errors() -> List[str]:
    """A Spanish slot that still holds the English sentence (the pair is identical)."""
    errors = []  # type: List[str]
    seen = set()
    for en, es in translation_pairs():
        text = site_i18n.text_of(en)
        if text and text == site_i18n.text_of(es) and text not in seen and looks_like(text, "en"):
            seen.add(text)
            errors.append(f"sources: Spanish copy is still the English text: {text[:90]!r}")
    return errors


# --- per page ------------------------------------------------------------------------------

def site_relative(href: str) -> str:
    """https://sosatechsolutions.com/x/?q#h -> /x/?q#h; other URLs are returned unchanged."""
    for origin in SITE_ORIGINS:
        if href == origin:
            return "/"
        if href.startswith(origin) and href[len(origin)] in "/?#":
            rest = href[len(origin):]
            return rest if rest.startswith("/") else "/" + rest
    return href


def is_page_link(href: str) -> bool:
    href = site_relative(href)
    if not href.startswith("/") or href.startswith("//"):
        return False
    path = urlsplit(href).path
    return not path.startswith("/assets/") and (path.endswith("/") or "." not in path.rsplit("/", 1)[-1])


def json_ld_nodes(source: str) -> List[dict]:
    nodes = []
    for block in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', source):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue  # reported by validate_site.py
        stack = [data]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if "@type" in item:
                    nodes.append(item)
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    return nodes


def page_errors(rel: Path, source: str, root: Path) -> List[str]:
    errors = []  # type: List[str]
    lang = page_language(rel)
    other = "en" if lang == "es" else "es"
    path = url_path(rel)
    english = site_i18n.en_path(path)
    parser = LanguageParser()
    parser.feed(source)
    kind = page_kind(rel)

    if parser.lang != lang:
        errors.append(f"{rel}: <html lang> must be {lang!r}, found {parser.lang!r}")
    expected = {"en": SITE + english, "es": SITE + site_i18n.es_path(english), "x-default": SITE + english}
    if parser.alternates != expected:
        errors.append(f"{rel}: hreflang alternates must be {expected}, found {parser.alternates}")
    if parser.meta.get("og:url") != SITE + path:
        errors.append(f"{rel}: og:url must be {SITE + path}, found {parser.meta.get('og:url')!r}")
    if parser.meta.get("og:locale") != OG_LOCALE[lang] or parser.meta.get("og:locale:alternate") != OG_LOCALE[other]:
        errors.append(f"{rel}: og:locale must be {OG_LOCALE[lang]} with og:locale:alternate {OG_LOCALE[other]}")
    for key in ("og:title", "og:description"):
        if not parser.meta.get(key):
            errors.append(f"{rel}: missing {key}")

    # Reciprocity: the twin exists and points back.
    twin_rel = Path(site_i18n.counterpart(path, other).strip("/") or ".") / "index.html"
    twin = root / twin_rel
    if not twin.exists():
        errors.append(f"{rel}: missing {other.upper()} twin {twin_rel}")
    else:
        twin_parser = LanguageParser()
        twin_parser.feed(twin.read_text(encoding="utf-8"))
        if twin_parser.alternates != parser.alternates:
            errors.append(f"{rel}: hreflang alternates differ from its twin {twin_rel}")
        if lang == "es":
            twin_description = twin_parser.meta.get("description", "")
            if norm(parser.title) == norm(twin_parser.title):
                errors.append(f"{rel}: Spanish title is the same as the English one")
            if norm(parser.meta.get("description", "")) == norm(twin_description):
                errors.append(f"{rel}: Spanish description is the same as the English one")
    if not parser.title.strip():
        errors.append(f"{rel}: missing title")

    for match in FORBIDDEN_ATTRIBUTES.finditer(source):
        errors.append(f"{rel}: leftover browser-side translation attribute {match.group(0).strip()!r}")
    for code in FORBIDDEN_PAGE_CODE:
        if code in source:
            errors.append(f"{rel}: leftover browser-side translation code {code!r}")
    redirects = source.count("<script data-lang-redirect>")
    if lang == "en" and (redirects != 1 or site_i18n.LEGACY_REDIRECT not in source):
        errors.append(f"{rel}: English page needs the legacy ?lang=es redirect snippet exactly once")
    if lang == "es" and redirects:
        errors.append(f"{rel}: Spanish page must not carry the legacy redirect")

    # data-i18n copy matches the dictionary of the page language.
    table = page_dictionary(rel)
    if table:
        try:
            values = site_i18n.i18n_values(source)
        except ValueError as exc:
            values = {}
            errors.append(f"{rel}: {exc}")
        for key, found in values.items():
            if key not in table:
                errors.append(f"{rel}: data-i18n key {key!r} not in content/i18n ({lang})")
                continue
            # Page links inside the copy point to the page language (as build_language_pages renders them).
            wanted = site_i18n.localize_links(table[key], lang, build_service_pages.link_pages())
            for value in found:
                if not site_i18n.same_html(value, wanted):
                    errors.append(f"{rel}: data-i18n {key!r} differs from content/i18n ({lang}): {value[:80]!r}")

    # Language switch: one EN and one ES link to the twins, the current one marked.
    switches = [a for a in parser.anchors if a.get("data-lang-link")]
    targets = {a["data-lang-link"]: a for a in switches}
    if len(switches) != 2 or set(targets) != {"en", "es"}:
        errors.append(f"{rel}: expected one EN and one ES language link, found {len(switches)}")
    else:
        for target, anchor in targets.items():
            if anchor.get("href") != site_i18n.counterpart(path, target) or anchor.get("hreflang") != target:
                errors.append(f"{rel}: {target.upper()} language link must point to {site_i18n.counterpart(path, target)}")
            if (anchor.get("aria-current") == "true") != (target == lang):
                errors.append(f"{rel}: aria-current must mark the {lang.upper()} language link only")

    # Internal page links stay in the page language (assets and files excepted).
    for anchor in parser.anchors:
        href = anchor.get("href") or ""
        if anchor.get("data-lang-link") or not is_page_link(href):
            continue
        if site_i18n.is_es(urlsplit(site_relative(href)).path) != (lang == "es"):
            errors.append(f"{rel}: internal link {href} is not a {lang.upper()} page")
        if "lang" in parse_qs(urlsplit(href).query):
            errors.append(f"{rel}: internal link {href} carries the legacy ?lang= parameter")

    # Nothing visible (text, alt/aria/title attributes, <title>, descriptions) reads as the other language.
    for text in {norm(t) for t in parser.texts if norm(t)}:
        if looks_like(text, other):
            errors.append(f"{rel}: {'English' if other == 'en' else 'Spanish'}-looking text on a {lang.upper()} page: {text[:90]!r}")
    # The English tagline keeps lang="en" on Spanish pages (screen readers, language detection).
    if lang == "es" and source.count(f">{TAGLINE}<") != source.count(f' lang="en">{TAGLINE}<'):
        errors.append(f"{rel}: the tagline {TAGLINE!r} needs lang=\"en\" on a Spanish page")

    # No English UI strings on Spanish pages.
    if lang == "es":
        nodes = [norm(text) for text in parser.texts if norm(text)]
        joined = " ".join(nodes)
        node_set = set(nodes)
        for text, words in english_strings():
            if (words >= 3 and text in joined) or (words < 3 and text in node_set):
                errors.append(f"{rel}: English text on a Spanish page: {text[:90]!r}")

    # Structured data in the page language.
    nodes = json_ld_nodes(source)
    types = {node.get("@type") for node in nodes}
    missing = EXPECTED_TYPES.get(kind, set()) - types
    if lang == "es" and kind == "home":
        missing |= {"WebPage", "FAQPage"} - types
    if missing:
        errors.append(f"{rel}: JSON-LD is missing {sorted(missing)}")
    languages = [node.get("inLanguage") for node in nodes if "inLanguage" in node]
    if lang == "es" and kind != "legal":
        if "es" not in languages:
            errors.append(f"{rel}: no JSON-LD node with inLanguage 'es'")
        if any(value != "es" for value in languages):
            errors.append(f"{rel}: JSON-LD inLanguage must be 'es' on Spanish pages, found {languages}")
    elif any(value == "es" or value == ["es"] for value in languages):
        errors.append(f"{rel}: Spanish-only JSON-LD inLanguage on an English page")
    for node in nodes:
        identifier = node.get("@id") or ""
        if identifier.endswith("#business") and identifier != site_i18n.BUSINESS_ID:
            errors.append(f"{rel}: business @id must stay {site_i18n.BUSINESS_ID}, found {identifier}")
        if node.get("@type") == "FAQPage":
            names = [norm(q.get("name", "")) for q in node.get("mainEntity", [])]
            if names != parser.summaries:
                errors.append(f"{rel}: FAQPage questions differ from the visible questions")
            answers = [norm((q.get("acceptedAnswer") or {}).get("text", "")) for q in node.get("mainEntity", [])]
            if len(answers) != len(parser.answers):
                errors.append(f"{rel}: FAQPage has {len(answers)} answers, the page shows {len(parser.answers)}")
            for index, (answer, visible) in enumerate(zip(answers, parser.answers), 1):
                if answer != visible:
                    errors.append(f"{rel}: FAQPage answer {index} differs from the visible answer: {answer[:60]!r}")
            if node.get("inLanguage") != lang:
                errors.append(f"{rel}: FAQPage needs inLanguage {lang!r}")

    # Contact form: same endpoint, and a hidden field with the page language.
    if kind == "home":
        if [form.get("action") for form in parser.forms] != ["https://api.web3forms.com/submit"]:
            errors.append(f"{rel}: contact form must post to https://api.web3forms.com/submit")
        language_fields = [i.get("value") for i in parser.inputs if i.get("name") == "language" and i.get("type") == "hidden"]
        if language_fields != [lang]:
            errors.append(f"{rel}: contact form needs <input type=hidden name=language value={lang}>")

    prices = bool(PRICE.search(source))
    if prices != (str(rel) in PRICE_PAGES):
        errors.append(f"{rel}: starting prices must appear on {sorted(PRICE_PAGES)} only")
    return errors


def sitemap_alternate_errors(url: str, node) -> List[str]:
    path = urlsplit(url).path or "/"
    english = site_i18n.en_path(path)
    expected = {"en": SITE + english, "es": SITE + site_i18n.es_path(english), "x-default": SITE + english}
    found = {link.get("hreflang"): link.get("href") for link in node.findall(f"{XHTML_NS}link") if link.get("rel") == "alternate"}
    if found != expected:
        return [f"sitemap.xml: {url} alternates must be {expected}, found {found}"]
    return []


def site_errors(root: Path, pages: Iterable[Path]) -> List[str]:
    """Twins on both sides: every English page has /es/ + its path and nothing else is under es/."""
    errors = []  # type: List[str]
    rels = {str(page.relative_to(root)) for page in pages}
    for rel in sorted(rels):
        twin = (rel[3:] if rel.startswith("es/") else "es/" + rel)
        if twin not in rels:
            errors.append(f"{rel}: no {('English' if rel.startswith('es/') else 'Spanish')} twin {twin} among the public pages")
    for stray in sorted((root / "es").glob("**/*.html")) if (root / "es").exists() else []:
        if str(stray.relative_to(root)) not in rels:
            errors.append(f"{stray.relative_to(root)}: Spanish file outside the public page patterns")
    return errors


def script_errors(rel: Path, text: str) -> List[str]:
    return [f"{rel}: browser-side translation code {code!r} (pages are rendered per language)" for code in FORBIDDEN_SCRIPT_CODE if code in text]
