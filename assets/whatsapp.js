/* Page-aware WhatsApp links. The prefilled message follows the page language.
   Keep the templates and encoding identical to scripts/whatsapp_contact.py. */
(() => {
  'use strict';
  const number = '13057415702';
  const templates = {
    en: (topic, slug) => `Hi Sosa Tech Solutions, I'd like to talk about ${topic}. [web-${slug}]`,
    es: (topic, slug) => `Hola Sosa Tech Solutions, quiero hablar sobre ${topic}. [web-${slug}]`
  };
  const encode = (text) => encodeURIComponent(text).replace(/[!'()*]/g, (character) => `%${character.charCodeAt(0).toString(16).toUpperCase()}`);
  const pageLanguage = () => ((document.documentElement.lang || '').toLowerCase().startsWith('es') ? 'es' : 'en');

  function update(requested) {
    const language = requested === 'es' || requested === 'en' ? requested : pageLanguage();
    const suffix = language === 'es' ? 'Es' : 'En';
    document.querySelectorAll('a[data-wa-slug]').forEach((link) => {
      const topic = link.dataset[`waTopic${suffix}`];
      if (topic) link.href = `https://wa.me/${number}?text=${encode(templates[language](topic, link.dataset.waSlug))}`;
    });
    document.querySelectorAll('[data-wa-label-en]').forEach((element) => {
      element.setAttribute('aria-label', element.dataset[`waLabel${suffix}`] || element.dataset.waLabelEn);
    });
  }

  window.sosaWhatsApp = { update };
  new MutationObserver(() => update()).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  update();
})();
