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

    // Per-field validation: the error text is rendered in the page language next to each field
    // (p.field-error, hidden until needed) and also feeds the browser's own validation bubble.
    const fields = [...form.querySelectorAll('input:not([type="hidden"]):not(.honeypot), select, textarea')];
    function errorFor(field) {
      return document.getElementById(`${field.id}-error`);
    }
    function markField(field, invalid) {
      const error = errorFor(field);
      const describedBy = (field.getAttribute('aria-describedby') || '').split(' ').filter((id) => id && (!error || id !== error.id));
      if (invalid) {
        field.setAttribute('aria-invalid', 'true');
        if (error) {
          error.hidden = false;
          describedBy.push(error.id);
          field.setCustomValidity(error.textContent.trim());
        }
      } else {
        field.removeAttribute('aria-invalid');
        field.setCustomValidity('');
        if (error) error.hidden = true;
      }
      if (describedBy.length) field.setAttribute('aria-describedby', describedBy.join(' '));
      else field.removeAttribute('aria-describedby');
    }
    function isValid(field) {
      field.setCustomValidity('');
      return field.checkValidity();
    }
    fields.forEach((field) => {
      const recheck = () => {
        if (field.getAttribute('aria-invalid') === 'true' && isValid(field)) markField(field, false);
      };
      field.addEventListener('input', recheck);
      field.addEventListener('change', recheck);
    });

    let submitting = false;
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (submitting) return;

      const honeypot = form.elements.namedItem('botcheck');
      if ((honeypot && honeypot.checked) || Date.now() - formStartedAt < 3000) return;

      const invalid = fields.filter((field) => {
        const bad = !isValid(field);
        markField(field, bad);
        return bad;
      });
      if (invalid.length) {
        invalid[0].focus();
        invalid[0].reportValidity();
        return;
      }

      const submitButton = document.getElementById('contact-submit');
      const submitLabel = submitButton ? submitButton.textContent : '';
      submitting = true;
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = form.dataset.msgSending;
      }

      // The email goes to Victor with every field, including "phone"; an empty optional
      // email is left out so it is never used as an empty reply-to address.
      const payload = Object.fromEntries(new FormData(form));
      if (!String(payload.email || '').trim()) delete payload.email;

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!response.ok || !result.success) throw new Error('Submission failed');

        form.hidden = true;
        const success = document.getElementById('form-success');
        if (success) {
          success.classList.add('show');
          const title = document.getElementById('success-title');
          if (title) title.focus();
        }
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
