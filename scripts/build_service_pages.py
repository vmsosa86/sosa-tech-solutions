#!/usr/bin/env python3
"""Generate bilingual, SEO-focused service pages from one controlled template."""

from __future__ import annotations

import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OFFERS = [
    {
        "slug": "websites",
        "name": "Launch & Convert",
        "name_es": "Lanzar y Convertir",
        "title": "Websites built to <em>create action.</em>",
        "title_es": "Páginas web creadas para <em>generar acción.</em>",
        "meta": "Conversion-focused websites and landing pages for Miami small businesses, with fast mobile performance, lead capture, analytics, and clear ownership.",
        "meta_es": "Páginas web y landing pages para pequeños negocios en Miami, con rendimiento móvil, captación de oportunidades, analítica y propiedad clara.",
        "intro": "A good website makes the offer easy to understand, gives each visitor a useful next step, and tells the business which channels create real inquiries.",
        "intro_es": "Una buena página web facilita entender la oferta, le da a cada visitante un siguiente paso útil y muestra qué canales generan consultas reales.",
        "signal": "VISIT -> ACTION -> LEAD",
        "outcomes": [
            ("Clear offer", "Organize the page around the buyer's question, the useful result, and one primary action.", "Oferta clara", "Organizamos la página según la pregunta del cliente, el resultado útil y una acción principal."),
            ("Fast mobile experience", "Build lean pages that remain readable, responsive, and direct on the device customers use most.", "Experiencia móvil rápida", "Creamos páginas ligeras, legibles y directas en el dispositivo que más usa el cliente."),
            ("Measurable inquiries", "Connect forms, WhatsApp links, campaign parameters, and conversion events to the follow-up process.", "Consultas medibles", "Conectamos formularios, WhatsApp, parámetros de campaña y conversiones con el seguimiento."),
        ],
        "proof": [
            ("Conversion structure", "Offer hierarchy, mobile-first layouts, focused calls to action, and practical forms.", "Estructura de conversión", "Jerarquía de oferta, diseño móvil, llamadas a la acción y formularios prácticos."),
            ("Search foundations", "Unique metadata, structured data, internal links, sitemap coverage, and useful service content.", "Base para búsquedas", "Metadatos únicos, datos estructurados, enlaces internos, sitemap y contenido útil."),
        ],
        "faq": [
            ("Do you only build WordPress websites?", "No. We choose the simplest maintainable platform for the actual content, integration, and ownership needs.", "¿Solo crean páginas en WordPress?", "No. Elegimos la plataforma más sencilla y mantenible según el contenido, las integraciones y la propiedad."),
            ("Can you improve an existing website?", "Yes. A focused audit can identify positioning, speed, mobile, SEO, tracking, and conversion priorities before a rebuild is considered.", "¿Pueden mejorar una página existente?", "Sí. Una auditoría puede priorizar posicionamiento, velocidad, móvil, SEO, medición y conversión antes de considerar un reemplazo."),
            ("Who owns the website?", "The scope defines ownership and access. Whenever practical, the client owns the domain, hosting, analytics, and business accounts.", "¿Quién es dueño de la página?", "El alcance define la propiedad y el acceso. Siempre que sea práctico, el cliente posee el dominio, hosting, analítica y cuentas del negocio."),
        ],
    },
    {
        "slug": "automation",
        "name": "Automate & Respond",
        "name_es": "Automatizar y Responder",
        "title": "Every lead needs a <em>clear next step.</em>",
        "title_es": "Cada oportunidad necesita un <em>siguiente paso claro.</em>",
        "meta": "WhatsApp, CRM, n8n, and AI workflow automation for Miami small businesses that need faster lead routing, follow-up, and visibility.",
        "meta_es": "Automatización de WhatsApp, CRM, n8n e IA para pequeños negocios en Miami que necesitan asignación, seguimiento y visibilidad.",
        "intro": "We connect intake, routing, alerts, reminders, and follow-up state so opportunities do not depend on copying, memory, or one person's inbox.",
        "intro_es": "Conectamos la entrada, asignación, alertas, recordatorios y estado para que las oportunidades no dependan de copiar, recordar o una sola bandeja.",
        "signal": "CAPTURE -> ROUTE -> RESPOND",
        "outcomes": [
            ("Faster response", "Route each inquiry to the right person with the context needed to act.", "Respuesta más rápida", "Asignamos cada consulta a la persona correcta con el contexto necesario."),
            ("Less repetitive work", "Remove manual copying, duplicate alerts, repeated status checks, and avoidable reminders.", "Menos trabajo repetitivo", "Eliminamos copias manuales, alertas duplicadas, revisiones repetidas y recordatorios evitables."),
            ("Visible ownership", "Record who owns the next action, whether a response happened, and what remains open.", "Responsabilidad visible", "Registramos quién tiene la próxima acción, si hubo respuesta y qué sigue pendiente."),
        ],
        "proof": [
            ("Workflow safeguards", "Validation, deduplication, opt-out handling, bounded retries, alerts, and human escalation.", "Controles del flujo", "Validación, deduplicación, respeto a bajas, reintentos limitados, alertas y escalamiento humano."),
            ("Practical stack", "WhatsApp, forms, CRMs, n8n, databases, email, calendars, and AI connected only where useful.", "Tecnología práctica", "WhatsApp, formularios, CRM, n8n, bases de datos, correo, calendarios e IA conectados solo donde ayudan."),
        ],
        "faq": [
            ("Does automation replace the person serving the customer?", "No. The useful goal is to make sure the right person receives context and can respond, not to hide the relationship behind a bot.", "¿La automatización reemplaza a quien atiende?", "No. El objetivo es que la persona correcta reciba contexto y pueda responder, no esconder la relación detrás de un bot."),
            ("Can you connect our current tools?", "Usually. We first map what already works, available APIs, permissions, data ownership, and failure paths.", "¿Pueden conectar nuestras herramientas actuales?", "Normalmente sí. Primero mapeamos lo que funciona, las API, permisos, propiedad de datos y posibles fallas."),
            ("Can AI be part of the workflow?", "Yes, when it has a bounded role such as classification, summarization, drafting, or retrieval, with review and fallback paths where needed.", "¿La IA puede ser parte del flujo?", "Sí, cuando tiene una función limitada como clasificar, resumir, redactar o buscar, con revisión y alternativas cuando sea necesario."),
        ],
    },
    {
        "slug": "content-engine",
        "name": "Create & Publish",
        "name_es": "Crear y Publicar",
        "title": "Consistent content with <em>your approval built in.</em>",
        "title_es": "Contenido constante con <em>tu aprobación incluida.</em>",
        "meta": "AI-assisted social media content creation and scheduling for Miami small businesses, with bilingual posts, Reels, human approval, and verified publishing.",
        "meta_es": "Creación y programación de contenido para redes con IA para pequeños negocios en Miami, con posts bilingües, Reels, aprobación humana y publicación verificada.",
        "intro": "We turn your audience, offers, brand rules, and real business moments into a repeatable content cycle—without letting an AI publish on its own.",
        "intro_es": "Convertimos tu público, ofertas, reglas de marca y momentos reales del negocio en un ciclo de contenido constante, sin dejar que una IA publique por su cuenta.",
        "signal": "IDEA -> APPROVAL -> PUBLISH -> LEARN",
        "outcomes": [
            ("A usable content plan", "Organize themes, formats, offers, local moments, and calls to action into a calendar the owner can understand.", "Un plan de contenido útil", "Organizamos temas, formatos, ofertas, momentos locales y llamadas a la acción en un calendario fácil de entender."),
            ("Faster production", "Use AI to assist with bilingual captions, visual directions, carousels, and Reel scripts while following defined brand rules.", "Producción más rápida", "Usamos IA para ayudar con textos bilingües, dirección visual, carruseles y guiones para Reels siguiendo reglas de marca."),
            ("Controlled publishing", "Require human approval, schedule approved assets, verify Facebook and Instagram delivery, and surface failures.", "Publicación controlada", "Exigimos aprobación humana, programamos lo aprobado, verificamos la entrega en Facebook e Instagram y mostramos las fallas."),
        ],
        "proof": [
            ("Approval before public action", "Creative review stays separate from publishing permissions, so a draft cannot become public by accident.", "Aprobación antes de publicar", "La revisión creativa se mantiene separada del permiso de publicación para evitar que un borrador se haga público por accidente."),
            ("A measurable learning loop", "Track the content, destination, publication status, and useful response signals so the next cycle has evidence behind it.", "Un ciclo de aprendizaje medible", "Registramos contenido, destino, estado de publicación y señales útiles para mejorar el próximo ciclo con evidencia."),
        ],
        "faq": [
            ("Does AI publish without our approval?", "No. Human approval is the default control before public scheduling or publishing. The approval owner and process are defined during setup.", "¿La IA publica sin nuestra aprobación?", "No. La aprobación humana es el control predeterminado antes de programar o publicar. El responsable y el proceso se definen durante la configuración."),
            ("Can the content be in English and Spanish?", "Yes. We can produce English, Spanish, or bilingual variants based on the audience and channel instead of forcing one translation everywhere.", "¿El contenido puede ser en inglés y español?", "Sí. Podemos crear versiones en inglés, español o bilingües según el público y el canal, sin imponer la misma traducción en todas partes."),
            ("Can you create Reels and ads too?", "Yes. The system can include concepts, scripts, shot lists, editing direction, static assets, Reels, and approved organic ideas prepared for paid testing. Ad spend and activation remain separately approved.", "¿También pueden crear Reels y anuncios?", "Sí. El sistema puede incluir conceptos, guiones, listas de tomas, edición, imágenes, Reels e ideas orgánicas listas para probar como anuncios. El presupuesto y la activación se aprueban por separado."),
        ],
    },
    {
        "slug": "marketing",
        "name": "Reach & Grow",
        "name_es": "Alcanzar y Crecer",
        "title": "Marketing connected to the <em>system behind the click.</em>",
        "title_es": "Marketing conectado con el <em>sistema detrás del clic.</em>",
        "meta": "Meta and Google lead-generation systems for Miami small businesses, connecting campaigns, landing pages, tracking, routing, and reporting.",
        "meta_es": "Sistemas de generación de oportunidades en Meta y Google para negocios en Miami, conectando campañas, páginas, medición y seguimiento.",
        "intro": "Campaigns work better when the offer, landing page, measurement, response process, and lead owner are ready before more traffic arrives.",
        "intro_es": "Las campañas funcionan mejor cuando la oferta, la página, la medición, la respuesta y el responsable están listos antes de recibir más tráfico.",
        "signal": "ATTENTION -> INQUIRY -> FOLLOW-UP",
        "outcomes": [
            ("Offer readiness", "Clarify the audience, problem, promise, proof, and next action before building the campaign.", "Oferta preparada", "Aclaramos público, problema, promesa, prueba y siguiente acción antes de crear la campaña."),
            ("Connected measurement", "Use campaign parameters and verified events so reporting can connect attention to real actions.", "Medición conectada", "Usamos parámetros y eventos verificados para conectar la atención con acciones reales."),
            ("Operational follow-up", "Make lead destination, ownership, response status, and opt-out handling part of the campaign design.", "Seguimiento operativo", "Incluimos destino, responsable, estado de respuesta y bajas en el diseño de la campaña."),
        ],
        "proof": [
            ("Meta publishing operations", "Approved asset delivery, page-token handling, Facebook and Instagram status checks, and confirmation paths.", "Operación de publicaciones", "Entrega de contenido aprobado, manejo de tokens, revisión de estado y confirmación en Facebook e Instagram."),
            ("Guarded campaign systems", "Paused-first controls, audience review, opt-out enforcement, and reporting that does not depend on memory.", "Campañas con controles", "Controles antes de activar, revisión de público, respeto a bajas y reportes que no dependen de la memoria."),
        ],
        "faq": [
            ("Should we start advertising immediately?", "Not always. We first verify the offer, landing page, tracking, follow-up, account health, and budget controls.", "¿Debemos anunciar de inmediato?", "No siempre. Primero verificamos oferta, página, medición, seguimiento, estado de la cuenta y controles de presupuesto."),
            ("Do you guarantee leads or sales?", "No. We do not invent guarantees. We define the controllable system, measure real behavior, and improve from verified evidence.", "¿Garantizan prospectos o ventas?", "No. No inventamos garantías. Definimos el sistema controlable, medimos comportamiento real y mejoramos con evidencia verificada."),
            ("Can you create the content too?", "Yes. Strategy, scripts, bilingual copy, visual templates, static assets, Reels, and production workflows can be included.", "¿También pueden crear el contenido?", "Sí. Podemos incluir estrategia, guiones, texto bilingüe, plantillas, imágenes, Reels y flujos de producción."),
        ],
    },
    {
        "slug": "infrastructure",
        "name": "Run Reliably",
        "name_es": "Operar con Confianza",
        "title": "Infrastructure with <em>clear recovery ownership.</em>",
        "title_es": "Infraestructura con <em>recuperación claramente asignada.</em>",
        "meta": "Managed VPS, Docker, Cloudflare, monitoring, encrypted backups, and restore testing for small-business systems and media operations.",
        "meta_es": "VPS, Docker, Cloudflare, monitoreo, respaldos cifrados y pruebas de restauración para sistemas y medios de pequeños negocios.",
        "intro": "Reliable operations require more than a running server. Services need health checks, alerts, protected backups, tested recovery, and a person who owns the response.",
        "intro_es": "Una operación confiable requiere más que un servidor encendido. Necesita controles de salud, alertas, respaldos protegidos, recuperación probada y un responsable.",
        "signal": "OBSERVE -> PROTECT -> RECOVER",
        "outcomes": [
            ("Visible health", "Monitor the external service and the internal dependencies that customers actually need.", "Salud visible", "Monitoreamos el servicio externo y las dependencias internas que el cliente realmente necesita."),
            ("Protected data", "Use encrypted off-site backups, defined retention, verification, and access controls.", "Datos protegidos", "Usamos respaldos externos cifrados, retención definida, verificación y controles de acceso."),
            ("Tested recovery", "Document and exercise the restoration path instead of assuming a backup can be used.", "Recuperación probada", "Documentamos y ejercitamos la restauración en lugar de asumir que el respaldo funciona."),
        ],
        "proof": [
            ("Operational discipline", "Containerized services, controlled secrets, monitoring, change checkpoints, and documented ownership.", "Disciplina operativa", "Servicios en contenedores, secretos controlados, monitoreo, checkpoints y responsabilidad documentada."),
            ("Recovery lifecycle", "Encrypt, transfer off-site, retain, verify, restore-test, and record the result.", "Ciclo de recuperación", "Cifrar, transferir, retener, verificar, probar restauración y registrar el resultado."),
        ],
        "faq": [
            ("Do you manage existing servers?", "Yes, after a read-only assessment of access, services, backups, monitoring, exposure, and current ownership.", "¿Administran servidores existentes?", "Sí, después de evaluar acceso, servicios, respaldos, monitoreo, exposición y responsabilidad actual."),
            ("Is a backup enough?", "No. A backup becomes useful only when it is protected, recent, verified, and connected to a tested restoration procedure.", "¿Un respaldo es suficiente?", "No. Solo es útil si está protegido, reciente, verificado y conectado a un procedimiento de restauración probado."),
            ("Can you use Cloudflare and Docker?", "Yes. We use them when they simplify security, routing, deployment, recovery, or maintenance for the actual system.", "¿Pueden usar Cloudflare y Docker?", "Sí. Los usamos cuando simplifican seguridad, rutas, despliegue, recuperación o mantenimiento del sistema real."),
        ],
    },
    {
        "slug": "streaming",
        "name": "Stream & Broadcast",
        "name_es": "Transmitir y Difundir",
        "title": "Live media built for <em>stable delivery.</em>",
        "title_es": "Medios en vivo creados para una <em>entrega estable.</em>",
        "meta": "Radio and live-streaming infrastructure using RTMP, HLS, Icecast, FFmpeg, monitoring, and maintainable media workflows.",
        "meta_es": "Infraestructura de radio y streaming en vivo con RTMP, HLS, Icecast, FFmpeg, monitoreo y flujos de medios mantenibles.",
        "intro": "We build and support the path from ingest to processing to delivery, with clear health checks, operational handoff, and recovery for live-media systems.",
        "intro_es": "Construimos y apoyamos la ruta desde la entrada hasta el procesamiento y entrega, con controles de salud, operación clara y recuperación para medios en vivo.",
        "signal": "INGEST -> PROCESS -> DELIVER",
        "outcomes": [
            ("Stable ingest", "Define source, authentication, format, expected availability, and fallback behavior.", "Entrada estable", "Definimos fuente, autenticación, formato, disponibilidad esperada y alternativas."),
            ("Controlled processing", "Use FFmpeg and media services with bounded resources, health checks, and readable logs.", "Procesamiento controlado", "Usamos FFmpeg y servicios de medios con recursos limitados, controles de salud y registros claros."),
            ("Maintainable delivery", "Serve RTMP, HLS, Icecast, or related outputs with monitoring and a practical operating guide.", "Entrega mantenible", "Entregamos RTMP, HLS, Icecast u otras salidas con monitoreo y una guía práctica."),
        ],
        "proof": [
            ("Media operations", "Radio, audio processing, video relay, ingest, transcoding, and delivery systems with clear ownership.", "Operación de medios", "Radio, audio, retransmisión, entrada, transcodificación y entrega con responsables claros."),
            ("Reliability around the stream", "Monitoring, containers, alerts, backups, change records, and failure-path testing around the media pipeline.", "Confiabilidad del sistema", "Monitoreo, contenedores, alertas, respaldos, registro de cambios y pruebas de fallas alrededor del flujo."),
        ],
        "faq": [
            ("Do you support internet radio?", "Yes. Icecast, audio processing, source management, monitoring, and the surrounding website or automation can be included.", "¿Trabajan con radio por internet?", "Sí. Podemos incluir Icecast, audio, fuentes, monitoreo y la página o automatización relacionada."),
            ("Can you troubleshoot an unstable stream?", "Yes. We inspect the full path: source, network, processing, resources, protocol, delivery, monitoring, and operator procedure.", "¿Pueden revisar un stream inestable?", "Sí. Revisamos fuente, red, procesamiento, recursos, protocolo, entrega, monitoreo y operación."),
            ("Do you provide ongoing monitoring?", "Yes. The support scope can define checks, alerts, response ownership, maintenance windows, and escalation.", "¿Ofrecen monitoreo continuo?", "Sí. El soporte puede definir controles, alertas, responsables, ventanas de mantenimiento y escalamiento."),
        ],
    },
]

