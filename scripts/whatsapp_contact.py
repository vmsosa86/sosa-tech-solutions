"""Shared WhatsApp contact markup and page-aware prefilled messages.

Every public page tags its WhatsApp links with the page topic, so a new chat
arrives as, for example:

    Hi Sosa Tech Solutions, I'd like to talk about a website for my business. [web-websites]

The static href always carries the English message (the default language).
assets/whatsapp.js rebuilds the same message from the data-wa-* attributes
whenever the page language changes, so both encoders must stay identical.
"""

from html import escape
from urllib.parse import quote

NUMBER = "13057415702"
DISPLAY_NUMBER = "+1 (305) 741-5702"

CSS_HREF = "/assets/whatsapp.css?v=2"
JS_SRC = "/assets/whatsapp.js?v=2"

LABEL_EN = "Chat with Sosa Tech Solutions on WhatsApp"
LABEL_ES = "Escríbele a Sosa Tech Solutions por WhatsApp"
# The site speaks as Victor, so every visible WhatsApp button uses his name (service pages too).
CTA_EN = "Message Victor on WhatsApp"
CTA_ES = "Escribe a Victor por WhatsApp"

# Topic for the prefilled message, keyed by the slug in its [web-<slug>] tag.
TOPICS = {
    "home": ("my business", "mi negocio"),
    "websites": ("a website for my business", "una página web para mi negocio"),
    "whatsapp-automation": ("WhatsApp and follow-up automation", "automatizar WhatsApp y el seguimiento"),
    "content": ("content creation and publishing", "la creación y publicación de contenido"),
    "ads": ("Facebook and Instagram ads", "anuncios en Facebook e Instagram"),
    "ai-agents": ("AI agents and integrations", "agentes de IA e integraciones"),
    "ai-spokesperson": ("the AI spokesperson videos I saw on your website", "los videos con vocero de IA que vi en su página web"),
    "streaming": ("streaming and broadcasting", "streaming y transmisión"),
    "work": ("a project like the client work on your website", "un proyecto como los que vi en su página web"),
    "infrastructure": ("infrastructure and reliability", "infraestructura y confiabilidad"),
    "blog": ("my business", "mi negocio"),
    "blog-como-la-inteligencia-artificial-puede-automatizar-tu-negocio-en-miami": ("using AI in my business", "usar IA en mi negocio"),
    "blog-automatizacion-de-whatsapp-para-negocios-en-miami": ("WhatsApp automation for my business", "automatizar el WhatsApp de mi negocio"),
    "blog-por-que-tu-negocio-en-miami-necesita-un-sitio-web-rapido-y-movil": ("a faster website for my business", "una página web más rápida para mi negocio"),
    "blog-facebook-ads-vs-google-ads-para-negocios-locales": ("ads for my business", "anuncios para mi negocio"),
    "blog-que-es-n8n-y-como-puede-automatizar-tu-negocio": ("automating my business with n8n", "automatizar mi negocio con n8n"),
    "privacy-policy": ("privacy and my data", "la privacidad de mis datos"),
    "terms": ("your terms of service", "sus términos de servicio"),
    "data-deletion": ("deleting my data", "la eliminación de mis datos"),
}

# WhatsApp glyph, shared by the floating button, the nav item and the hero action.
ICON = (
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>'
    '<path d="M12 0C5.373 0 0 5.373 0 12c0 2.127.558 4.126 1.532 5.862L.057 23.486a.5.5 0 00.619.599l5.79-1.516A11.95 11.95 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.75a9.728 9.728 0 01-4.962-1.357l-.355-.212-3.685.965.983-3.596-.232-.37A9.711 9.711 0 012.25 12C2.25 6.615 6.615 2.25 12 2.25S21.75 6.615 21.75 12 17.385 21.75 12 21.75z"/>'
    "</svg>"
)


def message(language: str, topic: str, slug: str) -> str:
    if language == "es":
        return f"Hola Sosa Tech Solutions, quiero hablar sobre {topic}. [web-{slug}]"
    return f"Hi Sosa Tech Solutions, I'd like to talk about {topic}. [web-{slug}]"


def url(language: str, topic: str, slug: str) -> str:
    # Matches encodeURIComponent plus RFC 3986 escaping of !'()* in whatsapp.js.
    return f"https://wa.me/{NUMBER}?text={quote(message(language, topic, slug), safe='')}"


def topics_for(slug: str) -> tuple:
    if slug not in TOPICS:
        raise KeyError(f"No WhatsApp topic for slug {slug!r}; add it to TOPICS")
    return TOPICS[slug]


def link_attributes(slug: str) -> str:
    """href plus the data the browser needs to rebuild the message per language."""
    topic_en, topic_es = topics_for(slug)
    return (
        f'href="{escape(url("en", topic_en, slug))}" data-wa-slug="{escape(slug)}" '
        f'data-wa-topic-en="{escape(topic_en)}" data-wa-topic-es="{escape(topic_es)}" '
        'target="_blank" rel="noopener noreferrer"'
    )


def label_attributes() -> str:
    return f'aria-label="{LABEL_EN}" data-wa-label-en="{LABEL_EN}" data-wa-label-es="{LABEL_ES}"'


def floating_button(slug: str) -> str:
    # A plain wrapper, not a landmark: the link carries the (localized) accessible name.
    return (
        '<div class="wa-float">'
        f'<a class="floating-whatsapp" {link_attributes(slug)} {label_attributes()}>{ICON}</a>'
        "</div>"
    )
