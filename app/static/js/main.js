/**
 * Student Result Analysis System - Core JavaScript Utilities
 */

document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initSidebar();
    initAlertDismissal();
    initKeyboardShortcuts();
});

/* --------------------------------------------------------------------------
   1. Theme Management (Dark / Light)
   -------------------------------------------------------------------------- */
function initThemeToggle() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    if (!themeToggleBtn) return;

    const savedTheme = localStorage.getItem('sras-theme') || 'dark';
    applyTheme(savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('sras-theme', newTheme);
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const sunIcon = document.getElementById('themeIconSun');
    const moonIcon = document.getElementById('themeIconMoon');

    if (sunIcon && moonIcon) {
        if (theme === 'light') {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        } else {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        }
    }
}

/* --------------------------------------------------------------------------
   2. Responsive Sidebar Management
   -------------------------------------------------------------------------- */
function initSidebar() {
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.getElementById('appSidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (!sidebarToggleBtn) return;

    // Restore desktop collapsed state
    const isCollapsed = localStorage.getItem('sras-sidebar-collapsed') === 'true';
    if (isCollapsed && window.innerWidth > 1024) {
        document.body.classList.add('sidebar-collapsed');
    }

    sidebarToggleBtn.addEventListener('click', () => {
        if (window.innerWidth <= 1024) {
            document.body.classList.toggle('sidebar-open');
        } else {
            document.body.classList.toggle('sidebar-collapsed');
            const nowCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sras-sidebar-collapsed', nowCollapsed);
        }
    });

    if (overlay) {
        overlay.addEventListener('click', () => {
            document.body.classList.remove('sidebar-open');
        });
    }

    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 1024) {
            document.body.classList.remove('sidebar-open');
        }
    });
}

/* --------------------------------------------------------------------------
   3. Flash Alert Dismissal
   -------------------------------------------------------------------------- */
function initAlertDismissal() {
    const alertCloseButtons = document.querySelectorAll('.alert-close-btn');

    alertCloseButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alert = e.target.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-8px)';
                alert.style.transition = 'all 0.25s ease';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // Auto dismiss after 6 seconds
    const autoAlerts = document.querySelectorAll('.alert[data-auto-dismiss="true"]');
    autoAlerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-8px)';
                alert.style.transition = 'all 0.25s ease';
                setTimeout(() => alert.remove(), 250);
            }
        }, 6000);
    });
}

/* --------------------------------------------------------------------------
   4. Global Keyboard Shortcuts
   -------------------------------------------------------------------------- */
function initKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
        // Press '/' to focus search input
        if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input');
            if (searchInput) searchInput.focus();
        }

        // Press 'Escape' to close mobile sidebar or blur active search
        if (e.key === 'Escape') {
            document.body.classList.remove('sidebar-open');
            if (document.activeElement && typeof document.activeElement.blur === 'function') {
                document.activeElement.blur();
            }
        }
    });
}
