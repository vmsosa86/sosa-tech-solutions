"""Client work and approved testimonials: one source for /work/ and the homepage checks.

Truth rules: Victor confirmed on 2026-10-13 that he built all nine sites and that
they may be shown. Each "built" line describes only what is visible on the live
site or what Victor stated; never add metrics, results or dates. Testimonials are
the exact texts the owners approved on 2026-10-13: show them verbatim, with name
and business only (no job titles), and never as Review/AggregateRating schema.

Screenshots live in assets/site/work/: <domain>.jpg is the 600x750 phone crop of the
live mobile homepage (the src, width and height pages declare), and <domain>-<width>.jpg
are the same capture at other widths for srcset. Recaptured 2026-10-13 at 1200x1500
(viewport width chosen per site so no button or text line is cut at the bottom edge).
Cafe Travel's Cloudflare challenge blocks automated capture, so its largest variant is
the original 780x975 capture. The <domain>-desktop.jpg variants (960x600) are kept for
later use.
"""

WORK_IMAGE_DIR = "/assets/site/work"
WORK_IMAGE_SIZE = (600, 750)
WORK_IMAGE_WIDTHS = (300, 600, 900, 1200)
# Rendered widths for the sizes attribute: /work/ cards and homepage #proof thumbnails.
WORK_PAGE_SIZES = "(max-width:640px) calc(100vw - 40px), (max-width:1023px) calc(50vw - 50px), 410px"
HOME_SIZES = "(max-width:540px) 116px, (max-width:900px) calc(50vw - 40px), 410px"

# Display order on /work/: Mocasa x2, HEH, Miami Travel y Más, Cafe Travel, the radios, HAAG.
CLIENTS = [
    {
        "domain": "mocasahairtransplant.com",
        "name": "Mocasa Hair Transplant",
        "tag": ("Hair restoration · Miami", "Restauración capilar · Miami"),
        "built": (
            "I built their consultation landing page for hair and beard transplants, with a consultation form, WhatsApp and call links. I also create their social content and campaigns.",
            "Creé su landing page de consultas para trasplante de cabello y barba, con formulario de consulta y enlaces a WhatsApp y llamada. También creo su contenido para redes y sus campañas.",
        ),
        "alt": (
            "Mocasa Hair Transplant mobile homepage with the headline “Restore Your Hair” and a free consultation button",
            "Página de inicio móvil de Mocasa Hair Transplant con el titular “Restore Your Hair” y un botón de consulta gratuita",
        ),
    },
    {
        "domain": "mocasawc.com",
        "name": "Mocasa Wellness Center",
        "tag": ("Med spa · Miami", "Med spa · Miami"),
        "built": (
            "I built the center’s website, with its services, online booking and payment-plan information.",
            "Creé la página web del centro, con sus servicios, reservas en línea e información de planes de pago.",
        ),
        "alt": (
            "Mocasa Wellness Center mobile homepage with the MWC logo, the line “Mocasa, Tu Casa!” and buttons for services and booking",
            "Página de inicio móvil de Mocasa Wellness Center con el logo MWC, la frase “Mocasa, Tu Casa!” y botones de servicios y reservas",
        ),
    },
    {
        "domain": "hehconsultingfirm.com",
        "name": "H.E.H. Consulting",
        "tag": ("Government relations · Miami", "Relaciones gubernamentales · Miami"),
        "built": (
            "I built their website, including a Miami policy and business news section. I also run their Facebook and Instagram content and scheduled publishing, including Reels.",
            "Creé su página web, con una sección de noticias de política y negocios de Miami. También manejo su contenido y su publicación programada en Facebook e Instagram, incluidos los Reels.",
        ),
        "alt": (
            "H.E.H. Consulting mobile homepage with the gold H.E.H. logo on navy blue",
            "Página de inicio móvil de H.E.H. Consulting con el logo dorado de H.E.H. sobre azul marino",
        ),
    },
    {
        "domain": "miamitravelymas.com",
        "name": "Miami Travel y Más",
        "tag": ("Travel agency · Hialeah", "Agencia de viajes · Hialeah"),
        "built": (
            "I built their Spanish-language website, with WhatsApp contact and travel features. I also make their weekly travel flyers and posts.",
            "Creé su página web en español, con contacto por WhatsApp y viajes destacados. También hago sus flyers y publicaciones de viajes cada semana.",
        ),
        "alt": (
            "Miami Travel y Más mobile homepage with the agency’s sun logo on a turquoise background",
            "Página de inicio móvil de Miami Travel y Más con el logo del sol de la agencia sobre fondo turquesa",
        ),
    },
    {
        "domain": "cafetravel.com",
        "name": "Cafe Travel",
        "widths": (300, 600, 780),
        "tag": ("Group tours · Miami", "Viajes en grupo · Miami"),
        "built": (
            "I built their website and produce their tour campaigns: flyers, videos and scheduled WhatsApp Status updates.",
            "Creé su página web y produzco las campañas de sus tours: flyers, videos y Estados de WhatsApp programados.",
        ),
        "alt": (
            "Cafe Travel mobile homepage with the headline “Descubre el mundo con Cafe Travel” and a group travel button",
            "Página de inicio móvil de Cafe Travel con el titular “Descubre el mundo con Cafe Travel” y un botón de viajes grupales",
        ),
    },
    {
        "domain": "radiotobemiami.com",
        "name": "Radio To Be",
        "tag": ("Online radio · Miami", "Radio en línea · Miami"),
        "built": (
            "I built their website with a live player connected to the station’s stream, news headlines and app links, and I handle the streaming setup and support.",
            "Creé su página web con un reproductor en vivo conectado a la señal de la emisora, titulares de noticias y enlaces a las apps, y me encargo de la configuración y el soporte del streaming.",
        ),
        "alt": (
            "Radio To Be mobile homepage with the station logo, a news headline ticker and the station description",
            "Página de inicio móvil de Radio To Be con el logo de la emisora, titulares de noticias y la descripción de la emisora",
        ),
    },
    {
        "domain": "radio305.com",
        "name": "Radio 305",
        "tag": ("Online radio", "Radio en línea"),
        "built": (
            "I built the station’s website with news and a live player that shows the song now playing. I also made the station’s audio imaging and support its stream.",
            "Creé la página web de la emisora con reproductor en vivo, la canción que suena y noticias. También hice su identidad sonora y doy soporte a la señal.",
        ),
        "alt": (
            "Radio 305 mobile homepage with the station logo, breaking news and the live player showing the song now playing",
            "Página de inicio móvil de Radio 305 con el logo de la emisora, noticias de última hora y el reproductor en vivo con la canción que suena",
        ),
    },
    {
        "domain": "antenaflorida.com",
        "name": "Antena Florida",
        "tag": ("Online radio & news", "Radio en línea y noticias"),
        "built": (
            "I built their website with a live player and news headlines, plus the workflow that publishes their news.",
            "Creé su página web con reproductor en vivo y titulares de noticias, además del flujo que publica sus noticias.",
        ),
        "alt": (
            "Antena Florida mobile homepage with buttons to listen live and see the headlines",
            "Página de inicio móvil de Antena Florida con botones para escuchar en vivo y ver los titulares",
        ),
    },
    {
        "domain": "haagkids.org",
        "name": "Hispanic American Artist Group",
        "tag": ("Nonprofit · Miami", "Organización sin fines de lucro · Miami"),
        "built": (
            "I built the bilingual English and Spanish website for this Miami foundation that brings art and music to children with autism.",
            "Creé la página web bilingüe, en inglés y español, de esta fundación de Miami que lleva arte y música a niños con autismo.",
        ),
        "alt": (
            "Hispanic American Artist Group mobile homepage with its logo, a language switch and the headline “Art, music and hope for children with autism”",
            "Página de inicio móvil de Hispanic American Artist Group con su logo, selector de idioma y el titular “Art, music and hope for children with autism”",
        ),
    },
]

