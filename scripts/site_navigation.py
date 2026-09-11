"""Shared static navigation for service and blog pages."""
from html import escape


def render_navigation(service=None):
    contact = '/?service=' + service + '#contact' if service else '/#contact'
    links = [('/#specialist-services', 'specialists', 'AI & streaming'), ('/#solutions', 'solutions', 'Solutions'), ('/#proof', 'proof', 'Selected work'), ('/#about', 'about', 'About'), ('/blog/', 'blog', 'Blog')]
    items = ''.join(f'<a href="{href}" data-nav-text="{key}">{escape(label)}</a>' for href, key, label in links)
    return f'''<nav class="site-nav" aria-label="Primary navigation">
<a class="site-nav-brand" href="/" aria-label="Sosa Tech Solutions home"><img src="/assets/logo.svg" width="180" height="38" alt="Sosa Tech Solutions"><span>We build. You grow.</span></a>
<div class="site-nav-links" id="site-nav-links">{items}</div>
<div class="site-nav-actions"><div class="site-nav-language" role="group" aria-label="Language"><button type="button" data-nav-lang="en" aria-pressed="true">EN</button><button type="button" data-nav-lang="es" aria-pressed="false">ES</button></div><a class="site-nav-cta" href="{contact}" data-nav-text="contact">Request a free review</a></div>
<button class="site-nav-toggle" type="button" aria-controls="site-nav-links" aria-expanded="false" aria-label="Open navigation menu"><span></span><span></span><span></span></button>
</nav>'''
