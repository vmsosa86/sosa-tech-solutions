/* Shared inner-page navigation: the mobile menu. Labels are rendered in the page language. */
(() => {
  const nav = document.querySelector('.site-nav');
  if (!nav) return;
  const toggle = nav.querySelector('.site-nav-toggle');
  const links = nav.querySelector('.site-nav-links');
  function closeMenu() {
    links.classList.remove('open');
    toggle.setAttribute('aria-expanded','false');
    toggle.setAttribute('aria-label',toggle.dataset.labelOpen);
  }
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    links.classList.toggle('open',open);
    toggle.setAttribute('aria-expanded',String(open));
    toggle.setAttribute('aria-label',toggle.dataset[open?'labelClose':'labelOpen']);
  });
  nav.querySelectorAll('a').forEach(link=>link.addEventListener('click',closeMenu));
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape' && toggle.getAttribute('aria-expanded')==='true'){closeMenu();toggle.focus();}
  });
  document.addEventListener('click',event=>{if(!nav.contains(event.target)) closeMenu();});
})();
