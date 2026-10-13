#!/usr/bin/env python3
"""Generate bilingual, SEO-focused service pages from one controlled template."""

from __future__ import annotations

import json
import html
import whatsapp_contact
from site_navigation import NAV_CSS_HREF, NAV_JS_SRC, render_navigation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_CSS_HREF = "/assets/service.css?v=20261013c"
SERVICE_JS_SRC = "/assets/service.js?v=20261013c"
FONTS_HREF = "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&amp;family=DM+Sans:wght@400;500;600&amp;family=Syne:wght@700;800&amp;display=swap"

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
        "name": "Infrastructure & reliability",
        "name_es": "Infraestructura y confiabilidad",
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
        "name": "Streaming & broadcasting",
        "name_es": "Streaming y transmisión",
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


OFFERS.append({'slug': 'agents', 'name': 'AI agents & integrations', 'name_es': 'Agentes de IA e integraciones', 'title': 'Useful help, connected to your business.', 'title_es': 'Ayuda útil, conectada a tu negocio.', 'meta': 'Custom AI assistants and integrations for business questions, inquiry organization and repetitive work, with clear access and human review.', 'meta_es': 'Asistentes de IA e integraciones a medida para consultas, organización de contactos y tareas repetitivas, con acceso definido y revisión humana.', 'intro': 'Start with a task your team repeats. I can connect an assistant to approved business information and tools, define what it can do, and build the handoff to a person when needed.', 'intro_es': 'Empecemos con una tarea que tu equipo repite. Puedo conectar un asistente a información y herramientas aprobadas, definir qué puede hacer y preparar el paso a una persona cuando sea necesario.', 'signal': 'QUESTION -> CONTEXT -> REVIEW -> ACTION', 'stages': [('A question or task', 'Una pregunta o tarea'), ('Approved information', 'Información aprobada'), ('A useful response', 'Una respuesta útil'), ('Human review when needed', 'Revisión humana cuando haga falta')], 'outcomes': [('Business assistants', 'Help staff find information, summarize material and draft responses using the sources you approve.', 'Asistentes para tu equipo', 'Ayuda a encontrar información, resumir material y preparar respuestas con las fuentes que apruebes.'), ('Inquiry organization', 'Classify incoming requests, capture relevant details and route them to the right person.', 'Organización de consultas', 'Clasifica solicitudes, recopila datos relevantes y envíalos a la persona indicada.'), ('Custom integrations', 'Connect forms, databases and business tools to reduce copying and repeated manual work.', 'Integraciones a medida', 'Conecta formularios, bases de datos y herramientas para reducir copias y trabajo manual repetitivo.')], 'proof': [], 'example_title': 'An assistant that prepares the next step.', 'example_title_es': 'Un asistente que prepara el siguiente paso.', 'example': 'Example workflow: an inquiry arrives, an assistant identifies the topic and prepares a draft using approved service information. Your team reviews it before sending. We test the workflow against real scenarios before agreeing on any greater autonomy.', 'example_es': 'Ejemplo: llega una consulta, un asistente identifica el tema y prepara un borrador con información aprobada de tus servicios. Tu equipo lo revisa antes de enviarlo. Probamos situaciones reales antes de acordar mayor autonomía.', 'start': 'Bring one repetitive task and the tools involved. We review the available information, agree on permissions and costs, then scope a small first implementation.', 'start_es': 'Trae una tarea repetitiva y las herramientas que utilizas. Revisamos la información disponible, acordamos permisos y costos, y definimos una primera implementación concreta.', 'faq': [('Can the agent take actions automatically?', 'Where appropriate, yes. We define the permitted actions and review steps first. Messages, record changes and other consequential actions need an agreed approval process.', '¿El agente puede actuar automáticamente?', 'Sí, cuando sea adecuado. Primero definimos las acciones permitidas y la revisión. Los mensajes, cambios de registros y otras acciones importantes necesitan un proceso de aprobación acordado.'), ('Is this a CRM product?', 'No. This is a custom assistant or integration built around a specific task. If you already use a CRM, we can assess whether it can be connected.', '¿Es un producto CRM?', 'No. Es un asistente o integración a medida para una tarea concreta. Si ya usas un CRM, podemos evaluar su conexión.'), ('What happens if the assistant is unsure?', 'We define when it should ask for clarification or hand off to a person. The scope includes testing, access limits and ongoing platform costs.', '¿Qué pasa si el asistente no está seguro?', 'Definimos cuándo pedir aclaraciones o pasar la consulta a una persona. El alcance incluye pruebas, límites de acceso y costos recurrentes.')]})

