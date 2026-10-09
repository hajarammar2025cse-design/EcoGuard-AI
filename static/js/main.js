/**
 * AI-Powered Environmental Monitoring Network
 * Shared Client-side Enhancements
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Password Visibility Toggle
  initPasswordToggles();

  // 2. Mobile Sidebar Navigation
  initMobileSidebar();

  // 3. Auto-dismiss alerts or provide accessible close
  initAlertDismissals();
});

function initPasswordToggles() {
  document.querySelectorAll('.password-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      if (input && input.tagName === 'INPUT') {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
        btn.textContent = isPassword ? '👁️‍🗨️' : '👁️';
      }
    });
  });
}

function initMobileSidebar() {
  const sidebar = document.getElementById('appSidebar');
  const toggleBtn = document.getElementById('sidebarToggle');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      const isOpen = sidebar.classList.contains('open');
      toggleBtn.setAttribute('aria-expanded', isOpen);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
}

function initAlertDismissals() {
  document.querySelectorAll('.alert-toast').forEach(toast => {
    // Accessible close
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 200);
      });
    }
  });
}

// Global helper for formatting time hh:mm
function getFormattedCurrentTime() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}