# Exact approved texts (EN, ES). Name + business only.
TESTIMONIALS = [
    {
        "name": "Humberto Hernandez",
        "business": "H.E.H. Consulting",
        "quote": (
            "Victor built our website and runs our social media end to end — from the content to the publishing. I approve, and it goes out on time. It feels like having a tech and marketing team in-house.",
            "Victor creó nuestra página web y maneja nuestras redes de principio a fin — desde el contenido hasta la publicación. Yo apruebo y sale a tiempo. Es como tener un equipo de tecnología y marketing en casa.",
        ),
    },
    {
        "name": "Lisbeth Sanchez",
        "business": "Mocasa",
        "quote": (
            "With Sosa Tech Solutions our website, content and WhatsApp campaigns work together. Victor understands the business and always makes sure everything goes out right.",
            "Con Sosa Tech Solutions tenemos la web, el contenido y las campañas por WhatsApp funcionando juntos. Victor entiende el negocio y siempre está pendiente de que todo salga bien.",
        ),
    },
    {
        "name": "Betsi",
        "business": "Miami Travel y Más",
        "quote": (
            "Victor built our website and helps us with travel flyers and posts every week. Customers message us on WhatsApp straight from the site.",
            "Victor nos hizo la página y nos ayuda con los flyers y las publicaciones de viajes cada semana. Los clientes nos escriben directo por WhatsApp desde la web.",
        ),
    },
    {
        "name": "Leonel",
        "business": "Cafe Travel",
        "quote": (
            "Our tour campaigns go out with flyers, videos and scheduled WhatsApp Status updates. It saves us a lot of time, and our customers see them.",
            "Las campañas de nuestros tours salen con flyers, videos y Estados de WhatsApp programados. Nos ahorra mucho tiempo y nuestros clientes las ven.",
        ),
    },
    {
        "name": "Merida Perez",
        "business": "Radio To Be",
        "quote": (
            "Victor connected our station to the website with a live player and keeps the stream running. He always responds when we need him.",
            "Victor conectó nuestra emisora a la web con un reproductor en vivo y se encarga de que la transmisión funcione. Siempre responde cuando lo necesitamos.",
        ),
    },
    {
        "name": "Rodrigo Duran",
        "business": "Radio 305",
        "quote": (
            "Victor built the Radio 305 website and the station's audio imaging, and he keeps our stream on the air.",
            "Victor nos hizo la página de Radio 305, la identidad sonora de la emisora y se encarga de que la señal esté siempre al aire.",
        ),
    },
]

# The homepage (#proof) features these sites and quotes; validate_site.py checks
# that index.html and assets/home.js carry them exactly.
HOMEPAGE_SITES = [
    "mocasahairtransplant.com",
    "hehconsultingfirm.com",
    "miamitravelymas.com",
    "cafetravel.com",
    "radiotobemiami.com",
    "radio305.com",
]
HOMEPAGE_QUOTES = ["Humberto Hernandez", "Lisbeth Sanchez", "Betsi"]


def image_url(domain: str, width: int) -> str:
    """The 600 px file keeps the plain name; other widths carry a -<width> suffix."""
    suffix = "" if width == WORK_IMAGE_SIZE[0] else f"-{width}"
    return f"{WORK_IMAGE_DIR}/{domain}{suffix}.jpg"


def srcset(domain: str) -> str:
    client = next(item for item in CLIENTS if item["domain"] == domain)
    widths = client.get("widths", WORK_IMAGE_WIDTHS)
    return ", ".join(f"{image_url(domain, width)} {width}w" for width in widths)
