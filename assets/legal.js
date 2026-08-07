(function () {
  const buttons = Array.from(document.querySelectorAll("[data-set-language]"));
  const sections = Array.from(document.querySelectorAll("[data-language]"));

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
    try {
      window.localStorage.setItem("sosatech-language", selected);
    } catch (_) {
      // Language preference remains session-only when storage is unavailable.
    }
  }

  buttons.forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.setLanguage));
  });

  const queryLanguage = new URLSearchParams(window.location.search).get("lang");
  let savedLanguage = "";
  try {
    savedLanguage = window.localStorage.getItem("sosatech-language") || "";
  } catch (_) {
    savedLanguage = "";
  }
  const browserLanguage = navigator.language.toLowerCase().startsWith("es") ? "es" : "en";
  setLanguage(queryLanguage || savedLanguage || browserLanguage);
})();
