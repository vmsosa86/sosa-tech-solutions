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

  // Keep the floating button off a video's native control bar (e.g. full-width Reels on a phone).
  const float = document.querySelector('.wa-float');
  const floatLink = float && float.querySelector('.floating-whatsapp');
  const videos = Array.from(document.querySelectorAll('video[controls]'));
  if (floatLink && videos.length) {
    const controlBar = 56;
    let queued = false;
    const check = () => {
      queued = false;
      const button = floatLink.getBoundingClientRect();
      const covered = videos.some((video) => {
        const box = video.getBoundingClientRect();
        return box.width > 0 && box.left < button.right && box.right > button.left
          && box.bottom > button.top - 8 && box.bottom - controlBar < button.bottom + 8;
      });
      float.classList.toggle('is-tucked', covered);
    };
    const queue = () => { if (!queued) { queued = true; requestAnimationFrame(check); } };
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', queue);
    check();
  }
})();