# Primary offers use the approved homepage positioning.
PRIMARY = {
    "automation": {
        "name": "WhatsApp & follow-up automation", "name_es": "WhatsApp y seguimiento automatizado",
        "title": "An inquiry arrives. Everyone knows what happens next.", "title_es": "Llega una consulta. Todos saben qué sigue.",
        "meta": "Connect your forms, WhatsApp, alerts and reminders so your team can respond with the right information.",
        "meta_es": "Conecta formularios, WhatsApp, alertas y recordatorios para que tu equipo responda con la información necesaria.",
        "intro": "When inquiries live in separate inboxes, details get copied, messages get missed and follow-up depends on memory. I connect the handoffs around the tools your business already uses.",
        "intro_es": "Cuando las consultas quedan en distintas bandejas, se copian datos, se pierden mensajes y el seguimiento depende de la memoria. Conecto los pasos entre las herramientas que ya usa tu negocio.",
        "outcomes": [
            ("Organized inquiries", "Capture the details you need and reduce duplicate records in your existing tools or a connected database.", "Consultas organizadas", "Recopila los datos necesarios y reduce registros duplicados en tus herramientas o una base de datos conectada."),
            ("The right person alerted", "Route each inquiry with its source, contact details and the context your team needs to respond.", "Aviso a la persona indicada", "Envía cada consulta con su origen, datos de contacto y el contexto necesario para responder."),
            ("A clear next action", "Set reminders and follow-up rules, with a person responsible when something needs attention.", "Una próxima acción clara", "Define recordatorios y reglas de seguimiento, con un responsable cuando algo necesita atención.")],
        "example_title": "From a website form to a timely follow-up.", "example_title_es": "Del formulario web al seguimiento oportuno.",
        "example": "An example workflow: a customer requests information, their details are recorded, your team receives an alert, and a reminder prompts the next action. The exact steps depend on your tools and how you serve customers.",
        "example_es": "Un ejemplo: un cliente pide información, se registran sus datos, tu equipo recibe una alerta y un recordatorio indica la próxima acción. Los pasos se adaptan a tus herramientas y tu forma de atender.",
        "stages": [("Inquiry received", "Consulta recibida"),("Details organized", "Datos organizados"),("Team notified", "Equipo avisado"),("Follow-up reminder", "Recordatorio de seguimiento")],
        "start": "Bring one process that takes too much manual work. We map it together, identify the first useful connection and define the scope before implementation.",
        "start_es": "Trae un proceso que requiera demasiado trabajo manual. Lo revisamos juntos, identificamos la primera conexión útil y acordamos el alcance antes de implementarlo.",
        "faq": [
            ("Do I need to buy a CRM?", "Not necessarily. I can connect your existing tools and organize the data behind them. This service is custom integration and automation; it does not include a standalone CRM application.", "¿Necesito comprar un CRM?", "No necesariamente. Puedo conectar tus herramientas y organizar sus datos. El servicio es de integración y automatización a medida; no incluye una aplicación CRM independiente."),
            ("Will customers still speak with a person?", "Yes. We decide which steps can be automated and when your team takes over, with the information needed to continue the conversation.", "¿Los clientes seguirán hablando con una persona?", "Sí. Definimos qué pasos automatizar y cuándo interviene tu equipo, con la información necesaria para continuar la conversación."),
            ("Can you work with what we already use?", "I first check the available connections and account access. Any new tool, ongoing platform cost or limitation is included in the proposed scope.", "¿Puedes trabajar con lo que ya usamos?", "Primero reviso las conexiones disponibles y los accesos. La propuesta detalla cualquier herramienta nueva, costo recurrente o limitación.")]
    },
    "websites": {
        "name": "Websites", "name_es": "Páginas web",
        "title": "A website that makes the next step easy.", "title_es": "Una web que facilita el siguiente paso.",
        "meta": "A clear, polished website built around your offer and the way customers contact you. Designed for mobile, in English and Spanish when needed.",
        "meta_es": "Una web clara y cuidada, centrada en tu oferta y en cómo te contactan tus clientes. Diseñada para móvil, en inglés y español cuando lo necesites.",
        "example_title": "Mocasa Hair Transplant", "example_title_es": "Mocasa Hair Transplant",
        "example": "A real service website that brings treatment information and consultation calls to action into one experience. Explore the live site to see the design and content in context.",
        "example_es": "Una web de servicios que reúne información de tratamientos y opciones para solicitar una consulta. Visita la página para ver el diseño y el contenido en contexto.",
        "image": "/assets/site/project-mocasa-website.jpg", "image_alt": "Mocasa Hair Transplant website", "image_alt_es": "Página web de Mocasa Hair Transplant", "url": "https://mocasahairtransplant.com/",
        "start": "Share your current website, or the offer you want to launch. We identify the pages, content and contact flow you need, then agree on scope and cost.",
        "start_es": "Comparte tu web actual o la oferta que quieres lanzar. Identificamos las páginas, el contenido y la forma de contacto que necesitas; después acordamos alcance y costo."
    },
    "marketing": {
        "name": "Facebook & Instagram ads", "name_es": "Anuncios en Facebook e Instagram",
        "title": "Give your next customer a reason to get in touch.", "title_es": "Dale a tu próximo cliente una razón para contactarte.",
        "meta": "Facebook and Instagram campaigns connected to a clear offer, a useful landing page or WhatsApp, and a plan for following up.",
        "meta_es": "Campañas en Facebook e Instagram conectadas a una oferta clara, una página de destino o WhatsApp y un plan de seguimiento.",
        "outcomes": [
            ("Campaign plan", "Define the offer, audience, creative direction and agreed advertising budget before launch.", "Plan de campaña", "Define la oferta, el público, la dirección creativa y el presupuesto antes del lanzamiento."),
            ("A connected destination", "Match the ad to a landing page or WhatsApp conversation, with a clear contact path and measurement setup.", "Un destino conectado", "Conecta el anuncio con una página o conversación en WhatsApp, con un contacto claro y medición."),
            ("Review and improvement", "Review campaign performance and inquiry quality together to guide the next test.", "Revisión y mejoras", "Revisamos el rendimiento y la calidad de las consultas para decidir qué probar después.")],
        "example_title": "Plan the conversation beyond the click.", "example_title_es": "Planifica la conversación después del clic.",
        "example": "For a service business, a campaign might introduce one offer, send interested people to a focused page and route inquiries to the person who can help. This is an example approach, not a campaign results report.",
        "example_es": "Para un negocio de servicios, una campaña puede presentar una oferta, llevar a los interesados a una página específica y dirigir las consultas a quien pueda ayudar. Es un ejemplo de enfoque, no un reporte de resultados.",
        "stages": [("Focused offer", "Oferta concreta"),("Relevant ad", "Anuncio relevante"),("Website or WhatsApp", "Web o WhatsApp"),("Personal follow-up", "Seguimiento personal")],
        "start": "We start with your offer, service area and a realistic test budget. Campaign setup, creative work, landing pages and management are scoped clearly; ad spend is separate.",
        "start_es": "Empezamos con tu oferta, zona de servicio y un presupuesto de prueba realista. Definimos configuración, contenido, páginas y gestión; la inversión publicitaria se paga por separado.",
        "faq": [
            ("Is the advertising budget included?", "Ad spend is separate from service fees. We agree on the budget and campaign scope before activation.", "¿Está incluido el presupuesto publicitario?", "La inversión publicitaria es independiente del servicio. Acordamos el presupuesto y el alcance antes de activar la campaña."),
            ("Do you guarantee a number of leads?", "No. Results depend on the offer, market, budget and response process. We use actual campaign and inquiry data to decide what to improve.", "¿Garantizas una cantidad de contactos?", "No. Los resultados dependen de la oferta, el mercado, el presupuesto y la atención. Usamos datos reales para decidir qué mejorar."),
            ("Can you create the ads and landing page?", "Yes. Creative work and a landing page can be included in the agreed scope, alongside campaign setup and management.", "¿Puedes crear anuncios y la página de destino?", "Sí. Podemos incluir el contenido y una página de destino junto con la configuración y gestión de campaña.")]
    },
    "content-engine": {
        "name": "Content creation & publishing", "name_es": "Creación y publicación de contenido",
        "title": "Show up consistently. Sound like your business.", "title_es": "Publica con constancia. Mantén tu propia voz.",
        "meta": "Social posts, visuals and short-form video built around your brand, with a clear review process and a practical publishing schedule.",
        "meta_es": "Publicaciones, imágenes y videos cortos alineados con tu marca, con un proceso claro de revisión y un calendario práctico.",
        "example_title": "HEH: a recognizable editorial style.", "example_title_es": "HEH: un estilo editorial reconocible.",
        "example": "This Miami Business Watch creative is an example of the content produced for HEH. A consistent visual system helps each post feel like part of the same brand.",
        "example_es": "Esta pieza de Miami Business Watch es un ejemplo del contenido creado para HEH. Un sistema visual coherente ayuda a que cada publicación se reconozca como parte de la marca.",
        "image": "/assets/site/project-heh-content.jpg", "image_alt": "HEH Miami Business Watch social media creative", "image_alt_es": "Pieza de redes sociales de HEH Miami Business Watch", "url": "/assets/site/project-heh-content.jpg",
        "start": "We review your brand, audience and available material, then agree on formats, quantity, review rounds and publishing responsibilities for the first content cycle.",
        "start_es": "Revisamos tu marca, público y material disponible. Acordamos formatos, cantidad, revisiones y responsabilidades de publicación para el primer ciclo."
    }
}
for offer in OFFERS:
    if offer["slug"] in PRIMARY:
        offer.update(PRIMARY[offer["slug"]])

