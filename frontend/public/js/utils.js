export function formatDate(dateString) {
    const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', options);
}

// Manage dark mode
export function toggleDarkMode() {
    
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;

    const icon = darkModeToggle.querySelector('i');
    const isDarkMode = body.classList.contains('dark-mode');

    if (isDarkMode) {
        body.classList.remove('dark-mode');
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
        localStorage.setItem('dark-mode', 'false');
    } else {
        body.classList.add('dark-mode');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
        localStorage.setItem('dark-mode', 'true');
    }
}

export function checkDarkModeOnLoad() {
    const darkMode = localStorage.getItem('dark-mode') === 'true';
    if (darkMode) toggleDarkMode()
}