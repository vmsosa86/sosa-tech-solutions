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

  // Hero service cards (2026-10-15). Everything is readable without this script: it only
  // replays the chat example once in view, runs the muted AI loop and lets the phone row
  // scroll by keyboard.
  const heroCards = document.querySelector('.hero-cards');
  if (heroCards) {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const canObserve = 'IntersectionObserver' in window;

    // Chat example: hide the bubbles only when the sequence can play, then play it once
    // when the card is in view; it rests on the final state (CSS does the timing, < 3 s).
    const chat = heroCards.querySelector('.hero-visual-chat');
    if (chat && canObserve && !reduceMotion.matches) {
      chat.classList.add('is-armed');
      const chatObserver = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          chat.classList.add('is-playing');
          chatObserver.disconnect();
        }
      }, { threshold: 0.6 });
      chatObserver.observe(chat);
    }

    // AI spokesperson loop: preload="none", so nothing downloads until play(). It plays only
    // after the page has loaded, while the card is on screen, and never with reduced motion or
    // Save-Data (the visitor can still press play). The button pauses/plays it (WCAG 2.2.2).
    const video = heroCards.querySelector('.hero-ai-video');
    const toggle = heroCards.querySelector('.hero-video-toggle');
    if (video && toggle) {
      const saveData = Boolean(navigator.connection && navigator.connection.saveData);
      let wanted = !reduceMotion.matches && !saveData;
      let visible = !canObserve;
      let loaded = document.readyState === 'complete';
      video.muted = true;

      const render = () => {
        toggle.dataset.state = wanted ? 'playing' : 'paused';
        toggle.setAttribute('aria-label', wanted ? toggle.dataset.labelPause : toggle.dataset.labelPlay);
      };
      const sync = () => {
        if (wanted && visible && loaded) {
          if (video.paused) {
            const attempt = video.play();
            if (attempt && typeof attempt.catch === 'function') {
              attempt.catch(() => { wanted = false; render(); });
            }
          }
        } else if (!video.paused) {
          video.pause();
        }
        render();
      };

      toggle.hidden = false;
      toggle.addEventListener('click', () => { wanted = !wanted; sync(); });
      if (typeof reduceMotion.addEventListener === 'function') {
        reduceMotion.addEventListener('change', () => { if (reduceMotion.matches) { wanted = false; sync(); } });
      }
      if (canObserve) {
        new IntersectionObserver((entries) => {
          visible = entries[entries.length - 1].isIntersecting;
          sync();
        }, { threshold: 0.35 }).observe(video);
      }
      if (!loaded) {
        window.addEventListener('load', () => { loaded = true; sync(); }, { once: true });
      }
      render();
    }

    // Phones: the cards are a swipe row. While it scrolls sideways it is also a tab stop,
    // so arrow keys can move it (the card links scroll into view on focus as well).
    const scroller = document.querySelector('.hero-cards-scroller');
    if (scroller) {
      const updateScroller = () => {
        if (scroller.scrollWidth > scroller.clientWidth + 1) scroller.setAttribute('tabindex', '0');
        else scroller.removeAttribute('tabindex');
      };
      updateScroller();
      window.addEventListener('resize', updateScroller, { passive: true });
    }
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
    // Beyond the browser's checks: a required field needs more than spaces, and a phone
    // number needs at least 7 digits (so Victor can always reach the lead).
    function isValid(field) {
      field.setCustomValidity('');
      if (!field.checkValidity()) return false;
      const value = field.value.trim();
      if (field.required && !value) return false;
      if (field.type === 'tel' && value && (value.match(/\d/g) || []).length < 7) return false;
      return true;
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
      if (honeypot && honeypot.checked) return;

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

      // Anti-bot timing: a valid form sent within 3 s of loading (autofill makes that easy)
      // waits out the rest in the "Sending…" state instead of being dropped silently.
      const remaining = 3000 - (Date.now() - formStartedAt);
      if (remaining > 0) await new Promise((resolve) => setTimeout(resolve, remaining));

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