# Featured offer: one page with real video examples. It is one offer among the others,
# not the site's positioning. Presenters are always disclosed as AI; no prices on the page.
REELS_DIR = "/assets/site/reels"
OFFERS.append({
    "slug": "ai-spokesperson",
    "name": "AI spokesperson videos", "name_es": "Videos con vocero de IA",
    "title": "Your business on video every week. No cameras, no studio.",
    "title_es": "Tu negocio en video cada semana. Sin cámaras, sin estudio.",
    "meta": "Realistic AI presenters explain your services in English or Spanish. You approve every script before anything is published, and it’s much cheaper than a film crew.",
    "meta_es": "Presentadores realistas generados con IA explican tus servicios en español o en inglés. Tú apruebas cada guion antes de que se publique, y es mucho más barato que un equipo de filmación.",
    "hero_layout": "single",
    "primary_cta": "whatsapp",
    "reels_label": ("See it", "Míralo"),
    "reels_title": ("See it before you decide.", "Míralo antes de decidir."),
    "reels_lead": (
        "These are Reels I made for Sosa Tech Solutions, with the same process I’d use for your business. The AI-agent video is the same message in English and in Spanish.",
        "Son Reels que hice para Sosa Tech Solutions con el mismo proceso que usaría para tu negocio. El video sobre agentes de IA es el mismo mensaje en inglés y en español.",
    ),
    "reels": [
        {"file": "2026-10-17_sosa-parezco-real-es_v02", "title": "‘Do I look real?’ — four AI presenters (Spanish)", "title_es": "¿Parezco real? — cuatro presentadores con IA (en español)",
         "ai": ("Presenters generated with AI", "Presentadores generados con IA")},
        {"file": "2026-10-16_sosa-tech-ai-agent-en_v03", "title": "AI-agent explainer (English)", "title_es": "Explicación de agentes de IA (en inglés)"},
        {"file": "2026-10-15_sosa-tech-agente-ia-es_v03", "title": "AI-agent explainer (Spanish)", "title_es": "Explicación de agentes de IA (en español)"},
    ],
    "intro_label": ("What it’s for", "Para qué sirve"),
    "intro_title": ("One presenter, many uses.", "Un presentador, muchos usos."),
    "intro": "Use an AI presenter wherever your business needs to explain something on video, every week, without organizing a shoot.",
    "intro_es": "Usa un presentador con IA donde tu negocio necesite explicar algo en video, cada semana, sin organizar una grabación.",
    "outcomes": [
        ("Weekly Reels", "A steady flow of short vertical videos for Instagram and Facebook, so your page never goes quiet.", "Reels semanales", "Videos verticales cortos y constantes para Instagram y Facebook, para que tu página nunca se quede en silencio."),
        ("Service explainers", "Explain what you do, how it works and who it’s for, in a short video that gets to the point.", "Explicación de servicios", "Explica qué haces, cómo funciona y para quién es, en un video corto que va al grano."),
        ("Promos and offers", "Announce a promotion, a seasonal offer or an event, with a clear invitation to message you.", "Promociones y ofertas", "Anuncia una promoción, una oferta de temporada o un evento, con una invitación clara a escribirte."),
        ("English and Spanish versions", "The same video in both languages, written for each audience instead of translated word for word.", "Versiones en español e inglés", "El mismo video en los dos idiomas, escrito para cada público y no traducido palabra por palabra."),
        ("Story images", "Matching vertical images for Instagram and Facebook Stories, so each video has a companion piece.", "Imágenes para historias", "Imágenes verticales que combinan con cada video, para las historias de Instagram y Facebook."),
    ],
    "process_label": ("How it works", "Cómo funciona"),
    "process_title": ("From topic to published video.", "Del tema al video publicado."),
    "start": "You decide what your business says. I handle the script, the production and, if you want, the publishing.",
    "start_es": "Tú decides qué dice tu negocio. Yo me encargo del guion, la producción y, si quieres, la publicación.",
    "steps": [
        ("You tell me the topic", "A service, an offer or a question your customers keep asking. A WhatsApp message is enough to start.", "Me cuentas el tema", "Un servicio, una oferta o una pregunta que tus clientes repiten. Basta con un mensaje por WhatsApp."),
        ("I write the script. You approve it.", "You read every word before production and can ask for changes. Nothing moves forward without your OK.", "Escribo el guion. Tú lo apruebas.", "Lees cada palabra antes de producir y puedes pedir cambios. Nada avanza sin tu aprobación."),
        ("I produce the video", "An AI presenter, motion graphics and on-screen captions, in vertical format for Reels and Stories.", "Produzco el video", "Un presentador con IA, gráficos en movimiento y subtítulos en pantalla, en formato vertical para Reels e historias."),
        ("I publish it and confirm", "Optional: I schedule it on your Facebook and Instagram and let you know when it’s live.", "Lo publico y te confirmo", "Opcional: lo programo en tu Facebook e Instagram y te aviso cuando ya está publicado."),
    ],
    "notes_label": ("Honest notes", "Notas claras"),
    "notes_title": ("What you should know first.", "Lo que debes saber primero."),
    "notes": [
        ("The presenters are AI, and labeled as AI", "They are generated with AI. Every video says so on screen and in the post caption, and I never present them as real people.", "Los presentadores son IA y se identifican como IA", "Se generan con IA. Cada video lo indica en pantalla y en el texto de la publicación, y nunca los presento como personas reales."),
        ("You approve every script", "Nothing is produced or published without your OK. The presenter only says what you approved.", "Tú apruebas cada guion", "Nada se produce ni se publica sin tu aprobación. El presentador solo dice lo que aprobaste."),
        ("Ask for a quote on WhatsApp", "Every business needs a different mix of videos, languages and publishing, so I quote each one on WhatsApp. It’s much cheaper than a film crew.", "Pide una cotización por WhatsApp", "Cada negocio necesita una combinación distinta de videos, idiomas y publicación, así que cotizo cada caso por WhatsApp. Es mucho más barato que un equipo de filmación."),
    ],
    "related_label": ("Works well with", "Funciona bien con"),
    "related_title": ("Pair it with the rest of your marketing.", "Combínalo con el resto de tu marketing."),
    "related": [
        ("content-engine", "Explore content creation & publishing →", "Ver creación y publicación de contenido →", "Add the videos to a full content calendar of posts, carousels and Reels, approved by you before anything is scheduled.", "Suma los videos a un calendario completo de publicaciones, carruseles y Reels, aprobado por ti antes de programar."),
        ("agents", "Explore AI agents & integrations →", "Ver agentes de IA e integraciones →", "Want AI to answer your customers’ questions too? An AI agent can reply with your approved information and hand off to your team.", "¿Quieres que la IA también responda a tus clientes? Un agente de IA puede contestar con tu información aprobada y pasar la conversación a tu equipo."),
    ],
    "faq_title": ("Clear answers<br>before your first video.", "Respuestas claras<br>antes de tu primer video."),
    "cta_label": ("Your AI spokesperson", "Tu vocero con IA"),
    "cta_title": ("Tell me your first topic. I’ll write the script.", "Cuéntame tu primer tema. Yo escribo el guion."),
    "cta_button": ("Ask for a quote on WhatsApp", "Pide una cotización por WhatsApp"),
    "faq": [
        ("Will people know it’s AI?", "Yes. I label it on screen and in the caption of every post. The goal is a clear, professional video, not to fool anyone.", "¿La gente sabrá que es IA?", "Sí. Lo indico en pantalla y en el texto de cada publicación. El objetivo es un video claro y profesional, no engañar a nadie."),
        ("Can the videos be in Spanish and English?", "Yes. Spanish, English, or both versions of the same video, each written for its audience rather than translated word for word.", "¿Los videos pueden ser en español y en inglés?", "Sí. En español, en inglés o en ambas versiones del mismo video, cada una escrita para su público y no traducida palabra por palabra."),
        ("Who approves the script?", "You do, always. Nothing is produced until you approve the script, and you see the finished video before it’s published.", "¿Quién aprueba el guion?", "Tú, siempre. No se produce nada hasta que apruebes el guion, y ves el video terminado antes de que se publique."),
        ("Can you publish it for me?", "Yes. I can schedule it on your Facebook and Instagram and confirm when it’s live. If you prefer to post it yourself, you get the final video files.", "¿Puedes publicarlo por mí?", "Sí. Lo programo en tu Facebook e Instagram y te confirmo cuando está publicado. Si prefieres publicarlo tú, te entrego los archivos finales."),
        ("Do I need to record anything?", "No. No camera, no studio and no recording on your side. If you have photos of your business, products or logo, I can use them in the video.", "¿Tengo que grabar algo?", "No. No necesitas cámara, estudio ni grabarte. Si tienes fotos de tu negocio, tus productos o tu logo, puedo usarlas en el video."),
    ],
})
OFFER_BY_SLUG = {offer["slug"]: offer for offer in OFFERS}

