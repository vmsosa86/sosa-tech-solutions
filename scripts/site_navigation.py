"""Shared static navigation for service, work and blog pages, in English or Spanish."""
from html import escape

import whatsapp_contact
from site_i18n import en_path, localize_href, switch_links

NAV_CSS_HREF = "/assets/site-nav.css?v=6"
NAV_JS_SRC = "/assets/site-nav.js?v=6"

# The only copy of the navigation labels (the pages are rendered per language).
NAV_LABELS = {
    "en": {"specialists": "AI & streaming", "solutions": "Solutions", "spokesperson": "AI spokesperson", "work": "Work",
           "about": "About", "blog": "Blog", "contact": "Request a free review", "open": "Open navigation menu",
           "close": "Close navigation menu", "nav": "Primary navigation", "home": "Sosa Tech Solutions home", "language": "Language"},
    "es": {"specialists": "IA y streaming", "solutions": "Soluciones", "spokesperson": "Vocero con IA", "work": "Proyectos",
           "about": "Nosotros", "blog": "Blog", "contact": "Solicitar revisión gratuita", "open": "Abrir menú de navegación",
           "close": "Cerrar menú de navegación", "nav": "Navegación principal", "home": "Inicio de Sosa Tech Solutions", "language": "Idioma"},
}
LINKS = [("/#specialist-services", "specialists"), ("/#solutions", "solutions"), ("/services/ai-spokesperson/", "spokesperson"),
         ("/work/", "work"), ("/#about", "about"), ("/blog/", "blog")]
NAV_PAGES = {"/", "/services/ai-spokesperson/", "/work/", "/blog/"}


def render_navigation(service=None, whatsapp="home", current=None, lang="en", path=None):
    """Render the inner-page nav.

    `whatsapp` is the page's WhatsApp topic slug, `current` the English path of the nav item
    to mark with aria-current (a service page marks its own path) and `path` the page's
    English path, used by the EN/ES switch.
    """
    labels = NAV_LABELS[lang]
    pages = NAV_PAGES | ({f"/services/{service}/"} if service else set())
    contact = localize_href('/?service=' + service + '#contact' if service else '/#contact', lang, pages)
    current_page = current or (f'/services/{service}/' if service else None)
    page_path = en_path(path or current_page or "/")
    aria_current = ' aria-current="page"'
    # The sixth item is hidden only at 861-959px, where the desktop bar has no room (site-nav.css).
    extra = {'spokesperson': ' class="site-nav-spokesperson"'}
    items = ''.join(
        f'<a href="{localize_href(href, lang, pages)}"{extra.get(key, "")}{aria_current if href == current_page else ""}>{escape(labels[key])}</a>'
        for href, key in LINKS
    )
    items += (f'<a class="site-nav-whatsapp" {whatsapp_contact.link_attributes(whatsapp, lang)}>{whatsapp_contact.ICON}'
              f'<span>{whatsapp_contact.CTAS[lang]}</span></a>')
    home = localize_href("/", lang, pages)
    return f'''<nav class="site-nav" aria-label="{labels['nav']}">
<a class="site-nav-brand" href="{home}" aria-label="{labels['home']}"><img src="/assets/logo.svg?v=20261013b" width="180" height="46" alt="Sosa Tech Solutions"><span lang="en">We build. You grow.</span></a>
<div class="site-nav-links" id="site-nav-links">{items}</div>
<div class="site-nav-actions"><div class="site-nav-language" role="group" aria-label="{labels['language']}">{switch_links(page_path, lang)}</div><a class="site-nav-cta" href="{contact}">{escape(labels['contact'])}</a></div>
<button class="site-nav-toggle" type="button" aria-controls="site-nav-links" aria-expanded="false" aria-label="{labels['open']}" data-label-open="{labels['open']}" data-label-close="{labels['close']}"><span></span><span></span><span></span></button>
</nav>'''
