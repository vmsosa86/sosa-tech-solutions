/* Service and work pages (one language per page: English, or Spanish under /es/). */
(() => {
  const params = new URLSearchParams(location.search);
  const campaignKeys = ['utm_source','utm_medium','utm_campaign','utm_content'];

  campaignKeys.forEach(key => {
    const value = params.get(key);
    if (value) {
      try { sessionStorage.setItem(`sosa_${key}`, value.slice(0, 200)); } catch {}
    }
  });

  // Campaign parameters follow the visitor to the next page (and to the contact form).
  document.querySelectorAll('a[href^="/"]').forEach(link => {
    const url = new URL(link.href, location.origin);
    campaignKeys.forEach(key => {
      let value = null;
      try { value = sessionStorage.getItem(`sosa_${key}`); } catch {}
      if (value) url.searchParams.set(key, value);
    });
    link.href = `${url.pathname}${url.search}${url.hash}`;
  });

  // Only one example video plays at a time.
  document.addEventListener('play', event => {
    if (event.target instanceof HTMLVideoElement) document.querySelectorAll('video').forEach(video => { if (video !== event.target) video.pause(); });
  }, true);
})();