# Search snippet per page: <title> (<= 60 chars, ends "| Sosa Tech Solutions") and
# meta description (140-155 chars). The visible hero copy stays in "meta".
SEO = {
    "websites": (
        "Bilingual Website Design in Miami",
        "Get a clear, mobile-first website built around your offer, with WhatsApp and contact forms that make it easy to reach you. In English, Spanish or both.",
    ),
    "automation": (
        "WhatsApp Automation in Miami",
        "Connect your forms, WhatsApp, alerts and reminders so every inquiry reaches the right person with a clear next step, without copying details by hand.",
    ),
    "content-engine": (
        "Social Media Content Creation in Miami",
        "Posts, carousels, Reels and AI-assisted visuals built around your brand and approved by you before anything is scheduled on Facebook and Instagram.",
    ),
    "marketing": (
        "Facebook & Instagram Ads in Miami",
        "Facebook and Instagram ads tied to a clear offer, a landing page or WhatsApp and a follow-up plan, with tracking that shows where inquiries come from.",
    ),
    "agents": (
        "AI Agents & Integrations in Miami",
        "Custom AI assistants connected to your approved information and tools to answer questions, organize inquiries and cut repetitive work, with human review.",
    ),
    "infrastructure": (
        "Server Management & Backups in Miami",
        "Keep the servers and systems behind your business running, with monitoring, alerts, encrypted backups and tested recovery handled by someone accountable.",
    ),
    "streaming": (
        "Radio & Live Streaming Setup in Miami",
        "Internet radio, website players and live audio or video streams, set up and monitored for your station or business, with practical technical support.",
    ),
    "ai-spokesperson": (
        "AI Spokesperson Videos in Miami",
        "Weekly videos where a realistic AI presenter, labeled as AI, explains your services in English or Spanish. You approve every script. No cameras needed.",
    ),
}
# Spanish snippet, same limits; assets/service.js swaps document.title and the meta
# description when the visitor switches the page to Spanish.
SEO_ES = {
    "websites": (
        "Páginas web bilingües en Miami",
        "Una página web clara y pensada para el móvil, centrada en tu oferta, con WhatsApp y formularios que facilitan el contacto. En español, inglés o ambos.",
    ),
    "automation": (
        "Automatización de WhatsApp en Miami",
        "Conecta formularios, WhatsApp, alertas y recordatorios para que cada consulta llegue a la persona indicada con un siguiente paso claro, sin copiar datos.",
    ),
    "content-engine": (
        "Contenido para redes sociales en Miami",
        "Posts, carruseles, Reels e imágenes con IA alineados con tu marca y aprobados por ti antes de programar cualquier publicación en Facebook e Instagram.",
    ),
    "marketing": (
        "Anuncios en Facebook e Instagram",
        "Anuncios en Facebook e Instagram con una oferta clara, una página de destino o WhatsApp y un plan de seguimiento, midiendo de dónde llegan las consultas.",
    ),
    "agents": (
        "Agentes de IA e integraciones en Miami",
        "Asistentes de IA a medida, conectados a tu información y herramientas aprobadas, para responder preguntas, organizar consultas y reducir trabajo manual.",
    ),
    "infrastructure": (
        "Administración de servidores en Miami",
        "Mantén funcionando los servidores y sistemas de tu negocio con monitoreo, alertas, respaldos cifrados y recuperación probada, con un responsable claro.",
    ),
    "streaming": (
        "Radio y streaming en vivo en Miami",
        "Radio por internet, reproductores web y transmisiones de audio o video en vivo, configurados y monitoreados para tu emisora o negocio, con soporte técnico.",
    ),
    "ai-spokesperson": (
        "Videos con vocero de IA en Miami",
        "Videos semanales en los que un presentador realista con IA, identificado como IA, explica tus servicios en español o inglés. Tú apruebas cada guion.",
    ),
}
for offer in OFFERS:
    if offer["slug"] in SEO:
        offer["seo_title"], offer["seo_description"] = SEO[offer["slug"]]
    if offer["slug"] in SEO_ES:
        offer["seo_title_es"], offer["seo_description_es"] = SEO_ES[offer["slug"]]

