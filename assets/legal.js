(function () {
  const buttons = Array.from(document.querySelectorAll("[data-set-language]"));
  const sections = Array.from(document.querySelectorAll("[data-language]"));
  // Same key as the rest of the site; "sosatech-language" is the legal pages' older key.
  const STORAGE_KEY = "sosa-language";
  const LEGACY_KEY = "sosatech-language";

  function setLanguage(language) {
    const selected = language === "es" ? "es" : "en";
    document.documentElement.lang = selected;
    sections.forEach((section) => {
      section.hidden = section.dataset.language !== selected;
    });
    buttons.forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        button.dataset.setLanguage === selected ? "true" : "false"
      );
    });
    // Internal page links carry the language, like the homepage, service and blog pages.
    document.querySelectorAll('a[href^="/"]').forEach((link) => {
      const url = new URL(link.href, window.location.origin);
      if (url.origin !== window.location.origin || !url.pathname.endsWith("/")) return;
      url.searchParams.set("lang", selected);
      link.href = `${url.pathname}${url.search}${url.hash}`;
    });
    try {
      window.localStorage.setItem(STORAGE_KEY, selected);
    } catch (_) {
      // Language preference remains session-only when storage is unavailable.
    }
    if (window.sosaWhatsApp) window.sosaWhatsApp.update(selected);
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.setLanguage));
  });

  const queryLanguage = new URLSearchParams(window.location.search).get("lang");
  let savedLanguage = "";
  try {
    savedLanguage =
      window.localStorage.getItem(STORAGE_KEY) || window.localStorage.getItem(LEGACY_KEY) || "";
  } catch (_) {
    savedLanguage = "";
  }
  // English is the site default; the browser language is not used.
  setLanguage(queryLanguage || savedLanguage || "en");
})();
