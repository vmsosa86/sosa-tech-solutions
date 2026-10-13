(() => {
  'use strict';

  // The page is rendered in one language (English at /, Spanish at /es/) by
  // scripts/build_language_pages.py from content/i18n/home.json; runtime messages come
  // from data-* attributes rendered in the page language.
  const menuButton = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('.primary-nav');

  function closeMenu() {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('open');
    menuButton.setAttribute('aria-label', menuButton.dataset.labelOpen);
  }

  if (menuButton && navigation) {
    menuButton.addEventListener('click', () => {
      const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!isOpen));
      navigation.classList.toggle('open', !isOpen);
      menuButton.setAttribute('aria-label', menuButton.dataset[isOpen ? 'labelOpen' : 'labelClose']);
    });
    navigation.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeMenu();
    });
  }

  const header = document.querySelector('.site-header');
  function updateScroll() {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollable > 0 ? Math.min(100, (window.scrollY / scrollable) * 100) : 0;
    document.documentElement.style.setProperty('--scroll-progress', `${progress}%`);
    if (header) header.classList.toggle('scrolled', window.scrollY > 24);
  }
  updateScroll();
  window.addEventListener('scroll', updateScroll, { passive: true });

  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.body.classList.add('motion-ready');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));
  } else {
    document.querySelectorAll('.reveal').forEach((element) => element.classList.add('is-visible'));
  }

  const form = document.getElementById('contact-form');
  const formStartedAt = Date.now();
  if (form) {
    const query = new URLSearchParams(window.location.search);
    const interest = form.elements.namedItem('service_interest');
    const requestedService = query.get('service');
    if (interest && [...interest.options].some(option => option.value === requestedService)) {
      interest.value = requestedService;
    }

    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'].forEach((name) => {
      const fromQuery = query.get(name);
      if (fromQuery) {
        try { sessionStorage.setItem(`sosa-${name}`, fromQuery); } catch (_) { /* storage may be unavailable */ }
      }
      let value = fromQuery || '';
      if (!value) {
        try { value = sessionStorage.getItem(`sosa-${name}`) || ''; } catch (_) { /* storage may be unavailable */ }
      }
      const input = form.elements.namedItem(name);
      if (input) input.value = value;
    });
    const landingPage = form.elements.namedItem('landing_page');
    if (landingPage) landingPage.value = window.location.href;

    let submitting = false;
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (submitting) return;

      const honeypot = form.elements.namedItem('botcheck');
      if ((honeypot && honeypot.checked) || Date.now() - formStartedAt < 3000) return;

      const requiredFields = [...form.querySelectorAll('[required]')];
      requiredFields.forEach((field) => field.removeAttribute('aria-invalid'));
      const invalid = requiredFields.filter((field) => !field.checkValidity());
      if (invalid.length) {
        invalid.forEach((field) => field.setAttribute('aria-invalid', 'true'));
        invalid[0].focus();
        return;
      }

      const submitButton = document.getElementById('contact-submit');
      const submitLabel = submitButton ? submitButton.textContent : '';
      submitting = true;
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = form.dataset.msgSending;
      }

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(Object.fromEntries(new FormData(form)))
        });
        const result = await response.json();
        if (!response.ok || !result.success) throw new Error('Submission failed');

        form.hidden = true;
        const success = document.getElementById('form-success');
        if (success) success.classList.add('show');
        if (typeof window.fbq === 'function') window.fbq('track', 'Lead');
      } catch (_) {
        const error = document.createElement('p');
        error.className = 'form-error';
        error.setAttribute('role', 'alert');
        error.textContent = form.dataset.msgError;
        form.querySelector('.form-error')?.remove();
        form.appendChild(error);
      } finally {
        submitting = false;
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = submitLabel;
        }
      }
    });
  }
})();