# Service URL slug -> WhatsApp topic slug used in the prefilled [web-<slug>] tag.
WHATSAPP_SLUGS = {
    "websites": "websites",
    "automation": "whatsapp-automation",
    "content-engine": "content",
    "marketing": "ads",
    "agents": "ai-agents",
    "streaming": "streaming",
    "infrastructure": "infrastructure",
    "ai-spokesperson": "ai-spokesperson",
}

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


def render_reels(offer: dict) -> str:
    """9:16 video cards: no autoplay, nothing downloaded before play except the poster."""
    cards = []
    for i, reel in enumerate(offer["reels"], 1):
        src = f'{REELS_DIR}/{reel["file"]}-web.mp4'
        poster = f'{REELS_DIR}/{reel["file"]}-poster.webp'
        ai_en, ai_es = reel.get("ai", ("Presenter generated with AI", "Presentador generado con IA"))
        caption_id = f"reel-{i}-caption"
        cards.append(
            f'<figure class="reel-card"><video controls playsinline preload="none" poster="{poster}" width="720" height="1280" aria-labelledby="{caption_id}">'
            f'<source src="{src}" type="video/mp4"></video>'
            f'<figcaption id="{caption_id}"><span class="reel-ai">{both(ai_en, ai_es)}</span><span class="reel-title">{both(reel["title"], reel["title_es"])}</span></figcaption></figure>'
        )
    label_en, label_es = offer["reels_label"]
    title_en, title_es = offer["reels_title"]
    lead_en, lead_es = offer["reels_lead"]
    return (
        f'<section class="reels" id="see-it"><div class="reels-intro"><div><div class="label">{both(label_en, label_es)}</div><h2>{both(title_en, title_es)}</h2></div>'
        f'<p class="lead">{both(lead_en, lead_es)}</p></div><div class="reel-grid">{"".join(cards)}</div></section>'
    )


