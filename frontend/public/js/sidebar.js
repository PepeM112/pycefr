document.addEventListener('DOMContentLoaded', () => {
    const burgerMenu = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    burgerMenu.addEventListener('click', () => {
        sidebar.classList.toggle('hidden');
    });
});