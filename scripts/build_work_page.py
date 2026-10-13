#!/usr/bin/env python3
"""Generate /work/ (English) and /es/work/ (Spanish): live client sites and approved testimonials.

Shares the service pages' stylesheet, script, navigation, footer and WhatsApp contact.
build_service_pages.py runs this too, so one command regenerates every generated page.
Content lives in client_work.py.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

import whatsapp_contact
import build_service_pages
from build_service_pages import FONTS_HREF, OFFERS, SERVICE_CSS_HREF, SERVICE_JS_SRC, both, finish, pick, set_language
from client_work import CLIENTS, TESTIMONIALS, WORK_IMAGE_SIZE, WORK_PAGE_SIZES, image_url, srcset
from site_i18n import BUSINESS_ID, SITE, WEBSITE_ID, counterpart
from site_navigation import NAV_CSS_HREF, NAV_JS_SRC, render_navigation

ROOT = Path(__file__).resolve().parents[1]
PATH = "/work/"
WHATSAPP = "work"

# Search snippet: title <= 60 chars ending "| Sosa Tech Solutions", description 140-155 chars.
SEO = (
    "Client Work: Miami Websites & Systems | Sosa Tech Solutions",
    "Websites and systems I built for Miami businesses and online radio stations, from a med spa and travel agencies to a nonprofit, plus what my clients say.",
)
SEO_ES = (
    "Proyectos: webs y sistemas en Miami | Sosa Tech Solutions",
    "Páginas web y sistemas que creé para negocios de Miami y radios en línea: un med spa, agencias de viajes, una fundación y más, y lo que dicen mis clientes.",
)

COPY = {
    "label": ("Client work", "Proyectos de clientes"),
    "title": ("Websites and systems I built for Miami businesses and online radio.", "Páginas web y sistemas que creé para negocios de Miami y radios en línea."),
    "lead": (
        "Nine live sites for wellness, professional services, travel, radio and a nonprofit. For several of these clients I also run the content, WhatsApp campaigns or streaming behind the site.",
        "Nueve sitios publicados para bienestar, servicios profesionales, viajes, radio y una organización sin fines de lucro. Para varios de estos clientes también manejo el contenido, las campañas por WhatsApp o el streaming detrás de la web.",
    ),
    "sites_label": ("Live sites", "Sitios publicados"),
    "sites_title": ("Real businesses. Sites you can visit.", "Negocios reales. Sitios que puedes visitar."),
    "sites_lead": (
        "Each card shows the client’s homepage on a phone and what I built. Open any site to see it in context.",
        "Cada tarjeta muestra la página de inicio del cliente en un teléfono y lo que hice. Abre cualquier sitio para verlo en contexto.",
    ),
    "visit": ("Visit site", "Ver sitio"),
    # Screen-reader suffix after "Visit site": the business name and that the link opens a new tab.
    "new_tab": ("opens in a new tab", "se abre en una pestaña nueva"),
    "quotes_label": ("In their words", "En sus palabras"),
    "quotes_title": ("What my clients say.", "Lo que dicen mis clientes."),
    "cta_label": ("Your project", "Tu proyecto"),
    "cta_title": ("Want a website or system like these? Let’s talk.", "¿Quieres una web o un sistema así? Hablemos."),
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def visit_suffix(name: str) -> str:
    """Screen-reader text, so each "Visit site" link names the business and the new tab."""
    return f'<span class="sr-only">: {esc(name)} ({both(*COPY["new_tab"])})</span>'


def render_card(client: dict) -> str:
    width, height = WORK_IMAGE_SIZE
    alt_en, alt_es = client["alt"]
    domain = client["domain"]
    return (
        '<li class="work-card">'
        f'<div class="work-shot"><img src="{image_url(domain, width)}" srcset="{srcset(domain)}" sizes="{WORK_PAGE_SIZES}" '
        f'width="{width}" height="{height}" loading="lazy" decoding="async" '
        f'alt="{esc(pick(alt_en, alt_es))}"></div>'
        f'<span class="work-tag">{both(*client["tag"])}</span>'
        f'<h3>{esc(client["name"])}</h3>'
        f'<p>{both(*client["built"])}</p>'
        f'<a class="work-visit" href="https://{domain}/" target="_blank" rel="noopener">{both(*COPY["visit"])}'
        f'<span aria-hidden="true">↗</span>{visit_suffix(client["name"])}</a>'
        "</li>"
    )


def render_quote(item: dict) -> str:
    return (
        '<figure class="quote-card">'
        f'<blockquote><p>{both(*item["quote"])}</p></blockquote>'
        f'<figcaption><strong>{esc(item["name"])}</strong><span>{esc(item["business"])}</span></figcaption>'
        "</figure>"
    )


def schema(description: str, lang: str) -> dict:
    url = SITE + counterpart(PATH, lang)
    name = pick(*COPY["label"])
    items = [
        {"@type": "ListItem", "position": i, "item": {"@type": "WebSite", "name": c["name"], "url": f'https://{c["domain"]}/', "creator": {"@id": BUSINESS_ID}}}
        for i, c in enumerate(CLIENTS, 1)
    ]
    return {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "CollectionPage", "@id": f"{url}#page", "url": url, "name": name, "description": description,
             "inLanguage": lang, "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": BUSINESS_ID},
             "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": pick("Home", "Inicio"), "item": SITE + counterpart("/", lang)},
                {"@type": "ListItem", "position": 2, "name": name, "item": url}]},
        ],
    }


def render(lang: str = "en") -> str:
    set_language(lang)
    seo = SEO_ES if lang == "es" else SEO
    title, description = (esc(value) for value in seo)
    whatsapp_link = whatsapp_contact.link_attributes(WHATSAPP, lang)
    url = SITE + counterpart(PATH, lang)
    review = 'href="/#contact"'
    cards = "".join(render_card(client) for client in CLIENTS)
    quotes = "".join(render_quote(item) for item in TESTIMONIALS)
    more = "".join(f'<a href="/services/{item["slug"]}/">{both(item["name"], item["name_es"])}</a>' for item in OFFERS)
    page = f'''<!DOCTYPE html>
<html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}"><meta name="robots" content="index,follow">
<link rel="canonical" href="{url}"><meta name="theme-color" content="#080A0F">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:image" content="https://sosatechsolutions.com/og-image-2026-10b.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{description}"><meta name="twitter:image" content="https://sosatechsolutions.com/og-image-2026-10b.png">
<link rel="icon" href="/favicon.ico"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS_HREF}"><link rel="stylesheet" href="{SERVICE_CSS_HREF}">
<script type="application/ld+json">{json.dumps(schema(seo[1], lang), ensure_ascii=False, separators=(',', ':'))}</script>
<link rel="stylesheet" href="{NAV_CSS_HREF}"><link rel="stylesheet" href="{whatsapp_contact.CSS_HREF}">
</head><body class="has-site-nav work-page">
<a class="skip" href="#main">{both('Skip to content', 'Saltar al contenido')}</a>
{render_navigation(whatsapp=WHATSAPP, current=PATH, lang=lang)}
<main id="main">
<header class="hero hero-single"><div><div class="label">{both(*COPY['label'])}</div><h1>{both(*COPY['title'])}</h1><p class="hero-copy">{both(*COPY['lead'])}</p><div class="actions"><a class="primary" {review}>{both("Request my free review", "Solicitar revisión gratuita")}</a><a class="secondary" {whatsapp_link}>{both("Message Victor on WhatsApp", "Escribe a Victor por WhatsApp")}</a></div></div></header>
<section class="work-sites" id="sites" aria-labelledby="sites-title"><div class="work-intro"><div><div class="label">{both(*COPY['sites_label'])}</div><h2 id="sites-title">{both(*COPY['sites_title'])}</h2></div><p class="lead">{both(*COPY['sites_lead'])}</p></div><ul class="work-grid" role="list">{cards}</ul></section>
<section class="work-quotes" id="testimonials" aria-labelledby="testimonials-title"><div class="work-intro"><div><div class="label">{both(*COPY['quotes_label'])}</div><h2 id="testimonials-title">{both(*COPY['quotes_title'])}</h2></div></div><div class="quote-grid">{quotes}</div></section>
<section class="cta"><div><div class="label">{both(*COPY['cta_label'])}</div><h2>{both(*COPY['cta_title'])}</h2></div><div class="cta-actions"><a class="primary" {review}>{both("Request my free review", "Solicitar revisión gratuita")}</a><a class="primary cta-whatsapp whatsapp-action" {whatsapp_link}>{whatsapp_contact.ICON}{both("Message Victor on WhatsApp", "Escribe a Victor por WhatsApp")}</a></div></section>
<section class="more"><div class="label">{both('Explore capabilities', 'Explora capacidades')}</div><div class="more-grid">{more}</div></section>
</main>
<footer><span>© 2026 Sosa Tech Solutions · Miami, Florida</span><span><a href="/privacy-policy/">{both('Privacy', 'Privacidad')}</a> · <a href="/terms/">{both('Terms', 'Términos')}</a> · <a href="/blog/">Blog</a></span></footer>
{whatsapp_contact.floating_button(WHATSAPP, lang)}
<script src="{SERVICE_JS_SRC}" defer></script><script src="{NAV_JS_SRC}" defer></script><script src="{whatsapp_contact.JS_SRC}" defer></script></body></html>'''
    return finish(page, counterpart(PATH, lang))


if __name__ == "__main__":
    # The work page is built with the services (same template pieces): run build_service_pages.py.
    for rel in build_service_pages.write():
        print(rel)
