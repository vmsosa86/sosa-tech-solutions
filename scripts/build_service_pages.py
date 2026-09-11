#!/usr/bin/env python3
"""Generate bilingual, SEO-focused service pages from one controlled template."""

from __future__ import annotations

import json
import html
from site_navigation import render_navigation
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
    outcomes = "".join(f'<article class="outcome"><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(offer["outcomes"], 1))
    steps = "".join(f'<article class="step"><b>0{i}</b><div><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></div></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(STEPS, 1))
    proof = "".join(f'<article class="proof-card"><b>{"OPERATING PROOF" if i == 1 else "BUILD PRINCIPLE"}</b><h3>{both(en_t, es_t)}</h3><p>{both(en_d, es_d)}</p></article>' for i, (en_t, en_d, es_t, es_d) in enumerate(offer["proof"], 1))
    faq = "".join(f'<details><summary>{both(en_q, es_q)}</summary><p>{both(en_a, es_a)}</p></details>' for en_q, en_a, es_q, es_a in offer["faq"])
    more_links = []
    for item in OFFERS:
        current = 'aria-current="page"' if item["slug"] == offer["slug"] else ""
        more_links.append(f'<a href="/services/{item["slug"]}/" {current}>{both(item["name"], item["name_es"])}</a>')
    more = "".join(more_links)
    if offer.get("image"):
        visual = f'<figure class="service-visual"><img src="{offer["image"]}" alt="{offer["image_alt"]}" data-alt-en="{offer["image_alt"]}" data-alt-es="{offer["image_alt_es"]}" width="1902" height="815"><figcaption>{both(offer["example_title"], offer["example_title_es"])}</figcaption></figure>'
    else:
        stages = offer.get("stages", [(part.strip(), part.strip()) for part in offer["signal"].split("->")])
        visual = '<ol class="service-journey">' + ''.join(f'<li><span class="stage-number" aria-hidden="true">0{i}</span><div>{both(en, es)}</div></li>' for i, (en, es) in enumerate(stages, 1)) + '</ol>'
    if offer.get("example"):
        example_link = f'<a class="example-link" href="{offer["url"]}" target="_blank" rel="noopener noreferrer">{both("Explore this work", "Ver este trabajo")}</a>' if offer.get("url") else ''
        example_section = f'<section class="example"><div><div class="label">{both("Selected work" if offer.get("image") else "Example workflow", "Trabajo seleccionado" if offer.get("image") else "Ejemplo de flujo")}</div><h2>{both(offer["example_title"], offer["example_title_es"])}</h2></div><div><p class="lead">{both(offer["example"], offer["example_es"])}</p>{example_link}</div></section>'
    else:
        example_section = f'<section class="proof"><h2>{both("Built for day-to-day operations.", "Para la operación diaria.")}</h2><div class="proof-grid">{proof}</div></section>'
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
<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/service.css?v=20260911">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
<link rel="stylesheet" href="/assets/site-nav.css?v=1">
</head><body class="has-site-nav">
<a class="skip" href="#main">Skip to content</a>
{render_navigation(offer['slug'])}
<main id="main">
<header class="hero"><div><div class="label">{both(offer['name'], offer['name_es'])}</div><h1>{both(offer['title'], offer['title_es'])}</h1><p class="hero-copy">{both(offer['meta'], offer['meta_es'])}</p><div class="actions"><a class="primary" href="/?service={offer['slug']}#contact">{both('Request my free review','Solicitar revisión gratuita')}</a><a class="secondary" href="https://wa.me/13057415702" target="_blank" rel="noopener noreferrer">{both('Message Victor on WhatsApp','Escribe a Victor por WhatsApp')}</a></div></div>{visual}</header>
<section class="intro"><div><div class="label">{both('What we can build','Qué podemos crear')}</div><h2>{both('What’s included.','Qué incluye.')}</h2></div><div><p class="lead">{both(offer['intro'], offer['intro_es'])}</p><div class="outcomes">{outcomes}</div></div></section>
<section class="process"><div><div class="label">{both('How we work','Cómo trabajamos')}</div><h2>{both('Start with one useful conversation.','Empecemos con una conversación útil.')}</h2></div><div><p class="lead engagement">{both(offer.get("start", offer["intro"]), offer.get("start_es", offer["intro_es"]))}</p><div class="steps">{steps}</div></div></section>
{example_section}
<section class="faq"><div><div class="label">FAQ</div><h2>{both('Clear answers<br>before we build.','Respuestas claras<br>antes de construir.')}</h2></div><div class="faq-list">{faq}</div></section>
<section class="cta"><div><div class="label">{both('Free lead-flow review','Revisión gratuita del flujo')}</div><h2>{both('Let’s find your next practical step.','Encontremos tu próximo paso.')}</h2></div><a class="primary" href="/?service={offer['slug']}#contact">{both('Request my free review','Solicitar revisión gratuita')}</a></section>
<section class="more"><div class="label">{both('Explore capabilities','Explora capacidades')}</div><div class="more-grid">{more}</div></section>
</main>
<footer><span>© 2026 Sosa Tech Solutions · Miami, Florida</span><span><a href="/privacy-policy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/blog/">Blog</a></span></footer>
<script src="/assets/service.js?v=20260911c" defer></script><script src="/assets/site-nav.js?v=1" defer></script></body></html>'''


if __name__ == "__main__":
    for item in OFFERS:
        target = ROOT / "services" / item["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(item), encoding="utf-8")
        print(target.relative_to(ROOT))
