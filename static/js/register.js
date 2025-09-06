document.addEventListener('DOMContentLoaded', () => {
  const form         = document.getElementById('registerForm');
  const pwd          = document.getElementById('user_password');
  const bars         = document.querySelectorAll('.strength-bar');
  const label        = document.querySelector('.strength-label');
  const hints        = document.querySelectorAll('.hint');
  const submitBtn    = document.getElementById('submitBtn');
  const consentInput = document.getElementById('consent_data');
  const toggleBtn    = document.querySelector('.toggle-password');

  if (!form) return;

  // Afficher/Masquer mot de passe
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const type = pwd.getAttribute('type') === 'password' ? 'text' : 'password';
      pwd.setAttribute('type', type);
      const icon = toggleBtn.querySelector('i');
      if (icon) icon.classList.toggle('fa-eye-slash');
    });
  }

  let ctrl;
  async function checkServerOrClient() {
    const pass = pwd.value;

    // Si une URL serveur est fournie (facultatif), essaye la route Flask /register/check_password
    if (window.CHECK_PASSWORD_URL) {
      const fd = new FormData();
      fd.append('password', pass);

      const csrf = form.querySelector('input[name="csrf_token"]');
      const headers = csrf ? { 'X-CSRFToken': csrf.value } : {};

      try {
        if (ctrl) ctrl.abort();
        ctrl = new AbortController();

        const res = await fetch(window.CHECK_PASSWORD_URL, {
          method: 'POST',
          body: fd,
          headers,
          signal: ctrl.signal
        });

        if (res.ok) {
          const data = await res.json();
          updateStrengthUI(Number(data.score ?? 0));
          updateHints(pass);
          updateSubmit(Boolean(data.valid));
          return;
        }
      } catch (_) {
        // on tombera sur le fallback client
      }
    }

    // Fallback client-only
    const ok = clientValid(pass);
    const score = clientScore(pass);
    updateStrengthUI(score);
    updateHints(pass);
    updateSubmit(ok);
  }

  function clientValid(p) {
    return p.length >= 12 && /[A-Z]/.test(p) && /[a-z]/.test(p) && /\d/.test(p) && /[^A-Za-z0-9]/.test(p);
  }
  function clientScore(p) {
    let s = 0;
    if (p.length >= 12) s++;
    if (/[A-Z]/.test(p)) s++;
    if (/\d/.test(p)) s++;
    if (/[^A-Za-z0-9]/.test(p)) s++;
    return Math.min(s, 4);
  }

  function updateStrengthUI(score) {
    bars.forEach((bar, idx) => {
      bar.style.background = idx < score ? getStrengthColor(score) : '#e2e8f0';
    });
    const labels = ['Très faible','Faible','Moyen','Fort','Fort'];
    label.textContent = labels[Math.min(4, score || 0)];
    label.style.color = getStrengthColor(score);
  }

  function updateHints(p) {
    const reqs = {
      length: p.length >= 12,
      uppercase: /[A-Z]/.test(p),
      lowercase: /[a-z]/.test(p),
      digit: /\d/.test(p),
      special: /[^A-Za-z0-9]/.test(p),
    };
    hints.forEach(h => {
      const key = h.dataset.requirement;
      h.classList.toggle('valid', !!reqs[key]);
    });
  }

  function updateSubmit(passwordOK) {
    const formOK = form.checkValidity();
    const consentOK = consentInput ? consentInput.checked : false;
    submitBtn.disabled = !(formOK && consentOK && passwordOK);
  }

  function getStrengthColor(score) {
    const colors = ['#e53e3e', '#dd6b20', '#d69e2e', '#38a169'];
    return colors[(score || 1) - 1] || '#e2e8f0';
  }

  // Écoutes
  if (pwd) {
    ['input','change'].forEach(ev => pwd.addEventListener(ev, checkServerOrClient));
  }
  if (consentInput) {
    ['change','input'].forEach(ev => consentInput.addEventListener(ev, () => updateSubmit(clientValid(pwd.value))));
  }
  form.addEventListener('input', () => updateSubmit(clientValid(pwd.value)));

  // Init
  updateStrengthUI(0);
  updateHints('');
  updateSubmit(false);
});
