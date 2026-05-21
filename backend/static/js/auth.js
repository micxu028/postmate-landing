// Auth helpers
document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  const loginLink = document.getElementById('login-link');
  const logoutBtn = document.getElementById('logout-btn');

  if (token && logoutBtn) {
    logoutBtn.style.display = 'block';
    logoutBtn.onclick = () => {
      localStorage.removeItem('token');
      window.location.href = '/app/login';
    };
  }

  if (token && window.location.pathname.endsWith('login.html')) {
    window.location.href = '/app/dashboard.html';
  }
});

function showToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}
