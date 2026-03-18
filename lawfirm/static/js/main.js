// Sidebar mobile toggle
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');
const toggle = document.getElementById('sidebarToggle');

function openSidebar() {
    sidebar.classList.add('open');
    overlay.classList.add('active');
    toggle.setAttribute('aria-expanded', 'true');
}

function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
    toggle.setAttribute('aria-expanded', 'false');
}

toggle?.addEventListener('click', () => {
    sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
});

overlay?.addEventListener('click', closeSidebar);

// Topbar date
(function () {
    const el = document.getElementById('topbarDate');
    if (!el) return;
    const opts = { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' };
    el.textContent = new Date().toLocaleDateString('es-EC', opts).toUpperCase();
})();