def render_notes(offer: dict, whatsapp: str) -> str:
    cards = "".join(
        f'<article class="proof-card"><b>0{i}</b><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></article>'
        for i, (en_t, en_d, es_t, es_d) in enumerate(offer["notes"], 1)
    )
    link = f'<a class="example-link" {whatsapp_contact.link_attributes(whatsapp)}>{both("Ask for a quote on WhatsApp →", "Pide una cotización por WhatsApp →")}</a>'
    label_en, label_es = offer["notes_label"]
    title_en, title_es = offer["notes_title"]
    return f'<section class="proof notes"><div class="label">{both(label_en, label_es)}</div><h2>{both(title_en, title_es)}</h2><div class="proof-grid">{cards}</div>{link}</section>'


def render_related(offer: dict) -> str:
    items = []
    for slug, link_en, link_es, en, es in offer["related"]:
        target = OFFER_BY_SLUG[slug]
        items.append(
            f'<article><h3>{both(target["name"], target["name_es"])}</h3><p>{both(en, es)}</p>'
            f'<a class="example-link" href="/services/{slug}/">{both(link_en, link_es)}</a></article>'
        )
    label_en, label_es = offer["related_label"]
    title_en, title_es = offer["related_title"]
    return f'<section class="example related"><div><div class="label">{both(label_en, label_es)}</div><h2>{both(title_en, title_es)}</h2></div><div class="related-list">{"".join(items)}</div></section>'


