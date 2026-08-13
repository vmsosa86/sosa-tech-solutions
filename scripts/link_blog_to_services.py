#!/usr/bin/env python3
"""Connect each existing blog article to its most relevant service page."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

AUTOMATION = {
    "href": "/services/automation/",
    "en_title": "See the automation system",
    "en_desc": "Learn how Sosa Tech maps intake, routing, follow-up, safeguards, and ownership before automating a business process.",
    "en_button": "Explore Automate & Respond →",
    "es_title": "Conoce el sistema de automatización",
    "es_desc": "Descubre cómo Sosa Tech mapea la entrada, asignación, seguimiento, controles y responsabilidad antes de automatizar un proceso.",
    "es_button": "Ver Automatizar y Responder →",
}

PAGES = {
    "como-la-inteligencia-artificial-puede-automatizar-tu-negocio-en-miami": AUTOMATION,
    "automatizacion-de-whatsapp-para-negocios-en-miami": AUTOMATION,
    "que-es-n8n-y-como-puede-automatizar-tu-negocio": AUTOMATION,
    "por-que-tu-negocio-en-miami-necesita-un-sitio-web-rapido-y-movil": {
        "href": "/services/websites/",
        "en_title": "Build a website that creates action",
        "en_desc": "See how Sosa Tech connects a clear offer, fast mobile experience, lead capture, search foundations, and measurable inquiries.",
        "en_button": "Explore Launch & Convert →",
        "es_title": "Crea una página que genere acción",
        "es_desc": "Conoce cómo Sosa Tech conecta una oferta clara, experiencia móvil rápida, captación, SEO y consultas medibles.",
        "es_button": "Ver Lanzar y Convertir →",
    },
    "facebook-ads-vs-google-ads-para-negocios-locales": {
        "href": "/services/marketing/",
        "en_title": "Connect the system behind the click",
        "en_desc": "See how Sosa Tech connects the offer, landing page, measurement, lead routing, and follow-up before scaling traffic.",
        "en_button": "Explore Reach & Grow →",
        "es_title": "Conecta el sistema detrás del clic",
        "es_desc": "Conoce cómo Sosa Tech conecta oferta, página, medición, asignación y seguimiento antes de aumentar el tráfico.",
        "es_button": "Ver Alcanzar y Crecer →",
    },
}

ORIGINAL = {
    "en_title": "Want to automate your business?",
    "en_desc": "At Sosa Tech Solutions, we help small businesses in Miami build websites, AI systems, marketing automation, and processes that work for you.",
    "en_button": "Talk about my project →",
    "es_title": "¿Quieres automatizar tu negocio?",
    "es_desc": "En Sosa Tech Solutions ayudamos a pequeñas empresas en Miami a crear páginas web, sistemas con IA, automatización de marketing y procesos que trabajan por ti.",
    "es_button": "Hablar de mi proyecto →",
}

for slug, values in PAGES.items():
    path = ROOT / "blog" / slug / "index.html"
    text = path.read_text(encoding="utf-8")
    text = text.replace('<a class="btn" href="/#contact" data-i18n="cta.btn">', f'<a class="btn" href="{values["href"]}" data-i18n="cta.btn">')
    for language in ("en", "es"):
        for field in ("title", "desc", "button"):
            key = "btn" if field == "button" else field
            text = text.replace(
                f"'cta.{key}':'{ORIGINAL[f'{language}_{field}']}'",
                f"'cta.{key}':'{values[f'{language}_{field}']}'",
            )
    text = text.replace(ORIGINAL["en_title"], values["en_title"])
    text = text.replace(ORIGINAL["en_desc"], values["en_desc"])
    text = text.replace(ORIGINAL["en_button"], values["en_button"])
    if slug == "automatizacion-de-whatsapp-para-negocios-en-miami":
        text = text.replace(
            "<title>WhatsApp automation for Miami businesses: how to capture more customers</title>",
            "<title>WhatsApp automation for Miami businesses | Sosa Tech</title>",
        )
        text = text.replace(
            "'metaTitle':'Automatización de WhatsApp para negocios en Miami: cómo captar más clientes'",
            "'metaTitle':'Automatización de WhatsApp en Miami | Sosa Tech'",
        )
        text = text.replace(
            "'metaTitle':'WhatsApp automation for Miami businesses: how to capture more customers'",
            "'metaTitle':'WhatsApp automation for Miami businesses | Sosa Tech'",
        )
    path.write_text(text, encoding="utf-8")
    print(path.relative_to(ROOT))
