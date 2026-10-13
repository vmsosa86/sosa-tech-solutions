"""Shared static navigation for service and blog pages."""
from html import escape

import whatsapp_contact

NAV_CSS_HREF = "/assets/site-nav.css?v=3"
NAV_JS_SRC = "/assets/site-nav.js?v=3"


def render_navigation(service=None, whatsapp="home"):
    """Render the inner-page nav; `whatsapp` is the page's WhatsApp topic slug."""
    contact = '/?service=' + service + '#contact' if service else '/#contact'
    links = [('/#specialist-services', 'specialists', 'AI & streaming'), ('/#solutions', 'solutions', 'Solutions'), ('/services/ai-spokesperson/', 'spokesperson', 'AI spokesperson'), ('/#proof', 'proof', 'Selected work'), ('/#about', 'about', 'About'), ('/blog/', 'blog', 'Blog')]
    current_page = f'/services/{service}/' if service else None
    current = ' aria-current="page"'
    # The sixth item is hidden only at 861-959px, where the desktop bar has no room (site-nav.css).
    extra = {'spokesperson': ' class="site-nav-spokesperson"'}
    items = ''.join(
        f'<a href="{href}"{extra.get(key, "")} data-nav-text="{key}"{current if href == current_page else ""}>{escape(label)}</a>'
        for href, key, label in links
    )
    items += f'<a class="site-nav-whatsapp" {whatsapp_contact.link_attributes(whatsapp)}>{whatsapp_contact.ICON}<span data-nav-text="whatsapp">{whatsapp_contact.CTA_EN}</span></a>'
    return f'''<nav class="site-nav" aria-label="Primary navigation">
<a class="site-nav-brand" href="/" aria-label="Sosa Tech Solutions home"><img src="/assets/logo.svg" width="180" height="46" alt="Sosa Tech Solutions"><span>We build. You grow.</span></a>
<div class="site-nav-links" id="site-nav-links">{items}</div>
<div class="site-nav-actions"><div class="site-nav-language" role="group" aria-label="Language"><button type="button" data-nav-lang="en" aria-pressed="true">EN</button><button type="button" data-nav-lang="es" aria-pressed="false">ES</button></div><a class="site-nav-cta" href="{contact}" data-nav-text="contact">Request a free review</a></div>
<button class="site-nav-toggle" type="button" aria-controls="site-nav-links" aria-expanded="false" aria-label="Open navigation menu"><span></span><span></span><span></span></button>
</nav>'''
