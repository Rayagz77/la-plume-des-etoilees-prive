// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
  const showMenu = (toggleId, navId) => {
    const toggle = document.getElementById(toggleId);
    const nav = document.getElementById(navId);
    if (!toggle || !nav) return; // garde anti-erreur
    toggle.addEventListener('click', () => {
      nav.classList.toggle('show-menu');
      toggle.classList.toggle('show-icon');
    });
  };

  showMenu('nav-toggle', 'nav-menu');
});
