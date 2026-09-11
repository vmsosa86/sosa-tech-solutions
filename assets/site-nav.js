(() => {
  const nav = document.querySelector('.site-nav');
  if (!nav) return;
  const toggle = nav.querySelector('.site-nav-toggle');
  const links = nav.querySelector('.site-nav-links');
  const labels = {
    en: {specialists:'AI & streaming', solutions:'Solutions', proof:'Selected work', about:'About', blog:'Blog', contact:'Request a free review', open:'Open navigation menu', close:'Close navigation menu'},
    es: {specialists:'IA y streaming', solutions:'Soluciones', proof:'Proyectos', about:'Nosotros', blog:'Blog', contact:'Solicitar revisión gratuita', open:'Abrir menú de navegación', close:'Cerrar menú de navegación'}
  };
  const language = () => document.documentElement.lang === 'es' ? 'es' : 'en';
  function closeMenu() {
    links.classList.remove('open');
    toggle.setAttribute('aria-expanded','false');
    toggle.setAttribute('aria-label',labels[language()].open);
  }
  function sync() {
    const lang = language();
    nav.querySelectorAll('[data-nav-text]').forEach(el => {el.textContent=labels[lang][el.dataset.navText];});
    nav.querySelectorAll('[data-nav-lang]').forEach(button => {button.setAttribute('aria-pressed',String(button.dataset.navLang===lang));});
    nav.querySelectorAll('a').forEach(link => {
      const url = new URL(link.href,location.origin);
      url.searchParams.set('lang',lang);
      link.href = `${url.pathname}${url.search}${url.hash}`;
      if (url.pathname === '/blog/' && location.pathname.startsWith('/blog/')) link.setAttribute('aria-current','page');
    });
    closeMenu();
  }
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    links.classList.toggle('open',open);
    toggle.setAttribute('aria-expanded',String(open));
    toggle.setAttribute('aria-label',labels[language()][open?'close':'open']);
  });
  nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',closeMenu));
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape' && toggle.getAttribute('aria-expanded')==='true'){closeMenu();toggle.focus();}
  });
  document.addEventListener('click',event=>{if(!nav.contains(event.target)) closeMenu();});
  nav.querySelectorAll('[data-nav-lang]').forEach(button=>button.addEventListener('click',()=>{
    const lang=button.dataset.navLang;
    if(typeof window.setLang==='function') window.setLang(lang);
    else document.dispatchEvent(new CustomEvent('sosa:language',{detail:lang}));
    sync();
  }));
  new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  sync();
})();
