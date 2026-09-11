(() => {
  const params = new URLSearchParams(location.search);
  const campaignKeys = ['utm_source','utm_medium','utm_campaign','utm_content'];

  campaignKeys.forEach(key => {
    const value = params.get(key);
    if (value) sessionStorage.setItem(`sosa_${key}`, value.slice(0, 200));
  });

  document.querySelectorAll('a[href^="/"]').forEach(link => {
    const url = new URL(link.href, location.origin);
    campaignKeys.forEach(key => {
      const value = sessionStorage.getItem(`sosa_${key}`);
      if (value) url.searchParams.set(key, value);
    });
    link.href = `${url.pathname}${url.search}${url.hash}`;
  });

  function setLanguage(language) {
    const lang = language === 'es' ? 'es' : 'en';
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-alt-en]').forEach(image => { image.alt = image.dataset[lang === 'es' ? 'altEs' : 'altEn']; });
    document.querySelectorAll('a[href^="/"]').forEach(link => {
      const url = new URL(link.href, location.origin);
      url.searchParams.set('lang', lang);
      link.href = `${url.pathname}${url.search}${url.hash}`;
    });
    document.querySelectorAll('[data-lang]').forEach(element => {
      element.hidden = element.dataset.lang !== lang;
    });
    document.querySelectorAll('[data-set-lang]').forEach(button => {
      button.setAttribute('aria-pressed', button.dataset.setLang === lang ? 'true' : 'false');
    });
    try { localStorage.setItem('sosa-language', lang); } catch {}
  }

  document.querySelectorAll('[data-set-lang]').forEach(button => {
    button.addEventListener('click', () => setLanguage(button.dataset.setLang));
  });

  document.addEventListener('sosa:language', event => setLanguage(event.detail));

  let saved = null;
  try { saved = localStorage.getItem('sosa-language') || localStorage.getItem('sosa-tech-language'); } catch {}
  setLanguage(params.get('lang') || saved || 'en');
})();