def render(offer: dict) -> str:
    url = f"https://sosatechsolutions.com/services/{offer['slug']}/"
    faq_entities = []
    for en_q, en_a, _, _ in offer["faq"]:
        faq_entities.append({"@type": "Question", "name": en_q, "acceptedAnswer": {"@type": "Answer", "text": en_a}})
    description = offer.get("seo_description", offer["meta"])
    page_title = f'{offer.get("seo_title", offer["name"])} | Sosa Tech Solutions'
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Service", "name": offer["name"], "description": description, "url": url, "areaServed": "Miami and South Florida", "provider": {"@type": "LocalBusiness", "@id": "https://sosatechsolutions.com/#business", "name": "Sosa Tech Solutions", "url": "https://sosatechsolutions.com/"}},
            {"@type": "FAQPage", "mainEntity": faq_entities},
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://sosatechsolutions.com/"}, {"@type": "ListItem", "position": 2, "name": offer["name"], "item": url}]},
        ],
    }
    outcomes = "".join(f'<article class="outcome"><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(offer["outcomes"], 1))
    steps = "".join(f'<article class="step"><b>0{i}</b><div><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></div></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(offer.get("steps", STEPS), 1))
    proof = "".join(f'<article class="proof-card"><b>{"OPERATING PROOF" if i == 1 else "BUILD PRINCIPLE"}</b><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(offer.get("proof", []), 1))
    faq = "".join(f'<details><summary>{both(en_q, es_q)}</summary><p>{both(en_a, es_a)}</p></details>' for en_q, en_a, es_q, es_a in offer["faq"])
    more_links = []
    for item in OFFERS:
        current = 'aria-current="page"' if item["slug"] == offer["slug"] else ""
        more_links.append(f'<a href="/services/{item["slug"]}/" {current}>{both(item["name"], item["name_es"])}</a>')
    more = "".join(more_links)
    if offer.get("hero_layout") == "single":
        visual = ""
    elif offer.get("image"):
        visual = f'<figure class="service-visual"><img src="{offer["image"]}" alt="{offer["image_alt"]}" data-alt-en="{offer["image_alt"]}" data-alt-es="{offer["image_alt_es"]}" width="1902" height="815"><figcaption>{both(offer["example_title"], offer["example_title_es"])}</figcaption></figure>'
    else:
        stages = offer.get("stages", [(part.strip(), part.strip()) for part in offer["signal"].split("->")])
        visual = '<ol class="service-journey">' + ''.join(f'<li><span class="stage-number" aria-hidden="true">0{i}</span><div>{both(en, es)}</div></li>' for i, (en, es) in enumerate(stages, 1)) + '</ol>'
    whatsapp = WHATSAPP_SLUGS[offer["slug"]]
    if offer.get("notes"):
        example_section = render_notes(offer, whatsapp) + render_related(offer)
    elif offer.get("example"):
        example_link = f'<a class="example-link" href="{offer["url"]}" target="_blank" rel="noopener noreferrer">{both("Explore this work", "Ver este trabajo")}</a>' if offer.get("url") else ''
        example_section = f'<section class="example"><div><div class="label">{both("Selected work" if offer.get("image") else "Example workflow", "Trabajo seleccionado" if offer.get("image") else "Ejemplo de flujo")}</div><h2>{both(offer["example_title"], offer["example_title_es"])}</h2></div><div><p class="lead">{both(offer["example"], offer["example_es"])}</p>{example_link}</div></section>'
    else:
        example_section = f'<section class="proof"><h2>{both("Built for day-to-day operations.", "Para la operación diaria.")}</h2><div class="proof-grid">{proof}</div></section>'
    review = f'href="/?service={offer["slug"]}#contact"'
    whatsapp_link = whatsapp_contact.link_attributes(whatsapp)
    if offer.get("primary_cta") == "whatsapp":
        actions = (f'<a class="primary whatsapp-action" {whatsapp_link}>{whatsapp_contact.ICON}{both("Message Victor on WhatsApp", "Escribe a Victor por WhatsApp")}</a>'
                   f'<a class="secondary" {review}>{both("Request a free review", "Solicitar revisión gratuita")}</a>')
        cta_button = f'<a class="primary" {whatsapp_link}>{both(*offer["cta_button"])}</a>'
    else:
        actions = (f'<a class="primary" {review}>{both("Request my free review", "Solicitar revisión gratuita")}</a>'
                   f'<a class="secondary" {whatsapp_link}>{both("Message Victor on WhatsApp", "Escribe a Victor por WhatsApp")}</a>')
        cta_button = f'<a class="primary" {review}>{both("Request my free review", "Solicitar revisión gratuita")}</a>'
    hero_class = "hero hero-single" if offer.get("hero_layout") == "single" else "hero"
    reels = "\n" + render_reels(offer) if offer.get("reels") else ""
    intro_label = offer.get("intro_label", ("What we can build", "Qué podemos crear"))
    intro_title = offer.get("intro_title", ("What’s included.", "Qué incluye."))
    process_label = offer.get("process_label", ("How we work", "Cómo trabajamos"))
    process_title = offer.get("process_title", ("Start with one useful conversation.", "Empecemos con una conversación útil."))
    faq_title = offer.get("faq_title", ("Clear answers<br>before we build.", "Respuestas claras<br>antes de construir."))
    cta_label = offer.get("cta_label", ("Free lead-flow review", "Revisión gratuita del flujo"))
    cta_title = offer.get("cta_title", ("Let’s find your next practical step.", "Encontremos tu próximo paso."))
    title = html.escape(page_title, quote=True)
    meta = html.escape(description, quote=True)
    title_es = html.escape(f'{offer.get("seo_title_es", offer["name_es"])} | Sosa Tech Solutions', quote=True)
    meta_es = html.escape(offer.get("seo_description_es", offer["meta_es"]), quote=True)
    return f'''<!DOCTYPE html>
<html lang="en" data-title-es="{title_es}" data-description-es="{meta_es}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{meta}"><meta name="robots" content="index,follow">
<link rel="canonical" href="{url}"><meta name="theme-color" content="#080A0F">
<meta property="og:type" content="website"><meta property="og:url" content="{url}"><meta property="og:title" content="{title}"><meta property="og:description" content="{meta}"><meta property="og:image" content="https://sosatechsolutions.com/og-image-2026-10.png">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{meta}"><meta name="twitter:image" content="https://sosatechsolutions.com/og-image-2026-10.png">
<link rel="icon" href="/favicon.ico"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS_HREF}"><link rel="stylesheet" href="{SERVICE_CSS_HREF}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
<link rel="stylesheet" href="{NAV_CSS_HREF}"><link rel="stylesheet" href="{whatsapp_contact.CSS_HREF}">
</head><body class="has-site-nav">
<a class="skip" href="#main">{both('Skip to content', 'Saltar al contenido')}</a>
{render_navigation(offer['slug'], whatsapp)}
<main id="main">
<header class="{hero_class}"><div><div class="label">{both(offer['name'], offer['name_es'])}</div><h1>{both(offer['title'], offer['title_es'])}</h1><p class="hero-copy">{both(offer['meta'], offer['meta_es'])}</p><div class="actions">{actions}</div></div>{visual}</header>{reels}
<section class="intro"><div><div class="label">{both(*intro_label)}</div><h2>{both(*intro_title)}</h2></div><div><p class="lead">{both(offer['intro'], offer['intro_es'])}</p><div class="outcomes">{outcomes}</div></div></section>
<section class="process"><div><div class="label">{both(*process_label)}</div><h2>{both(*process_title)}</h2></div><div><p class="lead engagement">{both(offer.get("start", offer["intro"]), offer.get("start_es", offer["intro_es"]))}</p><div class="steps">{steps}</div></div></section>
{example_section}
<section class="faq"><div><div class="label">{both('FAQ', 'Preguntas frecuentes')}</div><h2>{both(*faq_title)}</h2></div><div class="faq-list">{faq}</div></section>
<section class="cta"><div><div class="label">{both(*cta_label)}</div><h2>{both(*cta_title)}</h2></div>{cta_button}</section>
<section class="more"><div class="label">{both('Explore capabilities','Explora capacidades')}</div><div class="more-grid">{more}</div></section>
</main>
<footer><span>© 2026 Sosa Tech Solutions · Miami, Florida</span><span><a href="/privacy-policy/">{both('Privacy', 'Privacidad')}</a> · <a href="/terms/">{both('Terms', 'Términos')}</a> · <a href="/blog/">Blog</a></span></footer>
{whatsapp_contact.floating_button(whatsapp)}
<script src="{SERVICE_JS_SRC}" defer></script><script src="{NAV_JS_SRC}" defer></script><script src="{whatsapp_contact.JS_SRC}" defer></script></body></html>'''


if __name__ == "__main__":
    for item in OFFERS:
        target = ROOT / "services" / item["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(item), encoding="utf-8")
        print(target.relative_to(ROOT))