STEPS = [
    ("Map", "Understand the business process, current tools, people, risk, and useful outcome.", "Mapear", "Entender el proceso, herramientas, personas, riesgo y resultado útil."),
    ("Scope", "Define deliverables, owner, dependencies, timing, acceptance, and cost before building.", "Definir", "Acordar entregables, responsable, dependencias, tiempo, aceptación y costo."),
    ("Build", "Implement the smallest maintainable system that solves the real bottleneck.", "Construir", "Implementar el sistema mantenible más pequeño que resuelve el obstáculo real."),
    ("Verify", "Test the happy path, alerts, handoff, failure behavior, and recovery before sign-off.", "Verificar", "Probar la ruta normal, alertas, entrega, fallas y recuperación antes de aprobar."),
]


def both(en: str, es: str, tag: str = "span") -> str:
    en = en.replace("&", "&amp;")
    es = es.replace("&", "&amp;")
    return f'<{tag} data-lang="en">{en}</{tag}><{tag} data-lang="es" hidden>{es}</{tag}>'


def render(offer: dict) -> str:
    url = f"https://sosatechsolutions.com/services/{offer['slug']}/"
    faq_entities = []
    for en_q, en_a, _, _ in offer["faq"]:
        faq_entities.append({"@type": "Question", "name": en_q, "acceptedAnswer": {"@type": "Answer", "text": en_a}})
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Service", "name": offer["name"], "description": offer["meta"], "url": url, "provider": {"@type": "LocalBusiness", "name": "Sosa Tech Solutions", "url": "https://sosatechsolutions.com/", "areaServed": "Miami and South Florida"}},
            {"@type": "FAQPage", "mainEntity": faq_entities},
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://sosatechsolutions.com/"}, {"@type": "ListItem", "position": 2, "name": offer["name"], "item": url}]},
        ],
    }
    outcomes = "".join(f'<article class="outcome"><div class="num">0{i}</div><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(offer["outcomes"], 1))
    steps = "".join(f'<article class="step"><b>0{i}</b><div><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></div></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(STEPS, 1))
    proof = "".join(f'<article class="proof-card"><b>{"OPERATING PROOF" if i == 1 else "BUILD PRINCIPLE"}</b><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(offer["proof"], 1))
    faq = "".join(f'<details><summary>{both(en_q, es_q)}</summary><p>{both(en_a, es_a)}</p></details>' for en_q, en_a, es_q, es_a in offer["faq"])
    more_links = []
    for item in OFFERS:
        current = 'aria-current="page"' if item["slug"] == offer["slug"] else ""
        more_links.append(f'<a href="/services/{item["slug"]}/" {current}>{both(item["name"], item["name_es"])}</a>')
    more = "".join(more_links)
    name = html.escape(offer["name"])
    meta = html.escape(offer["meta"], quote=True)
    return f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} | Sosa Tech Solutions Miami</title>
<meta name="description" content="{meta}"><meta name="robots" content="index,follow">
<link rel="canonical" href="{url}"><meta name="theme-color" content="#080A0F">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:title" content="{name} | Sosa Tech Solutions"><meta property="og:description" content="{meta}"><meta property="og:image" content="https://sosatechsolutions.com/og-image.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{name} | Sosa Tech Solutions"><meta name="twitter:description" content="{meta}"><meta name="twitter:image" content="https://sosatechsolutions.com/og-image.png">
<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/service.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
</head><body>
<a class="skip" href="#main">Skip to content</a>
<nav aria-label="Main navigation"><a class="brand" href="/"><strong>Sosa<span>Tech</span></strong><small>We build. You grow.</small></a><div class="nav-actions"><div class="lang" role="group" aria-label="Language"><button type="button" data-set-lang="en" aria-pressed="true">EN</button><button type="button" data-set-lang="es" aria-pressed="false">ES</button></div><a class="nav-cta" href="/#contact">{both('Free Lead-Flow Review','Revisión Gratuita')}</a></div></nav>
<main id="main">
<header class="hero"><div><div class="label">{both(offer['name'], offer['name_es'])}</div><h1>{both(offer['title'], offer['title_es'])}</h1><p class="hero-copy">{both(offer['meta'], offer['meta_es'])}</p><div class="actions"><a class="primary" href="/#contact">{both('Book a Free Lead-Flow Review','Solicita una Revisión Gratuita')}</a><a class="secondary" href="https://wa.me/13057415702" target="_blank" rel="noopener noreferrer">{both('Message us on WhatsApp ->','Escríbenos por WhatsApp ->')}</a></div></div><div class="signal" aria-hidden="true"><strong>{offer['signal']}</strong></div></header>
<section class="intro"><div><div class="label">{both('The useful outcome','El resultado útil')}</div><h2>{both('Start with the result.','Empieza con el resultado.')}</h2></div><div><p class="lead">{both(offer['intro'], offer['intro_es'])}</p><div class="outcomes">{outcomes}</div></div></section>
<section class="process"><div><div class="label">{both('How we work','Cómo trabajamos')}</div><h2>{both('Simple process.<br>Real responsibility.','Proceso simple.<br>Responsabilidad real.')}</h2></div><div class="steps">{steps}</div></section>
<section class="proof"><div class="label">{both('Systems we operate','Sistemas que operamos')}</div><h2>{both('Credibility without<br>invented results.','Credibilidad sin<br>resultados inventados.')}</h2><div class="proof-grid">{proof}</div></section>
<section class="faq"><div><div class="label">FAQ</div><h2>{both('Clear answers<br>before we build.','Respuestas claras<br>antes de construir.')}</h2></div><div class="faq-list">{faq}</div></section>
<section class="cta"><div><div class="label">{both('Free lead-flow review','Revisión gratuita del flujo')}</div><h2>{both('Show us where the process gets stuck.','Muéstranos dónde se atasca el proceso.')}</h2></div><a class="primary" href="/#contact">{both('Book the review ->','Solicitar revisión ->')}</a></section>
<section class="more"><div class="label">{both('Explore capabilities','Explora capacidades')}</div><div class="more-grid">{more}</div></section>
</main>
<footer><span>© 2026 Sosa Tech Solutions · Miami, Florida</span><span><a href="/privacy-policy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/blog/">Blog</a></span></footer>
<script src="/assets/service.js" defer></script></body></html>'''


if __name__ == "__main__":
    for item in OFFERS:
        target = ROOT / "services" / item["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(item), encoding="utf-8")
        print(target.relative_to(ROOT))
