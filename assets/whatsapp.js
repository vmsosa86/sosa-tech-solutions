/* Loaded on every public page.
   1. EN/ES language links ([data-lang-link]): each page exists in English (current URL) and
      Spanish (/es/ + path). The links are real hrefs to the counterpart page; this adds the
      current ?query (minus any legacy lang=) and #hash and remembers the choice. Nothing
      redirects automatically: English stays the default at every English URL.
   2. The floating WhatsApp button (its prefilled message is rendered in the page language). */
(() => {
  'use strict';
  const legacyKeys = ['sosa-tech-language', 'sosatech-language', 'sosaLang'];

  function updateLanguageLinks() {
    const current = new URLSearchParams(location.search);
    document.querySelectorAll('a[data-lang-link]').forEach((link) => {
      // Keep what the link already carries (e.g. utm_* added by service.js), then the current query.
      const target = new URL(link.getAttribute('href'), location.origin);
      current.forEach((value, key) => target.searchParams.set(key, value));
      target.searchParams.delete('lang');
      const search = target.searchParams.toString();
      link.href = `${target.pathname}${search ? `?${search}` : ''}${location.hash}`;
    });
  }

  document.querySelectorAll('a[data-lang-link]').forEach((link) => {
    link.addEventListener('click', () => {
      updateLanguageLinks();
      try {
        localStorage.setItem('sosa-language', link.dataset.langLink);
        legacyKeys.forEach((key) => localStorage.removeItem(key));
      } catch (_) { /* storage may be unavailable */ }
    });
  });
  window.addEventListener('hashchange', updateLanguageLinks);
  updateLanguageLinks();

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
